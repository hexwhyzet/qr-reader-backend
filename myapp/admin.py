import enum
import os
import urllib.parse

from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html

from myapp.custom_groups import QRManager, UserManager, SeniorUserManager, CanteenAdminManager
from myapp.excel import fire_extinguishers, guards_stats
from myapp.models import Guard, Round, Visit, Point, Message
from myapp.services.guards import get_manager_guards, get_guard_by_guard_id
from myapp.services.messages import messages_by_user
from myapp.admin_mixins import CustomAdmin
from food.admin import register_food_admin
from food.models import Feedback


class ServicesEnum(enum.StrEnum):
    QR_GUARD = 'myapp'
    CANTEEN = 'food'


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
        guard_id = int(self.cleaned_data['guards'])
        return get_manager_guards(self.request.user) if guard_id == self.ALL_EMPLOYEES_OPTION else [
            get_guard_by_guard_id(guard_id)]


class GroupUserManagementForm(forms.Form):
    add_user = forms.ModelChoiceField(
        queryset=User.objects,
        required=False,
        label="Добавить в сервис",
    )

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        self.fields['add_user'].queryset = User.objects.exclude(groups=self.group)

    def save(self):
        new_group_user = self.cleaned_data['add_user']
        self.group.user_set.add(new_group_user)
        self.group.save()


class MyAdminSite(AdminSite):
    def register(self, model_or_iterable, admin_class=None, **options):
        if admin_class is None:
            admin_class = CustomAdmin
        super().register(model_or_iterable, admin_class, **options)
        
    def app_index(self, request, app_label, extra_context=None):
        extra_context = extra_context or {}
        if app_label == 'food':
            extra_context['unread_feedback_count'] = Feedback.objects.filter(is_read=False).count()
        return super().app_index(request, app_label, extra_context)
    
    def get_absolute_url(self, request, view_name, *args, **kwargs):
        return os.path.join(f'http://{request.get_host()}', 'admin', view_name)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-fire-extinguishers/', fire_extinguishers, name='export_fire_extinguishers'),
            path('export-guards-stats/', self.guards_stats_form, name='guards_stats'),
            path('manage_group_users/<str:group_name>', self.manage_group_users, name='manage_group_users'),
            path('manage_group_users/<str:group_name>/delete/<str:user_id>', self.manage_group_users_delete,
                 name='manage_group_users_delete'),
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

    def manage_group_users(self, request, group_name):
        group = get_object_or_404(Group, name=group_name)
        if request.method == 'POST':
            form = GroupUserManagementForm(request.POST, group=group)
            if form.is_valid():
                form.save()
        else:
            form = GroupUserManagementForm(group=group)

        return render(request, 'manage_group_users.html',
                      {'form': form, 'group': group, 'users_in_group': group.user_set.all()})

    def manage_group_users_delete(self, request, group_name, user_id):
        if request.method == 'POST':
            group = get_object_or_404(Group, name=group_name)
            user = get_object_or_404(User, id=user_id)
            group.user_set.remove(user)
            return redirect(reverse('admin:manage_group_users', kwargs={'group_name': group_name}))

    def get_buttons(self, request, app_name):
        if app_name == ServicesEnum.QR_GUARD.value:
            result = [
                {
                    'label': 'Выгрузить информацию об огнетушителях',
                    'url': self.get_absolute_url(request, 'export-fire-extinguishers/'),
                },
                {
                    'label': 'Выгрузить информацию об обходах',
                    'url': self.get_absolute_url(request, 'export-guards-stats/'),
                }
            ]
            if request.user.is_superuser or request.user.groups.filter(name=QRManager.name).exists():
                result.append({
                    'label': 'Добавить сотрудников в сервис',
                    'url': self.get_absolute_url(request, 'manage_group_users/qr_guard'),
                })
            return result
        
        if app_name == ServicesEnum.CANTEEN:
            if request.user.is_superuser or request.user.groups.filter(name=CanteenAdminManager.name).exists():
                return [{
                    'label': 'Добавить сотрудников в сервис',
                    'url': self.get_absolute_url(request, 'manage_group_users/canteen_employee'),
                }]

        return []

    def each_context(self, request):
        app_name = request.path.split('/')[2] or None
        extra_context = super().each_context(request)
        extra_context['custom_buttons'] = self.get_buttons(request, app_name)
        extra_context['is_index'] = request.path.endswith('/admin/')
        extra_context['message_count'] = len(messages_by_user(request.user))
        extra_context['app_name'] = app_name
        return extra_context


