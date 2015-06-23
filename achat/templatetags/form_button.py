from django import template

register = template.Library()


@register.inclusion_tag('achat/achat_submit_line.html', takes_context=True)
def achat_submit_row(context):
    """
    Displays the row of buttons for delete and save.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    ctx = {
        'opts': opts,
        'show_delete_link': False,
        'show_save_as_new': False,
        'show_save_and_add_another': False,
        'show_save_and_continue': False,
        'is_popup': False,
        'show_save': True,
        'preserved_filters': context.get('preserved_filters'),
        'cancel_operation': True,
        'search_database': True,    # Searchable database
    }
    if context.get('original') is not None:
        ctx['original'] = context['original']
    return ctx

