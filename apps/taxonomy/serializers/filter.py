from apps.taxonomy.models import Filter
from apps.taxonomy.fields.taxon_rank_list_field import TaxonRankListField

from rest_framework import serializers


class FilterSerializer(serializers.HyperlinkedModelSerializer):
    included_ranks = TaxonRankListField(required=False, label='included ranks')
    excluded_ranks = TaxonRankListField(required=False, label='excluded ranks')

    class Meta:
        model = Filter
        fields = [
            'id', 'locale', 'lowest_rank', 'included_ranks', 'excluded_ranks', 'tree'
        ]
