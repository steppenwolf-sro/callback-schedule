# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import CallbackManager, CallbackManagerPhone, CallbackManagerSchedule


class CallbackManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    list_filter = ('user',)
admin.site.register(CallbackManager, CallbackManagerAdmin)


class CallbackManagerPhoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'manager', 'phone_type', 'number', 'priority')
    list_filter = ('manager',)
admin.site.register(CallbackManagerPhone, CallbackManagerPhoneAdmin)


class CallbackManagerScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'manager',
        'weekday',
        'available_from',
        'available_till',
    )
    list_filter = ('manager',)
admin.site.register(CallbackManagerSchedule, CallbackManagerScheduleAdmin)
