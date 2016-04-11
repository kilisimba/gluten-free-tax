
import urllib
import datetime
from decimal import *
from django import forms
from django.db.models import When, F, Q
from django.db.models import DecimalField, Case, Value, When
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.forms import widgets
from django.db.models import Sum
from achat.models import Achat, Pending
from dbref.models import Association
from newlook.admin import NewlookModelAdmin

class AchatListFilter(admin.ListFilter):
    title = ('period')
    parameter_period = 'period'
    template = 'achat/achat_period_filter.html'

    def __init__(self, request, params, model, model_admin):
        super(AchatListFilter, self).__init__(
            request, params, model, model_admin)
        for p in self.expected_parameters():
            if p in params:
                value = params.pop(p)
                self.used_parameters[p] = value

    def expected_parameters(self):
        return [ self.parameter_period, ]
        
    def queryset(self, request, qs):
        if self.period() == 0:
            return qs
        #import rpdb2
        #rpdb2.start_embedded_debugger("qwe123")
        #first_day_of_year = datetime.date(self.period(),1,1)
        #last_day_of_year = datetime.date(self.period(),12,31)
        #return qs.filter(date__range=(first_day_of_year, last_day_of_year)
        return qs.filter(date__year=self.period())

    def has_output(self):
        return True

    def choices(self, cl):
        return {}

    def period(self):
        return int(self.used_parameters[self.parameter_period]) \
                    if self.used_parameters.get(self.parameter_period, None) else 0

    def year_list(self, cl):
        date_list = Achat.objects.all().values('date')
        year_list = map( lambda x: x['date'].year, date_list )
        all_list = list(set(year_list))
        all_list.insert(0, 'All')
        for year in all_list:
            yield {
                'display': year,
                'selected': self.used_parameters[self.parameter_period] == str(year) \
                                if self.parameter_period in self.used_parameters else False,
            }


class AchatForm(forms.ModelForm):
    description = forms.CharField(   label='Description', \
                                     widget=widgets.TextInput(attrs={'size':"120"}), \
                                     max_length=300, \
                                     required=False )
    equivalent = forms.CharField(    label='Description', \
                                     widget=widgets.TextInput(attrs={'size':"120"}), \
                                     max_length=300, \
                                     required=False )

    class Meta:
        model = Achat
        fields = ['date', 'description', 'brand', 'unit', 'price', 'equivalent', 'equivalent_unit', \
                    'equivalent_price', 'quantity', 'taxable' ]

from django.contrib.admin.views.main import ChangeList
class AchatChangeList(ChangeList):
    IGNORED_PARAMS = ( 'association', 'product', )
    
    def __init__(self, request, model, list_display, list_display_links,
            list_filter, date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, model_admin):

            super(AchatChangeList, self).__init__(request, model, list_display, list_display_links,
            list_filter, date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, model_admin)
            """
            Set our title
            """
            self.title = 'Please select a purchase record'

    def get_filters_params(self, params=None):
        lookup_params = super(AchatChangeList, self).get_filters_params(params=params)
        # Remove all the parameters that are globally and systematically
        for ignored in self.IGNORED_PARAMS:
            if ignored in lookup_params:
                del lookup_params[ignored]
        return lookup_params
        
    def get_results(self, request):
        super(AchatChangeList, self).get_results(request)
        result_list = self.result_list.annotate(
            unit_price=Case(
                When(unit=Decimal(0), then=0),
                default=F('price')/F('unit'),
                output_field = DecimalField(),
            ),
            eq_unit_price=Case(
                When(equivalent_unit=Decimal(0), then=0),
                default=F('equivalent_price')/F('equivalent_unit'),
                output_field = DecimalField(),
            ),
        )
        self.result_list = result_list.annotate(cost=Case(
                When(unit_price__lte=F('eq_unit_price'), then=0),
                default=F('quantity')*F('unit')*(F('unit_price')-F('eq_unit_price')),
                output_field = DecimalField(),
             ),)

    def get_filters(self, request):
        """
        This will set 'has_filters' to False.
        This is necesary to remove the empty filter column on the right side of the window
        """
        (filter_specs, has_filters, lookup_params, use_distinct) = \
            super(AchatChangeList, self).get_filters(request)
        return filter_specs, False, lookup_params, use_distinct

