import secrets

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, ListView

from users.forms import UserRegisterForm
from users.models import User

from config.settings import EMAIL_HOST_USER


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()

        host = self.request.get_host()
        print(host)
        url = reverse('users:email-confirm', kwargs={'token': token})
        full_url = f"http://{host}{url}"
        # url = f"http://{host}/users/email_confirm/{token}/"

        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, перейди по ссылке для подтверждения почты {full_url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Список всех пользователей сервиса (только для менеджеров и админов)"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def test_func(self):
        """Проверка прав доступа"""
        user = self.request.user
        # Доступ только для менеджеров и админов
        return user.groups.filter(name='Модератор').exists() or user.is_superuser

    def handle_no_permission(self):
        """Обработка отсутствия прав"""
        messages.error(self.request, 'У вас нет прав для просмотра списка пользователей.')
        return redirect('mailing_service:index')

    def get_queryset(self):
        """Получение списка пользователей с аннотациями"""
        return User.objects.filter(
            is_superuser=False  # Исключаем суперпользователей из списка
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем дополнительную статистику
        for user in context['users']:
            user.is_moderator = user.groups.filter(name='Модератор').exists()

        context['total_users'] = User.objects.filter(is_superuser=False).count()
        context['active_users'] = User.objects.filter(
            is_superuser=False,
            is_active=True
        ).count()

        return context

class UserBlockView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Блокировка пользователя"""

    def test_func(self):
        """Проверка прав: только модераторы и админы"""
        user = self.request.user
        return user.groups.filter(name='Модератор').exists() or user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для блокировки пользователей.')
        return redirect('users:user_list')

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        # Проверка, что пользователь не блокирует сам себя
        if user == request.user:
            messages.error(request, 'Вы не можете заблокировать самого себя.')
            return redirect('users:user_list')

        # Проверка, что пользователь не админ
        if user.is_superuser:
            messages.error(request, 'Нельзя заблокировать администратора.')
            return redirect('users:user_list')

        # Блокируем пользователя
        user.is_active = False
        user.is_blocked = True
        user.save()

        messages.success(request, f'Пользователь {user.email} успешно заблокирован.')
        return redirect('users:user_list')

    def get(self, request, pk):
        """Поддержка GET запросов (для ссылок)"""
        return self.post(request, pk)

class UserUnblockView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Разблокировка пользователя"""

    def test_func(self):
        """Проверка прав: только модераторы и админы"""
        user = self.request.user
        return user.groups.filter(name='Модератор').exists() or user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для разблокировки пользователей.')
        return redirect('users:user_list')

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        # Разблокируем пользователя
        user.is_active = True
        user.is_blocked = False
        user.save()

        messages.success(request, f'Пользователь {user.email} успешно разблокирован.')
        return redirect('users:user_list')

    def get(self, request, pk):
        """Поддержка GET запросов (для ссылок)"""
        return self.post(request, pk)