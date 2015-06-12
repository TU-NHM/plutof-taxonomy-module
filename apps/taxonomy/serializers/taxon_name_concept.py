from apps.taxonomy.models import TaxonNameConcept
from rest_framework import serializers
from apps.taxonomy.serializers.taxon import TaxonSerializer


class TaxonNameConceptSerializer(serializers.HyperlinkedModelSerializer):
    taxa = TaxonSerializer(many=True)

    class Meta:
        model = TaxonNameConcept
        fields = [
            'url', 'taxa'
        ]
