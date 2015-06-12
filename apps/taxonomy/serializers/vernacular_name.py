import autocomplete_light

from apps.taxonomy.models import CommonName
from rest_framework import serializers
from apps.taxonomy.models import TaxonNode
from apps.taxonomy.fields.autocomplete_field import AutocompleteHyperlinkedRelatedField


class VernacularNameSerializer(serializers.HyperlinkedModelSerializer):

    taxon_node = AutocompleteHyperlinkedRelatedField(
        widget=autocomplete_light.ChoiceWidget('TaxonNodeAutocomplete'),
        view_name='taxonnode-detail', required=True
    )

    class Meta:
        model = CommonName
        fields = [
            'id', 'url', 'iso_639', 'common_name', 'taxon_node', 'is_preferred'
        ]

    def get_fields(self, *args, **kwargs):
        """
        Filter out root nodes
        from returned list of available choices
        """
        fields = super(VernacularNameSerializer, self).get_fields(*args, **kwargs)
        fields['taxon_node'].queryset = TaxonNode.objects.filter(taxon_rank_id__gt=0).order_by('id')
        return fields
