from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Subscription


UserAdmin.fieldsets += (
    ('Дополнительные поля', {'fields': ('avatar',)}),
)
UserAdmin.list_display = (
    'first_name', 'last_name', 'email', 'username', 'is_staff')

admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
