import autocomplete_light

from apps.taxonomy.models import TaxonNode
from rest_framework import serializers, pagination
from rest_framework.reverse import reverse
from apps.taxonomy.fields.autocomplete_field import AutocompleteHyperlinkedRelatedField

from apps.taxonomy.fields.vernacular_name_list_field import VernacularNameListField
from apps.taxonomy.models import NOMEN_STATUSES, SYNONYM_TYPES
from apps.taxonomy.fields.taxon_parent_field import TaxonParentField


class TaxonSerializer(serializers.HyperlinkedModelSerializer):
    related_taxa = serializers.SerializerMethodField('get_related_taxa')
    is_valid = serializers.BooleanField(source='get_validity',
                                        read_only=True,
                                        label='is valid')
    synonyms = serializers.SerializerMethodField('get_synonyms')
    hybrid_parents = serializers.SerializerMethodField('get_hybrid_parents')
    traverse_next = serializers.SerializerMethodField('get_next_taxon')
    traverse_previous = serializers.SerializerMethodField('get_previous_taxon')
    depth = serializers.SerializerMethodField('get_depth')
    parent = TaxonParentField(required=False)
    taxon_name = serializers.SerializerMethodField('get_taxon_name')
    full_taxon_name = serializers.SerializerMethodField('get_full_taxon_name')
    remarks = serializers.CharField(required=False, source='remarks')
    citation_text = serializers.CharField(required=False, source='citation_text')
    tree = AutocompleteHyperlinkedRelatedField(many=False,
                                               view_name='tree-detail',
                                               required=True,
                                               autocomplete_class='TreeAutocomplete')
    taxon_rank = AutocompleteHyperlinkedRelatedField(many=False,
                                                     view_name='taxonrank-detail',
                                                     required=True,
                                                     autocomplete_class='TaxonRankAutocomplete')
    acts = serializers.HyperlinkedRelatedField(many=True,
                                               view_name='act-detail',
                                               read_only=True,
                                               label='Acts')
    vernacular_names = VernacularNameListField(read_only=True,
                                               label='Vernacular names')
    nomenclatural_status = serializers.ChoiceField(NOMEN_STATUSES, required=False, label="Nomenclatural status")
    synonym_type = serializers.ChoiceField(SYNONYM_TYPES, required=False, label="Synonym type")

    valid_name = AutocompleteHyperlinkedRelatedField(
        widget=autocomplete_light.ChoiceWidget('TaxonNodeAutocomplete'),
        view_name='taxonnode-detail', required=False
    )

    taxon_name_concept = AutocompleteHyperlinkedRelatedField(
        widget=autocomplete_light.ChoiceWidget('TaxonNameConceptAutocomplete'),
        view_name='taxonnameconcept-detail', required=False
    )

    parent_described_in = AutocompleteHyperlinkedRelatedField(
        widget=autocomplete_light.ChoiceWidget('TaxonNodeAutocomplete'),
        view_name='taxonnode-detail', required=False
    )

    class Meta:
        model = TaxonNode
        fields = [
            'id', 'url', 'parent',
            'depth', 'traverse_previous', 'traverse_next',
            'synonyms', 'parent_described_in', 'valid_name', 'synonym_type',
            'nomenclatural_status',
            'epithet', 'is_valid', 'related_taxa', 'hybrid_parents',
            'taxon_name_concept', 'taxon_rank', 'epithet_author',
            'year_described_in', 'use_parentheses', 'uid', 'code',
            'taxon_name', 'full_taxon_name', 'tree', 'acts',
            'vernacular_names', 'citation_text', 'remarks', 'is_fossil'
        ]

    def validate_valid_name(self, attrs, source):
        if attrs:
            tree = attrs.get("tree", None)
            if attrs[source] and (not attrs[source].tree):
                raise serializers.ValidationError("Selected taxon node is a root node")
            if (attrs[source] and (attrs[source].tree != tree)):
                raise serializers.ValidationError("Selected taxon node is linked to different tree")
            if attrs[source] and attrs[source].valid_name:
                raise serializers.ValidationError("Selected taxon node is also a synonym")
        return attrs

    def validate_parent_described_in(self, attrs, source):
        if attrs:
            tree = attrs.get("tree", None)
            if attrs[source] and (not attrs[source].tree):
                raise serializers.ValidationError("Selected taxon node is a root node")
            if attrs[source] and (attrs[source].tree != tree):
                origin_tree_id = self.object.tree.origin_tree_id
                if attrs[source] and (origin_tree_id != attrs[source].tree.id):
                    raise serializers.ValidationError("Selected taxon node has different tree")
        return attrs

    def validate_tree(self, attrs, source):
        tree = attrs.get("tree", None)
        if not tree:
            raise serializers.ValidationError("Tree is required")
        return attrs

    def validate_taxon_rank(self, attrs, source):
        taxon_rank = attrs.get("taxon_rank", None)
        if not taxon_rank:
            raise serializers.ValidationError("Taxon rank is required")
        parent = attrs.get("parent", None)
        if parent and parent.taxon_rank.id >= taxon_rank.id:
            raise serializers.ValidationError("Taxon rank must be greater than parent taxon rank")
        if parent and parent.taxon_rank.id >= "70":
            raise serializers.ValidationError("Parent cannot be species or lower level taxon, please choose genus or subgenus instead.")
        return attrs

    def restore_object(self, attrs, instance=None):
        attrs.pop('remarks', None)
        attrs.pop('citation_text', None)
        obj = super(TaxonSerializer, self).restore_object(attrs, instance)
        return obj

    def get_url_list(self, object_list):
        result_list = []
        for obj in object_list:
            field = serializers.HyperlinkedRelatedField(view_name='taxonnode-detail', source=self)
            result_list.append(field.get_url(obj=obj, view_name='taxonnode-detail',
                                             request=self.context.get('request', None),
                                             format=None))
        return result_list

    def get_related_taxa(self, taxon_node):
        if taxon_node:
            related_models = taxon_node.get_related_taxa()
            return self.get_url_list(related_models)

    def get_synonyms(self, taxon_node):
        if taxon_node:
            synonyms = taxon_node.get_synonyms()
            return self.get_url_list(synonyms)

    def get_hybrid_parents(self, taxon_node):
        if taxon_node:
            hybrid_parents = taxon_node.get_hybrid_parents()
            return self.get_url_list(hybrid_parents)

    def get_next_taxon(self, taxon_node):
        if taxon_node:
            next_taxon = taxon_node.get_next_taxon()
            if next_taxon:
                return reverse('taxonnode-detail', args=[next_taxon.id], request=self.context.get('request', None))
        return None

    def get_previous_taxon(self, taxon_node):
        if taxon_node:
            previous_taxon = taxon_node.get_previous_taxon()
            if previous_taxon:
                return reverse('taxonnode-detail', args=[previous_taxon.id], request=self.context.get('request', None))
        return None

    def get_depth(self, taxon_node):
        if taxon_node:
            return taxon_node.get_depth()

    def get_taxon_name(self, taxon_node):
        if taxon_node:
            return taxon_node.taxon_name

    def get_full_taxon_name(self, taxon_node):
        if taxon_node:
            return taxon_node.full_taxon_name


class PaginatedTaxonSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = TaxonSerializer
