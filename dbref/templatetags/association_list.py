from __future__ import unicode_literals

import datetime
from django.template import Library
from django.template.loader import get_template
from django.template.context import Context
from django.contrib.admin.templatetags.admin_list import *

register = Library()

DOT = '.'


@register.simple_tag
def association_brand_list_filter(cl, spec):
    if hasattr(spec, 'parameter_brand'):
        tpl = get_template(spec.template)
        return tpl.render(Context({
            'brands': list(spec.brand_list(cl)),
            'spec': spec,
        }))


@register.inclusion_tag("dbref/association_change_list_results.html")
def association_result_list(cl):
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
            'results': list(results(cl)),
            'action':  'action' in headers[0]['text'] }

