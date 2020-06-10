"""Internet_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from filesender.views import index, RegisterFormView, LoginFormView, user_logout, main_view, search_friends, user_page, change_rights, notification_center, add_to_friend, download, download_file
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('login/', LoginFormView.as_view()),
    path('register/', RegisterFormView.as_view()),
    path('logout/', user_logout),
    path('main/', main_view),
    path('search_user/', search_friends),
    path('user/<int:user_id>/', user_page),
    path('change_rights/', change_rights),
    path('notifications/', notification_center),
    path('add_to_friend/<int:user_id>/', add_to_friend),
    path('download_file/<int:user_id>/', download),
    path('file/<str:file_id>/<str:action>/', download_file),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)