from django.contrib import admin
from apps.user.models import User
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin as BaseBaseUserAdmin

# Register your models here.

@admin.register(User)
class UserAdmin(BaseBaseUserAdmin):
    list_display = ['profile_photo','email', 'username', 'is_active', 'email_verified', 'is_admin','is_superuser', 'last_login', 'date_joined']
    list_display_links = ['profile_photo','email', 'username']
    readonly_fields = ['last_login','date_joined']
    ordering = ['-date_joined']
    filter_horizontal = ()
    list_filter = (
        'email_verified',
        'is_active',
        'is_admin',
        'is_staff',
        'is_superuser',
    )
    fieldsets = (
        ('Personal info', {'fields': (
            'username',
            'first_name',
            'last_name',
            'contact_number',
            'email',
            'password',          
            'photo', 
            'bio', 
        )}),        

        ('Permissions', {'fields': (
            'is_active',
            'is_admin',
            'is_staff',
            'is_superuser',
            'email_verified',
            'groups', 
            'user_permissions',

            )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'password1',
                'password2'
                )
            }
        ),
    )
    show_full_result_count = True # Set to false to speed up page load

# Change the admin site headers
admin.site.site_header = 'PMA'
admin.site.site_title = 'PMA Admin'
admin.site.index_title = 'Welcome to Your Portal'