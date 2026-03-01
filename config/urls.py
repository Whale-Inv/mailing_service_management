from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('mailing_service.urls', namespace='mailing_service')),
    path('users/', include('users.urls', namespace='users')),
]