class VisitInline(admin.StackedInline):
    model = Visit
    extra = 0
    can_delete = False
    max_num = 0
    ordering = ('-created_at',)
    readonly_fields = ['point', 'created_at']


class GuardAdmin(CustomAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Senior Managers').exists() or request.user.groups.filter(name='senior_user_manager').exists():
            return qs
        elif request.user.groups.filter(name='Managers').exists() or request.user.groups.filter(name='qr_manager').exists():
            return qs.filter(managers=request.user)
        return []

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if request.user.is_superuser or request.user.groups.filter(name='Senior Managers').exists() or request.user.groups.filter(name='senior_user_manager').exists():
            return True
        if obj and (request.user.groups.filter(name='Managers').exists() or request.user.groups.filter(name='qr_manager').exists()):
            return request.user in obj.managers.all()
        return False

    def has_delete_permission(self, request, obj=None):
        if not super().has_delete_permission(request, obj):
            return False
        if request.user.is_superuser or request.user.groups.filter(name='Senior Managers').exists() or request.user.groups.filter(name='senior_user_manager').exists():
            return True
        if obj and (request.user.groups.filter(name='Managers').exists() or request.user.groups.filter(name='qr_manager').exists()):
            return request.user in obj.managers.all()
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change or not obj.managers:
            obj.managers.add(request.user)

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='Managers').exists() or request.user.groups.filter(name='qr_manager').exists():
            return ['managers']
        return []


class RoundAdmin(CustomAdmin):
    list_filter = [
        "guard",
    ]

    def is_finished(self, obj):
        return not obj.is_active

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Senior Managers').exists() or request.user.groups.filter(name='senior_user_manager').exists():
            return qs
        if request.user.groups.filter(name='Managers').exists() or request.user.groups.filter(name='qr_manager').exists():
            return qs.filter(guard__managers=request.user)
        return []

    inlines = [VisitInline]


class VisitAdmin(CustomAdmin):
    list_filter = [
        "point",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Senior Managers').exists() or request.user.groups.filter(name='senior_user_manager').exists():
            return qs
        if request.user.groups.filter(name='Managers').exists() or request.user.groups.filter(name='qr_manager').exists():
            return qs.filter(round__guard__managers=request.user)
        return []


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


class PointAdmin(CustomAdmin):
    list_display = ['name', 'qr_code_button']
    search_fields = ['name__icontains']

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


class MessageAdmin(CustomAdmin):
    list_display = ['visit', 'text', 'is_seen']
    readonly_fields = ['guard', 'visit']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Senior Managers').exists() or request.user.groups.filter(name='senior_user_manager').exists():
            return qs
        if request.user.groups.filter(name='Managers').exists() or request.user.groups.filter(name='qr_manager').exists():
            return qs.filter(guard__managers=request.user)
        return []


def is_user_manager(user):
    return user.groups.filter(name=UserManager.name).exists() or user.groups.filter(
        name=SeniorUserManager.name).exists()


def is_senior_user_manager(user):
    return user.groups.filter(name=SeniorUserManager.name).exists()


class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'is_staff'),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        if not request.user.is_superuser:
            return ((None, {'fields': ('username', 'first_name', 'last_name', 'is_staff', 'groups')}),)
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and not is_senior_user_manager(request.user):
            return 'is_superuser', 'user_permissions', 'groups'
        return super().get_readonly_fields(request, obj)

    def has_add_permission(self, request):
        return request.user.is_superuser or is_user_manager(request.user)

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser and obj and obj.is_superuser and not is_user_manager(request.user):
            return False
        return super().has_change_permission(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_superuser=False)
        return qs

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or is_user_manager(request.user)


admin.site = MyAdminSite()

admin.site.register(Guard, GuardAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, GroupAdmin)
register_food_admin(admin.site)
