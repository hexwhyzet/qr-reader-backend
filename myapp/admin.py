import urllib.parse

from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils.html import format_html

from myapp.models import Guard, Round, Visit, Point


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
            return qs.filter(manager=request.user)
        return qs

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj and request.user.groups.filter(name='Managers').exists():
            return obj.manager == request.user
        return True

    def has_delete_permission(self, request, obj=None):
        if not super().has_delete_permission(request, obj):
            return False
        if obj and request.user.groups.filter(name='Managers').exists():
            return obj.manager == request.user
        return True

    def save_model(self, request, obj, form, change):
        if not change or not obj.manager:
            obj.manager = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='Managers').exists():
            return ['manager']
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
            return qs.filter(guard__manager=request.user)
        return qs

    inlines = [VisitInline]


class VisitAdmin(admin.ModelAdmin):
    list_filter = [
        "point",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Managers').exists():
            return qs.filter(round__guard__manager=request.user)
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


admin.site.register(Guard, GuardAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Point, PointAdmin)

admin.site.index_title = None
