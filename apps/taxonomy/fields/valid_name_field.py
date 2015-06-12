from rest_framework import serializers

from apps.taxonomy.models import TaxonNode


class ValidNameField(serializers.WritableField):

    def field_to_native(self, taxon_node, field_name):
        if taxon_node and taxon_node.valid_name:
            valid_taxon = TaxonNode.objects.get(pk=taxon_node.valid_name)
            field = serializers.HyperlinkedRelatedField(view_name='taxonnode-detail', source=self)
            return field.get_url(obj=valid_taxon, view_name='taxonnode-detail', request=self.context.get('request', None), format=None)

    def from_native(self, taxon_url):
        if taxon_url:
            try:
                field = serializers.HyperlinkedRelatedField(view_name='taxonnode-detail', queryset=TaxonNode.objects.all(), source=self)
                return field.from_native(taxon_url).pk
            except:
                raise serializers.ValidationError("'%s' is not a valid url" % taxon_url)
        return None
