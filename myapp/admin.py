from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils.html import format_html

from myapp.models import Guard, Round, Visit, Point


# class RoundInline(admin.StackedInline):
#     model = Round
#     extra = 0
#     can_delete = False
#     max_num = 0
#     ordering = ('-created_at',)
#     readonly_fields = ['guard', 'created_at', 'is_active']


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
        if request.user.groups.filter(name='Manager').exists():
            manager = request.user.manager
            return qs.filter(manager=manager)
        return qs

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj and request.user.groups.filter(name='Manager').exists():
            return obj.manager.user == request.user
        return True

    def has_delete_permission(self, request, obj=None):
        if not super().has_delete_permission(request, obj):
            return False
        if obj and request.user.groups.filter(name='Manager').exists():
            return obj.manager.user == request.user
        return True


class RoundAdmin(admin.ModelAdmin):
    list_filter = [
        "guard",
    ]

    inlines = [VisitInline]


class VisitAdmin(admin.ModelAdmin):
    list_filter = [
        "point",
    ]


def generate_qr_code(request, object_id):
    obj = get_object_or_404(Point, pk=object_id)
    qr_code_file = obj.generate_qr_code()
    response = HttpResponse(qr_code_file, content_type='image/png')
    return response


class PointAdmin(admin.ModelAdmin):
    list_display = ['name', 'qr_code_button']

    def qr_code_button(self, obj):
        return format_html('<a class="button" href="{}">Показать</a>',
                           f'/admin/myapp/point/{obj.pk}/qr_code/')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/qr_code/', self.admin_site.admin_view(generate_qr_code), name='generate-qr-code'),
        ]
        return custom_urls + urls

    qr_code_button.short_description = 'QR Код'


admin.site.register(Guard, GuardAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Point, PointAdmin)
