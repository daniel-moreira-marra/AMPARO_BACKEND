from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.forms import TextInput, Textarea
from django import forms

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Admin compatível com usuário sem username.
    """
    model = User
    ordering = ("email",)
    list_display = ("email", "full_name", "role", "is_staff", "is_active", "is_verified")
    search_fields = ("email", "full_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Dados", {"fields": ("full_name", "phone", "address_line", "city", "state", "zip_code", "role", "is_verified")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Datas", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "phone", "address_line", "city", "state", "zip_code", "role", "password1", "password2", "is_staff", "is_active"),
        }),
    )

    # Como não temos username:
    username = None
