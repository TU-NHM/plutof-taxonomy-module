from django.conf.urls import patterns

from apps.taxonomy.views.taxon import TaxonView
from apps.taxonomy.views.vernacular_name import VernacularNameView
from apps.taxonomy.views.act import ActView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'taxon', TaxonView)
router.register(r'vernacular_name', VernacularNameView)
router.register(r'act', ActView)

urlpatterns = patterns('',
                       # url('^by_scientific_name/', BaseSearchView.as_view(model=TaxonNode), name='taxon-search'),
                       # url('^by_vernacular_name/', BaseSearchView.as_view(model=CommonName), name='commonname-search'),
                       # url('^by_fuzzy_name/', TaxonByFuzzyNameView.as_view()),
                       )
