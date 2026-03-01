from django.urls import path

from django.views.decorators.cache import cache_page

from mailing_service.apps import MailingServiceConfig
from .views import RecipientListView, RecipientCreateView, RecipientDetailView, RecipientUpdateView, \
    RecipientDeleteView, MessageListView, MessageCreateView, MessageDetailView, MessageUpdateView, MessageDeleteView, \
    MailingListView, MailingCreateView, MailingDetailView, MailingUpdateView, MailingDeleteView, MailingStartView, \
    IndexView

app_name = MailingServiceConfig.name

urlpatterns = [
    path('recipients/', RecipientListView.as_view(), name='recipient_list'),
    path('recipient/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipient/<int:pk>/', cache_page(60)(RecipientDetailView.as_view()), name='recipient_detail'),
    path("recipient/<int:pk>/update/", RecipientUpdateView.as_view(), name='recipient_update'),
    path("recipient/<int:pk>/delete/", RecipientDeleteView.as_view(), name='recipient_confirm_delete'),

    path('messages/', MessageListView.as_view(), name='message_list'),
    path('message/create/', MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/', cache_page(60)(MessageDetailView.as_view()), name='message_detail'),
    path("message/<int:pk>/update/", MessageUpdateView.as_view(), name='message_update'),
    path("message/<int:pk>/delete/", MessageDeleteView.as_view(), name='message_confirm_delete'),

    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailing/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/', cache_page(60)(MailingDetailView.as_view()), name='mailing_detail'),
    path("mailing/<int:pk>/update/", MailingUpdateView.as_view(), name='mailing_update'),
    path("mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name='mailing_confirm_delete'),
    path('mailing/<int:pk>/start/', MailingStartView.as_view(), name='mailing_start'),

    path('', IndexView.as_view(), name='index'),
]
