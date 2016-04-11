from django.contrib import admin
from django import forms
import urllib
from django.forms import widgets
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from dbref.models import Association, Brand
from newlook.admin import NewlookModelAdmin

class BrandListFilter(admin.ListFilter):
    title = ('Brand')
    parameter_brand = 'brand'
    parameter_search = 'search'
    parameter_description = 'description'
    template = 'dbref/association_brand_filter.html'

    def __init__(self, request, params, model, model_admin):
        super(BrandListFilter, self).__init__(
            request, params, model, model_admin)
        for p in self.expected_parameters():
            if p in params:
                value = params.pop(p)
                self.used_parameters[p] = value

    def expected_parameters(self):
        return [ self.parameter_brand, self.parameter_search, self.parameter_description ]
        
    def queryset(self, request, qs):
        if self.brand() == "" and self.description == "":
            return qs
        if self.brand() == "":
            params = self.description().split()
            return qs.filter(gluten_free__description__iregex="("+'|'.join(params)+")").distinct()
        if self.description() == "":
            return qs.filter(gluten_free__company__brand=self.brand()).distinct()
        params = self.description().split()
        return qs.filter(gluten_free__company__brand=self.brand(), gluten_free__description__iregex="("+'|'.join(params)+")").distinct()

    def has_output(self):
        return True

    def choices(self, cl):
        return {}

    def search(self):
        return self.used_parameters[self.parameter_search] \
                    if self.used_parameters.get(self.parameter_search, None) else ""

    def description(self):
        return self.used_parameters[self.parameter_description] \
                    if self.used_parameters.get(self.parameter_description, None) else ""

    def brand(self):
        return self.used_parameters[self.parameter_brand] \
                    if self.used_parameters.get(self.parameter_brand, None) else ""

    def brand_list(self, cl):
        #for brand in Brand.objects.all():
        params = self.description().split()
        for brand in Brand.objects.filter(company__product__description__iregex="("+'|'.join(params)+")").distinct():
            yield {
                'display': brand.name,
                'value' : brand.pk,
                'selected' : self.used_parameters[self.parameter_brand] == str(brand.pk) \
                                if self.parameter_brand in self.used_parameters else False,
            } 


class AssociationForm(forms.ModelForm):
    gf_description = forms.CharField(   label='Description', \
                                        widget=widgets.TextInput(attrs={'size':"120"}), \
                                        max_length=400 )
    gf_unit = forms.DecimalField( label='Unit',
                                  widget=widgets.TextInput(attrs={'size':"8"}) )
    gf_price = forms.DecimalField( label='Price',
                                   widget=widgets.TextInput(attrs={'size':"8"}) )
    gf_company = forms.ModelChoiceField( label='Company',
                                         queryset=None,
                                         widget=widgets.SelectMultiple(attrs={ 'style':"width:400px", 'size':"8" }))
    gf_note =  forms.CharField( label='Note',
                                      widget=widgets.Textarea(attrs={'style':"width:600px;height:80px"}), 
                                      max_length=800 )
    gf_category =  forms.CharField( label='Category',
                                      widget=widgets.Textarea(attrs={'style':"width:600px;height:80px"}), 
                                      max_length=800 )

    eq_description = forms.CharField(   label='Description', \
                                        widget=widgets.TextInput(attrs={'size':"120"}), \
                                        max_length=400 )
    eq_unit = forms.DecimalField( label='Unit',
                                  widget=widgets.TextInput(attrs={'size':"8"}) )
    eq_price = forms.DecimalField( label='Price',
                                   widget=widgets.TextInput(attrs={'size':"8"}) )


    """
    Set values
    """
    def __init__(self, *args, **kwargs):
        super(AssociationForm, self).__init__(*args, **kwargs)
        self.initial['gf_description'] = self.instance.gluten_free.description
        self.initial['gf_unit'] = self.instance.gluten_free.unit
        self.initial['gf_price'] = self.instance.gluten_free.price
        self.fields['gf_company'].queryset = self.instance.gluten_free.company.brand_set.all() \
                                            if self.instance.gluten_free.company is not None else Brand.objects.none()
        self.fields['gf_company'].empty_label = None
        self.initial['gf_note'] = self.instance.gluten_free.note \
                                            if self.instance.gluten_free.note is not None else ''
        self.initial['gf_category'] = self.instance.gluten_free.category \
                                            if self.instance.gluten_free.category is not None else ''

        self.initial['eq_description'] = self.instance.equivalent.description \
                                            if self.instance.equivalent is not None else 'No equivalent available'
        self.initial['eq_unit'] = self.instance.equivalent.unit \
                                            if self.instance.equivalent is not None else ''
        self.initial['eq_price'] = self.instance.equivalent.price \
                                            if self.instance.equivalent is not None else ''

    class Meta:
        model = Association
        fields = ('gf_description', 'gf_unit', 'gf_price', 'gf_company', 'gf_note', 'gf_category',  \
                  'eq_description', 'eq_unit', 'eq_price' )

