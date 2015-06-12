from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

import autocomplete_light
autocomplete_light.autodiscover()

admin.autodiscover()

from rest_framework import routers
from apps.taxonomy.urls import router as taxonomy_router
from apps.taxonomy.views.taxon_rank import TaxonRankView
from apps.taxonomy.views.vernacular_name import VernacularNameView
from apps.taxonomy.views.hybrid_taxon_node import HybridTaxonNodeView
from apps.taxonomy.views.language import LanguageView
from apps.taxonomy.views.filter import FilterView
from apps.taxonomy.views.tree import TreeView
from apps.taxonomy.views.taxon_name_concept import TaxonNameConceptView
from apps.taxonomy.views.taxon_search import BaseSearchView, CommonNameSearchView
from apps.taxonomy.models import CommonName, TaxonNode

router = routers.DefaultRouter()
router.registry = taxonomy_router.registry
router.register(r'taxon_rank', TaxonRankView)
router.register(r'vernacular_name', VernacularNameView)
router.register(r'language', LanguageView)
router.register(r'hybridtaxonnode', HybridTaxonNodeView)
router.register(r'filter', FilterView)
router.register(r'tree', TreeView)
router.register(r'taxon_name_concept', TaxonNameConceptView)

urlpatterns = patterns('',
                       # url(r'^$', RedirectView.as_view(url='api/taxonomy/', permanent=False)),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^api/taxonomy/vernacular_name/search/', CommonNameSearchView.as_view(model=CommonName), name='commonname-search'),
                       url(r'^api/taxonomy/taxon/search/', BaseSearchView.as_view(model=TaxonNode), name='taxon-search'),
                       url(r'^api/taxonomy/taxon/', include('apps.taxonomy.urls')),
                       url(r'^api/taxonomy/', include(router.urls)),
                       # Auth API
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
                       # Search
                       url(r'^autocomplete/', include('autocomplete_light.urls')),
                       # Application
                       url(r'^$', TemplateView.as_view(template_name='index.html'), name="home"),
                       url(r'^v1/getting-started$', TemplateView.as_view(template_name='v1/getting_started.html'),
                           name="getting-started"),
                       url(r'^api/taxonomy/docs/', include('rest_framework_swagger.urls')),
                       )
