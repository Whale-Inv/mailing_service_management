from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from config.settings import CACHE_ENABLE
from .models import MailingAttempt, Recipient
import logging

logger = logging.getLogger(__name__)

class MailingService:
    """ Сервис для отправки рассылок """

    @staticmethod
    def can_send(mailing):
        """ Проверяем можно ли отправлять рассылку """
        now = timezone.now()
        return mailing.start_time <= now <= mailing.end_time

    @staticmethod
    def send_to_recipient(mailing, recipient):
        """ Отправка письма одному получателю """
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            # Создаем запись об успешной попытке
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status='success',
                server_response='Письмо успешно отправлено'
            )
            return True, None

        except Exception as e:
            # Создаем запись о неудачной попытке
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status='failed',
                server_response=str(e)
            )
            logger.error(f"Ошибка отправки письма {recipient.email}: {e}")
            return False, str(e)

    @classmethod
    def start_mailing(cls, mailing):
        """ Запуск рассылки """
        results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'errors':[]
        }

        if not cls.can_send(mailing):
            return {
                'success': False,
                'message': f'Рассылка может быть отправлена только с {mailing.start_time} по {mailing.end_time}'
            }

        recipients = mailing.recipients.all()
        results['total'] = recipients.count()

        # Отправляем каждому
        for recipient in recipients:
            success, error = cls.send_to_recipient(mailing, recipient)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"{recipient.email}: {error}")

        # Обновляем статус рассылки
        if results['success'] > 0:
            mailing.status = 'started'
            mailing.save()

        return {
            'success': True,
            'message': f'Рассылка завершена. Успешно: {results["success"]}, Ошибок: {results["failed"]}',
            'details': results
        }


def get_recipient_from_cache():
    """ получает данные получателей из кэша, если кэш пуст - получает данные из БД """
    if not CACHE_ENABLE:
        return Recipient.objects.all()
    key = 'recipient_list'
    recipients = cache.get(key)
    if recipients is not None:
        return recipients
    recipients = Recipient.objects.all()
    cache.set(key, recipients)
    return recipients

