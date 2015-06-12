from haystack import indexes

from apps.taxonomy.models import TaxonNode, CommonName
from taxonomy.search_indexes import BaseIndex, CommonNameIndex


class TaxonNodeIndex(BaseIndex, indexes.Indexable):
    def get_model(self):
        return TaxonNode

    def index_queryset(self, using=None):
        return self.get_model().objects.exclude(taxon_rank__id=0)


class CommonNameIndex(CommonNameIndex, indexes.Indexable):
    def get_model(self):
        return CommonName
