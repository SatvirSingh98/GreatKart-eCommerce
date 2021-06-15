from django.urls import path

from .views import (activate_email_view, change_email_view,
                    change_password_view, dashboard_view, edit_profile_view,
                    forgot_password_view, login_view, logout_view,
                    my_orders_view, order_detail_view, register_view, remove_profile_picture_view,
                    reset_password_validate_view, reset_password_view)

app_name = 'accounts'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', activate_email_view, name='activate'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('forgot-password/', forgot_password_view, name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', reset_password_validate_view, name='verify-reset-password'),
    path('reset-password/', reset_password_view, name='reset-password'),
    path('my_orders/', my_orders_view, name='my-orders'),
    path('edit_profile/', edit_profile_view, name='edit-profile'),
    path('remove_profile_picture/', remove_profile_picture_view, name='remove-profile-picture'),
    path('change_password/', change_password_view, name='change-password'),
    path('change_email/', change_email_view, name='change-email'),
    path('order_detail/<order_no>', order_detail_view, name='order-detail')
]
