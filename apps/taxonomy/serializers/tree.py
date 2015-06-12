import autocomplete_light

from rest_framework import serializers
from apps.taxonomy.models import Tree, Edge
from apps.taxonomy.fields.autocomplete_field import AutocompleteHyperlinkedRelatedField


class TreeSerializer(serializers.HyperlinkedModelSerializer):
    origin_tree = serializers.HyperlinkedRelatedField(many=False, view_name='tree-detail', required=False)

    root_node = AutocompleteHyperlinkedRelatedField(
        widget=autocomplete_light.ChoiceWidget('TaxonNodeAutocomplete'),
        view_name='taxonnode-detail', required=False
    )

    class Meta:
        model = Tree
        fields = [
            'id', 'url', 'name', 'origin_tree', 'root_node'
        ]

    def validate(self, attrs):
        NODE_LIMIT = 5000
        origin_tree_children_count = 0
        root_node_children_count = 0
        root_node = attrs.get("root_node", None)
        origin_tree = attrs.get("origin_tree", None)

        if root_node:
            if origin_tree and (root_node.tree != origin_tree):
                raise serializers.ValidationError("The root_node does not belong to the given tree")
            root_node_children_count = Edge.objects.filter(ancestor=root_node).count()
            if root_node_children_count > NODE_LIMIT:
                raise serializers.ValidationError("Selected root node's taxon count exceeds the allowed limit, please contact site administrator for further details.")

        if origin_tree and origin_tree.root_node:
            origin_tree_children_count = Edge.objects.filter(ancestor=origin_tree.root_node).count()
            if origin_tree_children_count > NODE_LIMIT:
                raise serializers.ValidationError("Selected tree's taxon count exceeds the allowed limit, please contact site administrator for further details.")
        return super(TreeSerializer, self).validate(attrs)

    def restore_object(self, attrs, instance=None):
        # making origin_tree and root_node not editable.
        if instance is not None:
            attrs.pop('origin_tree', None)
            attrs.pop('root_node', None)
            return instance
        return Tree(**attrs)