@admin.register(Achat)
class AchatAdmin(NewlookModelAdmin):
    change_form_template = 'achat/change_form.html'
    change_list_template = 'achat/change_list.html'
    form = AchatForm
    list_filter = ( AchatListFilter, )
    #list_editable = ('taxable',)
    list_display = ('date', 'description', 'brand', 'unit', 'price', 'quantity', \
                    'equivalent', 'equivalent_unit', 'equivalent_price', 'taxable', 'cost')
    fieldsets = (
        (None, {
            'fields': ( 'date', 'quantity', 'taxable' )
        }),
        ('Gluten Free Product', {
            'fields': ( 'description', ('unit', 'price') )
        }),
        ('Equivalent Product', {
            'fields' : ('equivalent', ('equivalent_unit', 'equivalent_price') )
        }),
    )
    admin.actions.delete_selected.short_description = "Delete"
    actions = [ 'duplicate', ]

    # Override ModelAdmin
    def get_object(self, request, object_id, to_field):
        obj = super(AchatAdmin,self).get_object(request, object_id, to_field)
        if 'association' in request.GET:
            association_id = request.GET.get('association')
            association_obj = Association.objects.get(pk=association_id)
            obj.description = association_obj.gluten_free.description
            obj.brand = association_obj.gluten_free.company.brands()
            obj.unit = association_obj.gluten_free.unit
            obj.price = association_obj.gluten_free.price
            if association_obj.equivalent:
                obj.equivalent = association_obj.equivalent.description
                obj.equivalent_unit = association_obj.equivalent.unit
                obj.equivalent_price = association_obj.equivalent.price
            else:
                obj.equivalent = ""
                obj.equivalent_unit = ""
                obj.equivalent_price = ""
            return obj
        if 'product' in request.GET:
            association_id = request.GET.get('product')
            association_obj = Association.objects.get(pk=association_id)
            obj.description = association_obj.gluten_free.description
            obj.brand = association_obj.gluten_free.company.brands()
            obj.unit = association_obj.gluten_free.unit
            obj.price = association_obj.gluten_free.price
        return obj

    # Change form title
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'POST' and "_searchdatabase" in request.POST:
            if object_id is None:
                ModelForm = self.get_form(request, None)
                form = ModelForm(request.POST, request.FILES, instance=None)
                if not form.is_valid():
                    return super(AchatAdmin, self).changeform_view(request, \
                        object_id, form_url, extra_context)
                new_object = self.save_form(request, form, change=False)
                new_object.save()
                pending = Pending(achat=new_object)
                pending.save()
                object_id = new_object.pk
            post_url = reverse('admin:dbref_association_changelist')
            post_url += '?' + urllib.parse.urlencode({'achat': object_id})
            return HttpResponseRedirect(post_url)

        if request.method == 'POST' and "_cancel" in request.POST:
            post_url = reverse('admin:achat_achat_changelist')
            return HttpResponseRedirect(post_url)

        if request.method == 'POST' and "_save" in request.POST:
            if object_id is not None:
                obj = self.get_object(request, unquote(object_id), None)
                if hasattr(obj, 'pending'):
                    obj.pending.delete()

        add = object_id is None
        title=(_('Add %s') if add else _('Change %s')) % _('purchase record')
        context = dict(title=title)
        context.update(extra_context or {})
        return super(AchatAdmin, self).changeform_view(request, \
            object_id, form_url, context)

    def formfield_for_dbfield(self, db_field, **kwargs):
        # Set default date to today if not specified
        if db_field.name == "date":
            kwargs["initial"] = datetime.date.today()

        return super(AchatAdmin, self). \
               formfield_for_dbfield(db_field, **kwargs)

    def get_changelist(self, request, **kwargs):
        return AchatChangeList

    def cost(self, obj):
        return round(obj.cost, 2)

    def duplicate(self, request, queryset):
        for record in queryset:
            record.pk = None
            record.date = datetime.date.today()
            record.save()
            pending = Pending(achat=record)
            pending.save()
    duplicate.short_description = "Duplicate"

    class Media:
        css = {
                "all": ("achat/css/change_list.css",)
              }
        js = (	
                'achat/js/process_period.js',
             )