from django.contrib.admin.views.main import ChangeList
class AssociationChangeList(ChangeList):
    IGNORED_PARAMS = ( 'achat', )

    def __init__(self, request, model, list_display, list_display_links,
        list_filter, date_hierarchy, search_fields, list_select_related,
        list_per_page, list_max_show_all, list_editable, model_admin):

        super(AssociationChangeList, self).__init__(request, model, list_display, list_display_links,
        list_filter, date_hierarchy, search_fields, list_select_related,
        list_per_page, list_max_show_all, list_editable, model_admin)
        """
        Set our title
        """
        self.title = 'Select a gluten-free product for more details'

    def get_filters(self, request):
        """
        This will set 'has_filters' to False.
        This is necesary to remove the empty filter column on the right side of the window
        """
        (filter_specs, has_filters, lookup_params, use_distinct) = \
            super(AssociationChangeList, self).get_filters(request)
        return filter_specs, False, lookup_params, use_distinct

    def get_filters_params(self, params=None):
        lookup_params = super(AssociationChangeList, self).get_filters_params(params=params)
        # Remove all the parameters that are globally and systematically
        for ignored in self.IGNORED_PARAMS:
            if ignored in lookup_params:
                del lookup_params[ignored]
        return lookup_params

@admin.register(Association)
class AssociationAdmin(NewlookModelAdmin):
    list_per_page = 100
    form = AssociationForm
    change_list_template = 'dbref/association_change_list.html'
    list_display = ('gluten_free_product', 'gluten_free_brand', 'validation_date', \
                    'gluten_free_unit', 'gluten_free_price', \
                    'equivalent_description', 'equivalent_unit', 'equivalent_price', )
    ordering = ( 'gluten_free__description', )
    fieldsets = (
        (None, {
            'fields': ( 'gf_note', 'gf_category', )
        }),
        ('Gluten Free Product', {
            'fields': ( 'gf_description', ('gf_unit', 'gf_price') )
        }),
        ('Similar Non-Gluten Free Product', {
            'fields' : ('eq_description', ('eq_unit', 'eq_price') )
        }),
    )
    list_filter = ( BrandListFilter, )
    #actions = [ 'update_all', 'update_gf' ]
    actions = [ 'update_all', ]

    # Remove delete_selected
    def get_actions(self, request):
        actions = super(AssociationAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        if 'achat' not in request.GET:
            del actions['update_all']
            #del actions['update_gf']
        return actions

    def update_all(self, request, queryset):
        if (queryset.count() > 1):
            self.message_user(request, "Please select only one product", messages.ERROR)
            return

        if 'achat' in request.GET:
            recordid = request.GET.get('achat')
            post_url = reverse('admin:achat_achat_change', args=[recordid])
            post_url += '?' + urllib.parse.urlencode({'association': queryset[0].pk})
            return HttpResponseRedirect(post_url)
    update_all.short_description = "Select Product"

    def update_gf(self, request, queryset):
        if (queryset.count() > 1):
            self.message_user(request, "Please select only one association", messages.WARNING)
            return

        if 'achat' in request.GET:
            recordid = request.GET.get('achat')
            post_url = reverse('admin:achat_achat_change', args=[recordid])
            post_url += '?' + urllib.parse.urlencode({'product': queryset[0].pk})
            return HttpResponseRedirect(post_url)
    update_gf.short_description = "Update GF Only"

    def validation_date(self, obj):
        return obj.gluten_free.company.validation_date if hasattr(obj.gluten_free.company, 'validation_date') else ''

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def equivalent_description(self, obj):
        if obj.equivalent is None:
            return None
        else:
            return obj.equivalent.description
    equivalent_description.short_description = "Description"

    def equivalent_unit(self,obj):
        if obj.equivalent is None:
            return None
        else:
            return obj.equivalent.unit
    equivalent_unit.short_description = "Unit"

    def equivalent_price(self,obj):
        if obj.equivalent is None:
            return None
        else:
            return obj.equivalent.price
    equivalent_price.short_description = "Price"
                    
    def gluten_free_product(self, obj):
        return obj.gluten_free.description
    gluten_free_product.short_description = "Product"

    def gluten_free_brand(self, obj):
        return obj.gluten_free.company.brands()
    gluten_free_brand.short_description = "Brand"
        
    def gluten_free_unit(self, obj):
        return obj.gluten_free.unit
    gluten_free_unit.short_description = "Unit"
        
    def gluten_free_price(self, obj):
        return obj.gluten_free.price
    gluten_free_price.short_description = "Price"

    def get_changelist(self, request, **kwargs):
        return AssociationChangeList

    # Change form title
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        context = dict(title=_('Gluten-Free product and its equivalent'))
        context.update(extra_context or {})
        return super(AssociationAdmin, self).changeform_view(request, object_id=object_id, form_url=form_url, extra_context=context)
    
    def changelist_view(self, request, extra_context=None):
        context = dict(search_database=request.GET.get('achat', None))
        context.update(extra_context or {})
        return super(AssociationAdmin, self).changelist_view(request, extra_context=context)

    class Media:
        css = {
            "all": (
                "admin/css/forms.css",
                )
              }
        js = (	
                'dbref/js/select_brand.js',
             )
