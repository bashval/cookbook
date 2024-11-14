from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Subscription


UserAdmin.fieldsets += (
    ('Дополнительные поля', {'fields': ('avatar',)}),
)
admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
