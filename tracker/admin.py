from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from tracker.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'first_name', 'last_name']
    fieldsets = (
        (None, {'fields': ('email' ,'username' ,'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser',)
        })
    )

    search_fields = ('email', 'username','first_name', 'last_name')

