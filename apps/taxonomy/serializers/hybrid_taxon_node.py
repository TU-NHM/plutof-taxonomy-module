import autocomplete_light

from rest_framework import serializers
from apps.taxonomy.models import HybridTaxonNode, TaxonNode
from apps.taxonomy.fields.autocomplete_field import AutocompleteHyperlinkedRelatedField


class HybridTaxonNodeSerializer(serializers.HyperlinkedModelSerializer):

    taxon_node = AutocompleteHyperlinkedRelatedField(
        widget=autocomplete_light.ChoiceWidget('TaxonNodeAutocomplete'),
        view_name='taxonnode-detail', required=True
    )
    hybrid_parent1 = AutocompleteHyperlinkedRelatedField(
        widget=autocomplete_light.ChoiceWidget('TaxonNodeAutocomplete'),
        view_name='taxonnode-detail', required=True
    )
    hybrid_parent2 = AutocompleteHyperlinkedRelatedField(
        widget=autocomplete_light.ChoiceWidget('TaxonNodeAutocomplete'),
        view_name='taxonnode-detail', required=True
    )

    class Meta:
        model = HybridTaxonNode
        fields = [
            'id', 'url', 'taxon_node', 'hybrid_parent1', 'hybrid_parent2'
        ]

    def get_fields(self, *args, **kwargs):
        """
        Filter out root nodes
        from returned list of available choices
        """
        fields = super(HybridTaxonNodeSerializer, self).get_fields(*args, **kwargs)
        fields['taxon_node'].queryset = TaxonNode.objects.filter(taxon_rank_id__gt=0).order_by('id')
        fields['hybrid_parent1'].queryset = TaxonNode.objects.filter(taxon_rank_id__gt=0).order_by('id')
        fields['hybrid_parent2'].queryset = TaxonNode.objects.filter(taxon_rank_id__gt=0).order_by('id')
        return fields
