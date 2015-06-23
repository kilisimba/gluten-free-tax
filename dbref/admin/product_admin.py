from django.contrib import admin
from django.forms import widgets
from django import forms
from dbref.models import Product, Brand

class ProductForm(forms.ModelForm):
    category_note =  forms.CharField(   widget=widgets.Textarea(attrs={'style':"width:400px"}), 
                                        max_length=800 )
    validation_date =  forms.CharField( label='Validation Date', \
                                        widget=widgets.TextInput(attrs={'size':"120"}), \
                                        max_length=100 )
    description = forms.CharField(   label='Description', \
                                     widget=widgets.TextInput(attrs={'size':"120"}), \
                                     max_length=400 )

    """
    Set values
    """
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.initial['category_note'] = self.instance.category.note if self.instance.category is not None else ''
        self.initial['validation_date'] = self.instance.company.validation_date if self.instance.company is not None else ''
        self.fields['company'].widget = widgets.SelectMultiple(attrs={ 'readonly':'true', 'style':"width:400px", 'size':"8" })
        self.fields['company'].queryset = self.instance.company.brand_set.all() \
                                            if self.instance.company is not None else Brand.objects.none()
        self.fields['company'].empty_label = None
        self.initial['company'] = None      # This is important. Set to None for no options selected
        self.fields['description'].widget.attrs['readonly'] = 'True'
        self.fields['unit'].widget.attrs['readonly'] = 'True'
        self.fields['price'].widget.attrs['readonly'] = 'True'
        self.fields['gluten_free'].widget.attrs['onclick'] = "return false"     # This will make it readonly
        self.fields['category_note'].widget.attrs['readonly'] = 'True'

    class Meta:
        model = Product
        fields = ('description', 'unit', 'price', 'company', 'category_note', 'gluten_free')


from django.contrib.admin.views.main import ChangeList
class ProductChangeList(ChangeList):
    
    def __init__(self, request, model, list_display, list_display_links,
            list_filter, date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, model_admin):

            super(ProductChangeList, self).__init__(request, model, list_display, list_display_links,
            list_filter, date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, model_admin)
            """
            Set our title
            """
            self.title = 'Select a product for more details'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('description', 'unit', 'price', 'gluten_free', 'validation_date', 'company')
    form = ProductForm
    actions = None
    change_list_template = 'newlook/change_list.html'
    change_form_template = 'newlook/change_form.html'
    fieldsets = (
        (None, {
            'fields': ('description', 'validation_date', ('unit', 'price', 'gluten_free'), 'company', 'category_note', )
        }),
    )

    def validation_date(self, obj):
        #import rpdb2
        #rpdb2.start_embedded_debugger("qwe123")
        return obj.company.validation_date if hasattr(obj.company, 'validation_date') else ''

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id, extra_context=None):
            extra_context = extra_context or {}
            extra_context['readonly'] = True
            return super(ProductAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def get_changelist(self, request, **kwargs):
        return ProductChangeList

    class Media:
        css = {
                "all": ("dbref/css/product.css",)
              }

