from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import Subscription, User


UserAdmin.list_display = (
    'first_name', 'last_name', 'email', 'username', 'is_staff')
UserAdmin.add_fieldsets += (
    ('Дополнительные поля', {'fields': ('first_name', 'last_name', 'email',)}),
)
UserAdmin.fieldsets = (
    (None, {"fields": ("username", "password")}),
    (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
    ('Дополнительные поля', {'fields': ('avatar',)}),
    (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
    (_("Important dates"), {"fields": ("last_login", "date_joined")}),
)

admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
admin.site.unregister(Group)
