import urllib.parse

from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import path
from django.utils.html import format_html

from myapp.excel import fire_extinguishers, guards_stats
from myapp.models import Guard, Round, Visit, Point, Message
from myapp.services.guards import get_manager_guards, get_guard_by_guard_id, get_guards
from myapp.services.messages import messages_by_user


class GuardsStatsForm(forms.Form):
    ALL_EMPLOYEES_OPTION = -1

    guards = forms.ChoiceField(
        choices=[],
        label="Выберите сотрудника",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',  # Добавляем Bootstrap-класс
            'placeholder': 'Выберите сотрудника'
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        print(self.request)
        super().__init__(*args, **kwargs)
        guards_choices = [(self.ALL_EMPLOYEES_OPTION, "Все сотрудники")] + [
            (employee.id, employee.name) for employee in get_manager_guards(self.request.user)
        ]
        self.fields['guards'].choices = guards_choices

    def get_guards(self):
        guard_id = self.cleaned_data['guards']
        return get_manager_guards(self.request.user) if guard_id == self.ALL_EMPLOYEES_OPTION else [
            get_guard_by_guard_id(guard_id)]


class MyAdminSite(AdminSite):
    index_template = "admin/my_index.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-fire-extinguishers/', fire_extinguishers, name='export_fire_extinguishers'),
            path('export-guards-stats/', self.guards_stats_form, name='guards_stats'),
        ]
        return custom_urls + urls

    def guards_stats_form(self, request):
        if request.method == 'POST':
            form = GuardsStatsForm(request.POST, request=request)
            if form.is_valid():
                guards = form.get_guards()
                return guards_stats(guards)
        else:
            form = GuardsStatsForm(request=request)

        return render(request, 'guards_stats.html', {'form': form})

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_buttons'] = [{
            'label': 'Выгрузить информацию об огнетушителях',
            'url': 'export-fire-extinguishers/',
        }, {
            'label': 'Выгрузить информацию об обходах',
            'url': 'export-guards-stats/',
        }, ]
        extra_context['message_count'] = len(messages_by_user(request.user))
        return super().index(request, extra_context=extra_context)


class VisitInline(admin.StackedInline):
    model = Visit
    extra = 0
    can_delete = False
    max_num = 0
    ordering = ('-created_at',)
    readonly_fields = ['point', 'created_at']


class GuardAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Managers').exists():
            return qs.filter(managers=request.user)
        return qs

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj and request.user.groups.filter(name='Managers').exists():
            return request.user in obj.managers.all()
        return True

    def has_delete_permission(self, request, obj=None):
        if not super().has_delete_permission(request, obj):
            return False
        if obj and request.user.groups.filter(name='Managers').exists():
            return request.user in obj.managers.all()
        return True

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change or not obj.managers:
            obj.managers.add(request.user)

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='Managers').exists():
            return ['managers']
        return []


class RoundAdmin(admin.ModelAdmin):
    list_filter = [
        "guard",
    ]

    def is_finished(self, obj):
        return not obj.is_active

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Managers').exists():
            return qs.filter(guard__managers=request.user)
        return qs

    inlines = [VisitInline]


class VisitAdmin(admin.ModelAdmin):
    list_filter = [
        "point",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Managers').exists():
            return qs.filter(round__guard__managers=request.user)
        return qs


def show_qr_code(request, object_id):
    return generate_qr_code(request, object_id, False)


def download_qr_code(request, object_id):
    return generate_qr_code(request, object_id, True)


def generate_qr_code(request, object_id, force_download=True):
    obj = get_object_or_404(Point, pk=object_id)
    qr_code_file = obj.generate_qr_code()

    filename = f"{obj.name} QR.png"
    encoded_filename = urllib.parse.quote(filename)

    if force_download:
        response = HttpResponse(qr_code_file, content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
    else:
        response = HttpResponse(qr_code_file, content_type='image/png')
    return response


class PointAdmin(admin.ModelAdmin):
    list_display = ['name', 'qr_code_button']

    def qr_code_button(self, obj):
        return format_html('<a class="button" href="{}">Показать</a>&nbsp;<a class="button" href="{}">Скачать</a>',
                           f'/admin/myapp/point/{obj.pk}/qr_code/show/',
                           f'/admin/myapp/point/{obj.pk}/qr_code/download/')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/qr_code/show/', self.admin_site.admin_view(show_qr_code), name='show-qr-code'),
            path('<int:object_id>/qr_code/download/', self.admin_site.admin_view(download_qr_code),
                 name='download-qr-code'),
        ]
        return custom_urls + urls

    qr_code_button.short_description = 'QR Код'


class MessageAdmin(admin.ModelAdmin):
    list_display = ['visit', 'text', 'is_seen']
    readonly_fields = ['guard', 'visit']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Managers').exists():
            return qs.filter(guard__managers=request.user)
        return qs


admin.site = MyAdminSite()

admin.site.register(Guard, GuardAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(User, UserAdmin)
