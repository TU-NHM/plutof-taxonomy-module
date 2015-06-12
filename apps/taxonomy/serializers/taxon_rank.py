from apps.taxonomy.models import TaxonRank
from rest_framework import serializers


class TaxonRankSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonRank
        fields = [
            'id', 'url', 'abbreviation', 'botany_rank'
        ]
