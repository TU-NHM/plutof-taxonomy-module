from haystack import indexes
import re


class BaseIndex(indexes.SearchIndex):
    """
    Base search index
    """
    text = indexes.EdgeNgramField(document=True, use_template=True)
    name = indexes.CharField(indexed=False, faceted=True)
    full_taxon_name = indexes.CharField(model_attr='full_taxon_name', default=None, indexed=False)
    ordering_name = indexes.CharField(model_attr='taxon_name', default=None, indexed=True)

    def prepare_ordering_name(self, obj):
        ordering_name = obj.taxon_name.lower()
        no_specials = re.sub("[., ()-@;&]", "", ordering_name)
        return no_specials


class CommonNameIndex(indexes.SearchIndex):
    """
    Base search index for vernacular names
    """
    text = indexes.NgramField(document=True, use_template=True)
    name = indexes.CharField(indexed=False, faceted=True)
    taxon_id = indexes.IntegerField(model_attr='taxon_node__id', default=None)
    iso_639 = indexes.CharField(model_attr='iso_639__iso_639', default=None)
    object_id = indexes.CharField(model_attr='id')
    ordering_name = indexes.CharField(model_attr='common_name', default=None, indexed=True)

    def prepare_ordering_name(self, obj):
        ordering_name = obj.common_name.lower()
        no_specials = re.sub("[., ()-@;&]", "", ordering_name)
        return no_specials
