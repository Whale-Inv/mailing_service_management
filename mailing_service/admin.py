from django.contrib import admin

from mailing_service.models import Message, Mailing, MailingAttempt, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'comment')
    search_fields = ('email', 'full_name')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject',)
    search_fields = ('subject',)

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'status', 'message')
    list_filter = ('status',)
    search_fields = ('message__subject',)
    filter_horizontal = ('recipients',)

@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'recipient', 'attempt_time', 'status',)
    list_filter = ('status', 'attempt_time')
    search_fields = ('recipient__email',)
