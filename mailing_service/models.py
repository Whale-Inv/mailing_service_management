from django.db import models
from django.utils import timezone

from users.models import User


class Recipient(models.Model):
    email = models.EmailField(unique=True, max_length=100, verbose_name='Почта', help_text='Введите адрес эл. почты')
    full_name = models.CharField(max_length=255, verbose_name='Ф.И.О.', help_text='Введите ФИО получателя')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий', help_text='Введите комментарий')

    owner = models.ForeignKey(User, verbose_name="Создатель", help_text="Укажите создателя получателя", blank=True,
                              null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма', help_text='Введите тему письма')
    body = models.TextField()
    owner = models.ForeignKey(User, verbose_name="Создатель", help_text="Укажите создателя сообщения", blank=True,
                              null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('finished', 'Завершена'),
    ]

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',  # Message -> рассылки с этим сообщением
        verbose_name='Сообщение'
    )
    recipients = models.ManyToManyField(
        Recipient,
        related_name='mailings',  # Recipient -> рассылки для этого получателя
        verbose_name='Получатели'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')

    owner = models.ForeignKey(User, verbose_name="Создатель", help_text="Укажите создателя рассылки", blank=True, null=True, on_delete=models.SET_NULL)

    is_published = models.BooleanField(default=False)

    def update_status(self):
        now = timezone.now()
        if now < self.start_time:
            new_status = 'created'
        elif self.start_time <= now <= self.end_time:
            new_status = 'started'
        else:
            new_status = 'finished'
        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])
        return self.status

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка #{self.pk} ({self.get_status_display()})"


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('fail', 'Не успешно'),
    ]
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Время попытки')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='Статус')
    server_response = models.TextField(blank=True, null=True, verbose_name='Ответ сервера/Ошибка')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts', verbose_name='Рассылка')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='attempts', verbose_name='Получатель')

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ['-attempt_time']

    def __str__(self):
        return f"Попытка: {self.mailing} -> {self.recipient.email} ({self.get_status_display()})"
