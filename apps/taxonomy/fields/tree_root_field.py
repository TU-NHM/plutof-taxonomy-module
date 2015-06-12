from rest_framework import serializers
from apps.taxonomy.models import TaxonNode
from django.db.models import Q


class TreeRootField(serializers.WritableField):

    def field_to_native(self, tree, field_name):
        if tree:
            field = serializers.HyperlinkedRelatedField(view_name='taxonnode-detail', source=self)

            root_taxon = tree.root_node.get_related_taxa().filter(~Q(tree_id=None))
            if root_taxon.count() > 0 and tree.origin_tree:
                return field.get_url(obj=root_taxon[0], view_name='taxonnode-detail', request=self.context.get('request', None), format=None)
            else:
                return None

    def from_native(self, taxon_url):
        if taxon_url:
            try:
                field = serializers.HyperlinkedRelatedField(view_name='taxonnode-detail', queryset=TaxonNode.objects.all(), source=self)
                return field.from_native(taxon_url).pk
            except:
                raise serializers.ValidationError("'%s' is not a valid url" % taxon_url)
        return None
