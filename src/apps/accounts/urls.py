from django.urls import path

from .views import (activate_email_view, dashboard_view, login_view,
                    logout_view, register_view)

app_name = 'accounts'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('activate/<uidb64>/<token>', activate_email_view, name='activate'),
    path('dashboard/', dashboard_view, name='dashboard')
]
