from django.contrib import admin
from dbref.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = None          # Disable all actions
    change_list_template = 'newlook/change_list.html'
    change_form_template = 'newlook/change_form.html'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

