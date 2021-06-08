from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    '''Admin View for Account'''

    list_display = ('__str__', 'first_name', 'last_name', 'email')
