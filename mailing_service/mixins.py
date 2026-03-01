from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class OwnerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь - владелец объекта"""

    def test_func(self):
        obj = self.get_object()
        # Проверяем, что объект принадлежит текущему пользователю
        return obj.owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для этого действия.')
        return redirect('mailing_service:index')