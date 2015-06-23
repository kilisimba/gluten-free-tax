from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.admin import site
from django.core.urlresolvers import reverse
import types
import collections


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ssg.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

def each_extra_context(site_each_context):
    def each_context(self, request):
        main_menu = collections.OrderedDict()
        main_menu['Achat'] = reverse('admin:achat_achat_changelist')
        main_menu['Lookup Tables'] = reverse('admin:dbref_association_changelist')
        main_menu['Admin'] = reverse('admin:index')
        context = site_each_context(request)
        context.update ( {
                            'main_menu': main_menu,
                        } )
        return context
    return each_context

site.site_title = 'Gluten-Free admin'
site.site_header = 'Gluten-Free Accounting'
site.index_title = 'Gluten-Free Site administration'
site.index_template = 'newlook/index.html'
site.app_index_template = 'newlook/app_index.html'

# Overwrite AdminSite.each_context instance to include 'main_menu'
site.each_context = types.MethodType(each_extra_context(site.each_context), site)
