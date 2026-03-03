from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView

from mailing_service.forms import MailingForm
from mailing_service.models import Recipient, Message, Mailing
from django import forms
from django.contrib import messages

from mailing_service.services import MailingService
from .services import get_recipient_from_cache


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailing_service/recipient_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все поля модели, кроме служебных
        context['model_fields'] = [
            field for field in self.model._meta.fields
            if field.name not in ['id']  # исключаем id
        ]
        context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context

    def get_queryset(self):
        user = self.request.user
        # Модератор видит всех, обычный пользователь - только своих
        if user.groups.filter(name='Модератор').exists() or user.is_superuser:
            return Recipient.objects.all()
        return get_recipient_from_cache().filter(owner=user)

class RecipientCreateView(CreateView, LoginRequiredMixin):
    model = Recipient
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailing_service/recipient_form.html'
    success_url = reverse_lazy('mailing_service:recipient_list')

    def form_valid(self, form):
        recipient = form.save()
        user = self.request.user
        recipient.owner = user
        recipient.save()
        return super().form_valid(form)


class RecipientUpdateView(UpdateView):
    model = Recipient
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailing_service/recipient_form.html'
    success_url = reverse_lazy('mailing_service:recipient_list')


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = 'mailing_service/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailing_service:recipient_list')

class RecipientDetailView(DetailView):
    model = Recipient
    template_name = 'mailing_service/recipient_detail.html'
    context_object_name = 'recipient'


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing_service/message_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все поля модели, кроме служебных
        context['model_fields'] = [
            field for field in self.model._meta.fields
            if field.name not in ['id']  # исключаем id
        ]
        context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context

    def get_queryset(self):
        user = self.request.user
        # Модератор видит всех, обычный пользователь - только своих
        if user.groups.filter(name='Модератор').exists() or user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)

class MessageCreateView(CreateView, LoginRequiredMixin):
    model = Message
    fields = ['subject', 'body']
    template_name = 'mailing_service/message_form.html'
    success_url = reverse_lazy('mailing_service:message_list')

    def form_valid(self, form):
        message = form.save()
        user = self.request.user
        message.owner = user
        message.save()
        return super().form_valid(form)

class MessageUpdateView(UpdateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'mailing_service/message_form.html'
    success_url = reverse_lazy('mailing_service:message_list')

class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing_service/message_confirm_delete.html'
    success_url = reverse_lazy('mailing_service:message_list')

class MessageDetailView(DetailView):
    model = Message
    template_name = 'mailing_service/message_detail.html'


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    context_object_name = 'mailings'
    template_name = 'mailing_service/mailing_list.html'

    def get_queryset(self):
        # Дополнительная оптимизация запросов
        return Mailing.objects.select_related('message').prefetch_related('recipients').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все поля модели, кроме служебных
        context['model_fields'] = [
            field for field in self.model._meta.fields
            if field.name not in ['id']  # исключаем id
        ]
        context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context

    def get_queryset(self):
        user = self.request.user
        # Модератор видит всех, обычный пользователь - только своих
        if user.groups.filter(name='Модератор').exists() or user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing_service/mailing_form.html'
    success_url = reverse_lazy('mailing_service:mailing_list')

    def form_valid(self, form):
        mailing = form.save()
        user = self.request.user
        mailing.owner = user
        mailing.save()
        return super().form_valid(form)

    def form_valid(self, form):
        # Дополнительная обработка перед сохранением
        print("Форма валидна!")  # Для отладки
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Форма невалидна:", form.errors)  # Для отладки
        return super().form_invalid(form)

class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing_service/mailing_form.html'
    success_url = reverse_lazy('mailing_service:mailing_list')

    def get_form_class(self):
        # Для обновления добавляем поле status
        if self.request.method == 'POST':
            return MailingForm
        return MailingForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Для формы редактирования добавляем поле status
        if self.object.pk:
            form.fields['status'] = forms.ChoiceField(
                choices=Mailing.STATUS_CHOICES,
                initial=self.object.status,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        return form

class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailing_service/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_service:mailing_list')

class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing_service/mailing_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object

        # Получаем статистику
        attempts = mailing.attempts.all()
        total_attempts = attempts.count()
        success_count = attempts.filter(status='success').count()
        failed_count = attempts.filter(status='failed').count()

        # Рассчитываем процент успеха
        if total_attempts > 0:
            success_rate = round(success_count * 100 / total_attempts)
        else:
            success_rate = 0

        # Добавляем в контекст
        context['total_attempts'] = total_attempts
        context['success_count'] = success_count
        context['failed_count'] = failed_count
        context['success_rate'] = success_rate

        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # ← пересчёт и сохранение статуса
        return obj


class MailingStartView(DetailView):
    """
        View для запуска рассылки.
        GET - показывает страницу подтверждения
        POST - запускает рассылку
    """
    model = Mailing
    template_name = 'mailing_service/mailing_start_confirm.html'
    context_object_name = 'mailing'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        mailing = self.object

        now = timezone.now()

        # Запускаем рассылку
        result = MailingService.start_mailing(mailing)

        # Добавляем сообщение пользователю
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])

        # Перенаправляем на страницу деталей
        return redirect('mailing_service:mailing_detail', pk=mailing.pk)


class IndexView(TemplateView):
    """Главная страница со статистикой рассылок"""
    template_name = 'mailing_service/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Текущее время
        now = timezone.now()

        # 1. Общее количество всех созданных рассылок
        total_mailings = Mailing.objects.count()

        # 2. Количество активных рассылок (статус 'started' И текущее время между start_time и end_time)
        active_mailings = Mailing.objects.filter(
            status='started',
            start_time__lte=now,
            end_time__gte=now
        ).count()

        # 3. Количество уникальных получателей
        total_recipients = Recipient.objects.count()

        # Рассылки по статусам
        mailings_by_status = {
            'created': Mailing.objects.filter(status='created').count(),
            'started': Mailing.objects.filter(status='started').count(),
            'finished': Mailing.objects.filter(status='finished').count(),
        }

        # Завершенные рассылки (end_time прошло)
        finished_mailings = Mailing.objects.filter(
            status='finished'
        ).count()

        # Рассылки, которые еще не начались
        scheduled_mailings = Mailing.objects.filter(
            status='created',
            start_time__gt=now
        ).count()

        # Последние 5 рассылок
        recent_mailings = Mailing.objects.select_related('message').prefetch_related('recipients').order_by(
            '-start_time')[:5]

        context.update({
            'total_mailings': total_mailings,
            'active_mailings': active_mailings,
            'total_recipients': total_recipients,
            'mailings_by_status': mailings_by_status,
            'finished_mailings': finished_mailings,
            'scheduled_mailings': scheduled_mailings,
            'recent_mailings': recent_mailings,
            'now': now,
        })

        return context
