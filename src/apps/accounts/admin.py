from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Account, UserProfile


@admin.register(Account)
class AccountAdmin(UserAdmin):
    '''Admin View for Account'''

    list_display = ('__str__', 'first_name', 'last_name', 'email', 'date_joined', 'last_login', 'is_active')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        image = f'<img src="{object.profile_picture.url}" width="30" style="border-radius:50%;">'
        return format_html(image)
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')
