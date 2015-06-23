
from decimal import *
from django.db.models import Sum
from django.db.models import When, F, Q
from django.contrib.admin.templatetags.admin_list import *
from django.template import Library
from django.template.context import Context

register = Library()

DOT = '.'

class AchatResultList(ResultList):
    def __init__(self, obj, form, *items):
        self.form = form
        self.pending = False
        if hasattr(obj, 'pending'):
            self.pending = True
        super(AchatResultList, self).__init__(form, *items)

def results(cl):
    for res in cl.result_list:
        yield AchatResultList(res, None, items_for_result(cl, res, None))

@register.inclusion_tag("achat/achat_change_list_results.html")
def achat_result_list(cl):
    """
    Displays the headers and data list together
    """
    headers = list(result_headers(cl))
    num_sorted_fields = 0
    for h in headers:
        if h['sortable'] and h['sorted']:
            num_sorted_fields += 1
    return {'cl': cl,
            'result_hidden_fields': list(result_hidden_fields(cl)),
            'result_headers': headers,
            'num_sorted_fields': num_sorted_fields,
            'results': list(results(cl))}

def get_incremental_cost(cl):
    if cl.result_list.count() == 0:
        return Decimal(0.00)
    inc_cost = cl.result_list.aggregate(incremental_cost=Sum(F('cost')))
    return round(inc_cost['incremental_cost'], 2)

@register.inclusion_tag("achat/achat_summary_results.html")
def achat_summary(cl):
    """
    Displays total incremental cost
    """
    return {'cl': cl,
            'cost': get_incremental_cost(cl) }

@register.simple_tag
def achat_period_list_filter(cl, spec):
    if hasattr(spec, 'parameter_period'):
        tpl = get_template(spec.template)
        return tpl.render(Context({
            'periods': spec.year_list(cl),
            'spec': spec,
        }))

