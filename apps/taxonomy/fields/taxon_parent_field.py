from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.taxonomy.models import TaxonNode


class TaxonParentField(serializers.WritableField):

    def field_to_native(self, taxon_node, field_name):
        if taxon_node:
            field = serializers.HyperlinkedRelatedField(view_name='taxonnode-detail', source=self)
            parent = taxon_node.get_parent()
            if parent and not parent.is_root_node():
                return field.get_url(obj=parent, view_name='taxonnode-detail', request=self.context.get('request', None), format=None)
            return None

    def from_native(self, taxon_url):
        if taxon_url:
            if hasattr(taxon_url, "isdigit") and taxon_url.isdigit():
                taxon_url = reverse('taxonnode-detail', args=[int(taxon_url)])
            try:
                field = serializers.HyperlinkedRelatedField(view_name='taxonnode-detail', queryset=TaxonNode.objects.all(), source=self)
                return field.from_native(taxon_url)
            except:
                raise serializers.ValidationError("'%s' is not a valid url" % taxon_url)
        return ''
