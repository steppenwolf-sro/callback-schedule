# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import CallbackRequest, CallEntry


class CallbackRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'created',
        'phone',
        'name',
        'comment',
        'completed',
        'date',
        'immediate',
    )
    list_filter = ('client', 'created', 'completed', 'date', 'immediate')
    search_fields = ('name',)
    readonly_fields = ('phones',)


admin.site.register(CallbackRequest, CallbackRequestAdmin)


class CallEntryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'request',
        'attempt',
        'state',
        'record_url',
        'duration',
        'uuid',
    )
    list_filter = ('created', 'request')


admin.site.register(CallEntry, CallEntryAdmin)
