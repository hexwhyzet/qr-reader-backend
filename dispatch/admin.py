import calendar
from datetime import date, timedelta

from django import forms
from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.urls import path
from django.utils.html import format_html

from dispatch.models import DutyPoint, DutyRole, Duty, IncidentMessage, TextMessage, VideoMessage, PhotoMessage, \
    AudioMessage, Incident
from dispatch.services.duties import get_duties_by_date, get_duties_assigned, get_or_create_duty, delete_duty
from dispatch.utils import colors_palette, decl, today
from myapp.admin_mixins import CustomAdmin
from myapp.services.users import get_all_users


class DispatchAdmin(AdminSite):
    site_header = "Кастомная админка"
    site_title = "Панель управления"
    index_title = "Добро пожаловать в админку"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.index_page, name="index"),
            path("duty-schedule/", self.schedule_page, name="schedule"),
        ]
        return custom_urls + urls

    def index_page(self, request):
        return render(request, "admin/dispatch/index.html")

    def schedule_page(self, request):
        return render(request, "admin/dispatch/schedule.html")


def get_calendar_data(year, month, role: DutyRole):
    cal = calendar.Calendar(firstweekday=0)  # Неделя начинается с понедельника
    month_days = cal.monthdayscalendar(year, month)

    user_colors = {}
    color_index = 0

    def get_color(user_id):
        nonlocal color_index
        if user_id not in user_colors:
            user_colors[user_id] = colors_palette[color_index % len(colors_palette)]
            color_index += 1
        return user_colors[user_id]

    calendar_weeks = []
    for week in month_days:
        formatted_week = []
        for day in week:
            if day != 0:
                day_date = date(year, month, day)
                duties = get_duties_by_date(day_date, role)

                colored_duties = [
                    {"user": duty.user, "color": get_color(duty.user.id)}
                    for duty in duties
                ]

                formatted_week.append((day_date, colored_duties))
            else:
                formatted_week.append((None, None))
        calendar_weeks.append(formatted_week)

    return calendar_weeks


class DutyForm(forms.Form):
    user = forms.ModelChoiceField(queryset=get_all_users(), label="Сотрудник")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Дата начала")
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}),
                               label="Дата окончания (Опционально)")
    duty_step = forms.IntegerField(required=False, min_value=1, label="Шаг дежурства (дней) (Опционально)")
    rest_step = forms.IntegerField(required=False, min_value=1, label="Шаг отдыха (дней) (Опционально)")


class ClearDutyForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Дата начала")
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}),
                               label="Дата окончания")


class DutyRoleAdmin(CustomAdmin):
    list_display = ['name', 'next_duty_stats', 'duty_schedule']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/schedule/', self.admin_site.admin_view(self.schedule), name='schedule-duty'),
        ]
        return custom_urls + urls

    def schedule(self, request, object_id):
        duty_role = DutyRole.objects.get(pk=object_id)

        duty_form = DutyForm()
        clear_duty_form = ClearDutyForm()

        if request.method == "POST" and request.POST.get("form_type") == "add_duty_form":
            duty_form = DutyForm(request.POST)
            if duty_form.is_valid():
                user = duty_form.cleaned_data["user"]
                start_date = duty_form.cleaned_data["start_date"]
                end_date = duty_form.cleaned_data["end_date"]
                if end_date is None:
                    end_date = start_date
                duty_step = duty_form.cleaned_data.get("duty_step") or 1
                rest_step = duty_form.cleaned_data.get("rest_step") or 0

                current_date = start_date
                while current_date <= end_date:
                    for _ in range(duty_step):
                        if current_date > end_date:
                            break
                        duty, created = get_or_create_duty(duty_date=current_date, role=duty_role, defaults={"user": user})
                        if not created:
                            duty.user = user
                        duty.save()
                        current_date += timedelta(days=1)
                    current_date += timedelta(days=rest_step)
        elif request.method == "POST" and request.POST.get("form_type") == "clear_duty_form":
            clear_duty_form = ClearDutyForm(request.POST)
            if clear_duty_form.is_valid():
                start_date = clear_duty_form.cleaned_data["start_date"]
                end_date = clear_duty_form.cleaned_data["end_date"]
                if end_date is None:
                    end_date = start_date
                current_date = start_date
                while current_date <= end_date:
                    delete_duty(current_date, duty_role)
                    current_date += timedelta(days=1)

        today_date = today()
        year = int(request.GET.get('year', today_date.year))
        month = int(request.GET.get('month', today_date.month))

        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        context = {
            'current_year': year,
            'current_month': month,
            'current_month_name': month,
            'prev_year': prev_year,
            'prev_month': prev_month,
            'next_year': next_year,
            'next_month': next_month,
            'calendar_weeks': get_calendar_data(year, month, duty_role),
            'add_duty_form': duty_form,
            'clear_duty_form': clear_duty_form,
            'duty_role': duty_role,
        }

        return render(request, 'admin/dispatch/schedule.html', context)

    def duty_schedule(self, obj):
        return format_html('<a class="button" href="{}">Назначить график дежурств</a>',
                           f'/admin/dispatch/dutyrole/{obj.id}/schedule/')

    duty_schedule.short_description = 'Расписание дежурства'

    def next_duty_stats(self, obj):
        dt = today()
        num = get_duties_assigned(dt, obj)
        name = decl(num, ['день', 'дня', 'дней'])
        if num <= 7:
            color = '#dc3545'
            font_weight = 'bold'
        else:
            color = '#000000'
            font_weight = 'normal'
        return format_html(f'<a style="color: {color}; font-weight: {font_weight}">{num} {name}</a>')

    next_duty_stats.short_description = 'Кол-во распланированных дней'


class DutyAdmin(CustomAdmin):
    exclude = ('notification_need_to_open',)


class IncidentAdmin(CustomAdmin):
    list_display = ('name', 'author', 'created_at',)
    readonly_fields = ('created_at',)


dispatch_admin_site = DispatchAdmin()


def register_dispatch_admin(site):
    site.register(DutyPoint)
    site.register(DutyRole, DutyRoleAdmin)
    site.register(Duty, DutyAdmin)
    site.register(Incident, IncidentAdmin)
    site.register(IncidentMessage)
    site.register(TextMessage)
    site.register(VideoMessage)
    site.register(PhotoMessage)
    site.register(AudioMessage)
