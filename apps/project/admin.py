from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.project.models import Project, ProjectRole, Comment
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter

# Register your models here.
class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        url = reverse('admin:%s_%s_change' % (
            instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk] )
        if instance.pk:
            return mark_safe(u'<a href="{u}">edit</a>'.format(u=url))
        else:
            return ''

# Inline Forms

class CommentInlineAdmin(EditLinkToInlineObject, admin.TabularInline):
    model = Comment
    extra = 0
    max_num = 10 # Restricts the maximum number of comments per project page to 10 for performance reasons
    classes = ['collapse', ]
    list_display = [ 'user', 'project', 'created_at']
    autocomplete_fields = ['user', 'project']

    show_full_result_count = True # Set to False if page starts loading slow as data increases


class ProjectRoleInlineAdmin(EditLinkToInlineObject, admin.TabularInline):
    model = ProjectRole
    extra = 0
    max_num = 10 # Restricts the maximum number of project roles (users) per project page to 10 for performance reasons
    classes = ['collapse', ]
    list_display = ['role', 'user','project']
    autocomplete_fields = ['user', 'project']

    show_full_result_count = True # Set to False if page starts loading slow as data increases


# Main Forms

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title','created_at', 'updated_at']
    list_display_links = ['title','created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    list_filter = (
        ('users', RelatedDropdownFilter),
    )
    search_fields = ['title', 'description']
    autocomplete_fields = ['users']
    inlines = [ProjectRoleInlineAdmin, CommentInlineAdmin]


@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    list_display = ['role', 'user','project']
    list_display_links = ['role', 'user',]
    ordering = ['role']


    list_filter = (
        'role',
        ('user', RelatedDropdownFilter),
        ('project', RelatedDropdownFilter),
    )
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    autocomplete_fields = ['user', 'project']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'project', 'created_at']
    list_display_links = ['user', 'project']
    ordering = ['-created_at']

    list_filter = (
        ('user', RelatedDropdownFilter),
        ('project', RelatedDropdownFilter),
    )
    search_fields = ['content']
    autocomplete_fields = ['user', 'project']
