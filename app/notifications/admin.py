from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'sender',
        'notification_type',
        'event',
        'target_id',
        'is_read',
        'created_at',
    )
    list_filter = ('notification_type', 'event', 'is_read', 'created_at')
    search_fields = ('user__nickname', 'sender__nickname', 'target_id')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    ordering = ('-created_at',)