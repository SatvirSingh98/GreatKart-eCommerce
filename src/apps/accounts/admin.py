from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account


@admin.register(Account)
class AccountAdmin(UserAdmin):
    '''Admin View for Account'''

    list_display = ('__str__', 'first_name', 'last_name', 'email', 'date_joined', 'last_login', 'is_active')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
