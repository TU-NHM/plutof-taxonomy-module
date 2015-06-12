from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker
from django.core.exceptions import ValidationError
from django.core.management import call_command

# from itertools import chain


class Language(models.Model):
    iso_639 = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class TaxonRank(models.Model):
    abbreviation = models.CharField(max_length=255)
    zoology_rank = models.CharField(max_length=255)
    botany_rank = models.CharField(max_length=255)
    bacteria_rank = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255)
    suffix = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s" % (self.abbreviation)


# TODO:
#     Cloning a tree starting from synonym should be prohibited
#     Taxon name concept usage is UNIQUE inside one tree. Add checks and constraints

class TreeCloner():

    @staticmethod
    def clone(new_tree, starting_node):
        if not starting_node.tree_id:
            # we are cloning full tree, as origin_tree was given.
            TreeCloner.add_starting_node(new_tree.root_node, starting_node)
        cloner = TreeCloner(new_tree, starting_node)
        cloner.start_cloning()

    @staticmethod
    def add_starting_node(new_tree_root, starting_root_node):
        new_tree_root.taxon_name_concept = starting_root_node.taxon_name_concept
        new_tree_root.save()

    def __init__(self, new_tree, starting_node):
        self.new_tree = new_tree
        self.starting_node = starting_node
        self.levels = self.get_levels()
        subtree_taxa = Edge.objects.filter(ancestor_id=self.starting_node.pk).values('descendant_id')
        self.subtree_taxon_ids = [edge['descendant_id'] for edge in subtree_taxa]

    def get_levels(self):
        return Edge.objects.filter(ancestor=self.starting_node).order_by('-length').first().length

    def start_cloning(self):
        for level in self.get_cloneable_level_range():
            self.clone_level(level)
        call_command('populate_pre_traversal', self.new_tree.pk)

    def get_cloneable_level_range(self):
        if self.starting_node.tree_id:
            # cloning tree starting from a taxon
            return range(0, self.levels + 1)
        return range(1, self.levels + 1)

    def clone_level(self, level):
        level_taxon_node_ids = [edge.descendant_id for edge in Edge.objects.filter(ancestor_id=self.starting_node.pk, length=level)]
        nodes = TaxonNode.objects.filter(pk__in=level_taxon_node_ids).filter(valid_name=None)
        for node in nodes:
            new_node = self.clone_node(node)
            self.connect_with_parent(node, new_node, level)
            self.clone_synonyms(node, new_node)

    def clone_synonyms(self, node, new_node):
        for synonym in node.get_synonyms():
            if synonym.parent_described_in.pk in self.subtree_taxon_ids:
                new_synonym = self.clone_node(synonym)
                self.update_dependencies_for_new_synonym(new_synonym, new_node)
                self.create_edge_to_self(new_synonym)

    def update_dependencies_for_new_synonym(self, synonym, new_valid_name):
        parent_described_in = TaxonNode.objects.get(taxon_name_concept=synonym.parent_described_in.taxon_name_concept, tree_id=self.new_tree.pk)
        synonym.parent_described_in = parent_described_in
        synonym.valid_name = new_valid_name
        synonym.save()

    def create_edge_to_self(self, new_synonym):
        # all synonyms only have one edge to self
        edge = Edge(ancestor_id=new_synonym.id, descendant_id=new_synonym.id, length=0)
        edge.save()

    def clone_node(self, node):
        new_node = TaxonNode.objects.get(pk=node.pk)
        new_node.pk = None
        new_node.tree = self.new_tree
        new_node.save()
        # create post_created_act
        new_node.create_post_created_act('', '')

        return new_node

    def connect_with_parent(self, node, new_node, level):
        if self.should_connect_with_root_node(level):  # not first level in tree we take parent as root_node
            new_node_parent = self.new_tree.root_node
        else:
            new_node_parent = TaxonNode.objects.get(tree=self.new_tree, taxon_name_concept=node.get_parent().taxon_name_concept)
        new_node.create_edges(new_node_parent)

    def should_connect_with_root_node(self, level):
        if self.starting_node.tree_id:
            return level == 0
        return level <= 1


class Tree(models.Model):
    name = models.CharField(max_length=255)
    origin_tree = models.ForeignKey('self', related_name='origin', null=True, blank=True)
    root_node = models.ForeignKey('TaxonNode', related_name='root', null=True, blank=True)  # on trees that hold the whole tree
    owner_id = models.IntegerField(null=True)
    created_by = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True, blank=True)
    updated_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(blank=True, default='2000-01-01 00:00:00+03:00')
    is_public = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def create_root_node(self):
        self.root_node = TaxonNode(epithet=self.name,
                                   taxon_rank_id=0
                                   )
        self.root_node.save()
        self.root_node.create_edges(parent=None)
        self.root_node_id = self.root_node.pk
        self.save()

    def get_root_children(self):
        """
        Return first level children for root node
        """
        children_ids = [edge.descendant_id for edge in Edge.objects.filter(ancestor=self.root_node, length=1)]
        return TaxonNode.objects.filter(pk__in=children_ids)

    def get_taxon_count(self):
        return TaxonNode.objects.filter(tree=self).count()

    def clone_starting_from_taxon_node(self, starting_root_node):
        TreeCloner.clone(self, starting_root_node)

    def __unicode__(self):
        return u"%s" % (self.name)


@receiver(post_save, sender=Tree)
def tree_post_save(sender, instance, created, **kwargs):
    # Initial save is when there is no root node set or root_node is actually
    # a node inside another tree
    if created:
        if instance.root_node:
            old_root = instance.root_node
        elif instance.origin_tree:
            old_root = instance.origin_tree.root_node
        else:
            old_root = None
        # always create a new root node for a new tree as it cannot belong to
        # any other tree. will be connected with previous root afterwards.
        instance.create_root_node()

        if old_root:
            instance.clone_starting_from_taxon_node(old_root)


class TaxonNameConcept(models.Model):
    pass

    def __unicode__(self):
        return u"%s" % (self.id)


SYNONYM_TYPES = (
                ('synonym', _('Synonym')),
                ('basionym', _('Basionym')),
                ('invalid', _('Invalid'))
)

NOMEN_STATUSES = (
                 ('established', _('Established')),
                 ('compliant', _('Compliant')),
                 ('non-compliant', _('Non-compliant')),
                 ('registered', _('Registered'))
)


class SubtreeHelper():
    @staticmethod
    def find_last_traversal_node(taxonnode):
        subtree_ids = [edge.descendant_id for edge in Edge.objects.filter(ancestor_id=taxonnode.pk, length__gt=0)]        # TraversalOrder.objects.filter(current_id__in=subtree_ids)
        if len(subtree_ids):
            subtree_edges = Edge.objects.filter(ancestor_id__in=subtree_ids)
            leaf_ids = list(set(edge['ancestor_id'] for edge in subtree_edges.filter(length=0).values('ancestor_id')) - set(edge['ancestor_id'] for edge in subtree_edges.filter(length=1).values('ancestor_id')))

            last_traversal = TraversalOrder.objects.filter(current_id__in=leaf_ids).filter(~Q(next_id__in=subtree_ids)).first()

            return last_traversal
        else:
            return TraversalOrder.objects.get(current_id=taxonnode.id)


class TaxonNode(models.Model):
    """
    parent_described_in = parent taxon this taxon was originally described in,
    required for synonyms only;
    valid_name = valid taxon for this taxon, required for synonyms only;
    """
    tree = models.ForeignKey(Tree, null=True)
    code = models.CharField(max_length=255, verbose_name='User defined ID', help_text='User defined ID', null=True, blank=True)
    uid = models.CharField(max_length=255, null=True, blank=True)
    epithet = models.CharField(max_length=255)
    parent_described_in = models.ForeignKey('self', null=True, blank=True, related_name="original_parent", on_delete=models.PROTECT)
    valid_name = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)
    synonym_type = models.CharField(max_length=63, null=True, blank=True, choices=SYNONYM_TYPES)
    nomenclatural_status = models.CharField(max_length=63, null=True, blank=True, choices=NOMEN_STATUSES)
    taxon_rank = models.ForeignKey(TaxonRank, null=True)
    taxon_name_concept = models.ForeignKey(TaxonNameConcept, blank=True, null=True, related_name='taxa')
    epithet_author = models.CharField(max_length=255, blank=True, verbose_name='Author')
    year_described_in = models.CharField(max_length=63, blank=True, null=True)
    use_parentheses = models.BooleanField(default=False)
    owner_id = models.IntegerField(null=True)
    created_by = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True, blank=True)
    updated_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(blank=True, default='2000-01-01 00:00:00+03:00')
    is_deleted = models.BooleanField(default=False)
    is_fossil = models.BooleanField(default=False)

    tracker = FieldTracker()

    @property
    def taxon_name(self):
        if not self.taxon_rank or self.taxon_rank.id < 70:
            return self.epithet
        if self.parent_described_in:
            if self.parent_described_in.taxon_rank_id == 63:
                # subgenus should be displayed between gen and sp epithet
                sbg_parent = self.parent_described_in.get_parent()
                if sbg_parent:
                    return "%s (%s) %s" % (sbg_parent.epithet,
                                           self.parent_described_in.epithet,
                                           self.epithet)
                else:
                    # parent_described_in (subgenus) is also a synonym
                    sbg_parent = self.parent_described_in.parent_described_in
                    return "%s (%s) %s" % (sbg_parent.epithet,
                                           self.parent_described_in.epithet,
                                           self.epithet)
            else:
                return "%s %s" % (self.parent_described_in.epithet,
                                  self.epithet)
        parent = self.get_parent()
        if parent and not parent.is_root_node():
            if parent.taxon_rank_id == 63:
                # subgenus should be displayed between gen and sp epithet
                sbg_parent = parent.get_parent()
                if sbg_parent:
                    return "%s (%s) %s" % (sbg_parent.epithet, parent.epithet,
                                           self.epithet)
                else:
                    # parent_described_in (subgenus) is also a synonym
                    sbg_parent = parent.parent_described_in
                    return "%s (%s) %s" % (sbg_parent.epithet, parent.epithet,
                                           self.epithet)
            else:
                return "%s %s" % (parent.epithet, self.epithet)
        if parent and parent.is_root_node() and self.taxon_rank.id >= 70:
            """ The following code assumes that the original tree & subtree
            root node will not be removed in the future (needed to display
            full taxon name correctly on species level and below)
            """
            cloned_from_parent = TaxonNode.objects.filter(
                taxon_name_concept=self.tree.root_node.taxon_name_concept,
                tree=self.tree.origin_tree).first()
            if cloned_from_parent:
                if cloned_from_parent.taxon_rank_id == 63:
                    # subgenus should be displayed between gen and sp epithet
                    sbg_parent = cloned_from_parent.get_parent()
                    return "%s (%s) %s" % (sbg_parent.epithet,
                                           cloned_from_parent.epithet,
                                           self.epithet)
                else:
                    return "%s %s" % (cloned_from_parent.epithet, self.epithet)
        else:
            return self.epithet

    @property
    def remarks(self):
        return ""

    @property
    def citation_text(self):
        return ""

    @property
    def full_taxon_name(self):
        if self.use_parentheses is True:
            if self.year_described_in:
                return "%s (%s, %s)" % (self.taxon_name, self.epithet_author,
                                        self.year_described_in)
            else:
                if self.epithet_author:
                    return "%s (%s)" % (self.taxon_name, self.epithet_author)
                else:
                    return "%s" % (self.taxon_name)
        else:
            if self.year_described_in:
                return "%s %s, %s" % (self.taxon_name, self.epithet_author,
                                      self.year_described_in)
            else:
                if self.epithet_author:
                    return "%s %s" % (self.taxon_name, self.epithet_author)
                else:
                    return "%s" % (self.taxon_name)

    @property
    def taxon_name_with_tree(self):
        if self.tree:
            return self.full_taxon_name + " (" + self.tree.name + ")"
        else:
            return self.full_taxon_name

    def __unicode__(self):
        return self.full_taxon_name

    def get_validity(self):
        return False if self.valid_name else True

    def is_root_node(self):
        if not self.tree:
            return True
        return False

    def detach_from_tree_until_node(self, new_root):
        edges = Edge.objects.filter(descendant=self).order_by('-length')
        for edge in edges:
            if int(edge.ancestor.pk) == int(new_root.pk):
                break
            edge.delete()

    def detach_subtree_from_tree(self):
        edges = Edge.objects.filter(descendant=self)
        for edge in edges:
            if int(edge.ancestor.pk) != int(self.pk):
                edge.delete()
        for taxonnode in self.subtree():
            taxonnode.detach_from_tree_until_node(self)

    def attach_with_parent(self, new_parent):
        ancestors = Edge.objects.filter(descendant=new_parent)
        for parent_edge in ancestors:
            edge = Edge(descendant=self, ancestor=parent_edge.ancestor, length=parent_edge.length + 1)
            edge.save()

    def attach_with_tree_outside_of_subtree(self, subtree_root):
        length_from_subtree_root = Edge.objects.get(descendant=self, ancestor=subtree_root).length
        edges_till_root = Edge.objects.filter(descendant=subtree_root.get_parent())
        for edge in edges_till_root:
            length = edge.length + length_from_subtree_root + 1
            edge = Edge(descendant=self, ancestor=edge.ancestor, length=length)
            edge.save()

    def attach_subtree_with_parent(self, new_parent):
        self.attach_with_parent(new_parent)
        for taxonnode in self.subtree():
            taxonnode.attach_with_tree_outside_of_subtree(self)

    def set_new_parent(self, new_parent):
        # used only when changing current parent
        new_parent = new_parent if new_parent else self.tree.root_node
        self.detach_subtree_from_tree()

        if not self.valid_name:
            # only non-synonyms can have a parent and can exist in traversal
            # order
            self.attach_subtree_with_parent(new_parent)

            last_traversal = SubtreeHelper.find_last_traversal_node(self)
            self.remove_subtree_from_traversal_order(last_traversal)
            self.add_subtree_to_traversal_order(new_parent, last_traversal)

        return True

    def add_subtree_to_traversal_order(self, new_parent, last_traversal):
        first_traversal = TraversalOrder.objects.get(current_id=self.pk)

        if new_parent.is_root_node():
            next_traversal = TraversalOrder.objects.get(current_id=self.get_one_first_level_taxonnode())
            previous_traversal = TraversalOrder.objects.get(current_id=next_traversal.previous_id)
        else:
            previous_traversal = TraversalOrder.objects.get(current_id=new_parent)
            next_traversal = TraversalOrder.objects.get(current_id=previous_traversal.next_id)

        previous_traversal.next_id = first_traversal.current_id
        first_traversal.previous_id = previous_traversal.current_id
        last_traversal.next_id = next_traversal.current_id
        next_traversal.previous_id = last_traversal.current_id

        previous_traversal.save()
        first_traversal.save()
        last_traversal.save()
        next_traversal.save()

    def remove_subtree_from_traversal_order(self, last_traversal, attachEnds=False):
        first_traversal = TraversalOrder.objects.get(current_id=self.pk)

        previous_traversal = TraversalOrder.objects.get(current_id=first_traversal.previous_id)
        next_traversal = TraversalOrder.objects.get(current_id=last_traversal.next_id)

        previous_traversal.next_id = next_traversal.current_id
        next_traversal.previous_id = previous_traversal.current_id
        previous_traversal.save()
        next_traversal.save()

        if attachEnds:
            # no need to tie up things if we are going to insert the traversal
            # order into new posiiton in next step
            first_traversal.previous_id = last_traversal.current_id
            last_traversal.next_id = first_traversal.current_id
            first_traversal.save()
            last_traversal.save()

    def get_children_ids(self):
        children = Edge.objects.filter(ancestor=self, length=1)
        return [child.id for child in children]

    def get_children(self):
        """
        Return first level children for
        taxon node
        """
        children_ids = [edge.descendant_id for edge in Edge.objects.filter(ancestor=self, length=1)]
        return TaxonNode.objects.filter(pk__in=children_ids)

    def create_edges(self, parent=None):
        if parent:
            self.attach_with_parent(parent)
        edge = Edge(descendant=self, ancestor=self, length=0)
        edge.save()

    def create_traversal_node(self, previous_taxon_id):
        TraversalOrder.create(previous_taxon_id, self.pk)

    def get_one_first_level_taxonnode(self):
        return Edge.objects.filter(ancestor_id=self.tree.root_node).exclude(descendant_id=self.id).filter(length=1)[0].descendant

    def insert_to_traversal_order(self):
        parent_node = self.get_parent()
        if parent_node and not parent_node.is_root_node():
            self.create_traversal_node(parent_node.pk)
        else:
            if self.tree.get_taxon_count() > 1:
                # as this method is called from post_save method, tree always has at least one taxon.
                next_taxon_id = self.get_one_first_level_taxonnode().id
                previous_taxon_id = TraversalOrder.objects.get(current_id=next_taxon_id).previous_id
                self.create_traversal_node(previous_taxon_id)
            else:
                traversal_node = TraversalOrder(
                    current_id=self.pk,
                    next_id=self.pk,
                    previous_id=self.pk,
                )
                traversal_node.save()

    def remove_from_traversal_order(self):
        try:
            TraversalOrder.objects.get(current_id=self.pk).remove()
        except TraversalOrder.DoesNotExist:
            return

    def clean_fields(self, exclude):
        if self.valid_name and self.get_children_ids():
            raise ValidationError({'valid_name': ['Synonym cannot have direct children.']})
        if self.valid_name and not self.synonym_type:
            raise ValidationError({'synonym_type': ['Synonym type is required.']})
        if not self.valid_name and self.synonym_type:
            raise ValidationError({'synonym_type': ['Synonym type can only be used when current name is not selected.']})
        if self.valid_name and not self.parent_described_in:
            raise ValidationError({'parent_described_in': ['Parent originally described in is required.']})
        if not self.valid_name and self.parent_described_in:
            raise ValidationError({'parent_described_in': ['Parent originally described in can only be used when current name is not selected.']})

    def subtree(self):
        # Returns whole subtree of this element excluding all synonyms as they
        # are attached directly to their valid names
        return TaxonNode.objects.filter(child__ancestor_id=self.pk, child__length__gt=0)

    def higher_taxa(self, levels):
        if levels is None:
            higher_taxa_ids = [edge.ancestor_id for edge in Edge.objects.filter(descendant_id=self.pk, length__gt=0)]
        else:
            higher_taxa_ids = [edge.ancestor_id for edge in Edge.objects.filter(descendant_id=self.pk, length__gt=0, length__lte=levels)]
        return TaxonNode.objects.filter(pk__in=higher_taxa_ids).exclude(tree=None)

    @staticmethod
    def taxa_intersection(ids1, ids2):
        return list(set(ids1).intersection(set(ids2)))

    def higher_taxa_intersection(self, given_ids):
        if given_ids:
            ids = given_ids.split(',')
            higher_taxa_ids = [edge.ancestor_id for edge in Edge.objects.filter(descendant_id=self.pk, length__gt=0)]
            for id in ids:
                next_taxon_parent_ids = [edge.ancestor_id for edge in Edge.objects.filter(descendant_id=TaxonNode.objects.get(pk=id), length__gt=0)]
                higher_taxa_ids = TaxonNode.taxa_intersection(higher_taxa_ids, next_taxon_parent_ids)
        else:
            higher_taxa_ids = [edge.ancestor_id for edge in Edge.objects.filter(descendant_id=self.pk, length__gt=0)]
        return TaxonNode.objects.filter(pk__in=higher_taxa_ids).exclude(tree=None)

    def get_related_taxa(self):
        return TaxonNode.objects.filter(taxon_name_concept=self.taxon_name_concept).exclude(id=self.id)

    def get_synonyms(self):
        return TaxonNode.objects.filter(valid_name_id=self.pk)

    def get_hybrid_parents(self):
        hybrid_parents = HybridTaxonNode.objects.filter(taxon_node_id=self.id)
        if hybrid_parents:
            hybrid_parent_ids = [hybrid_parents[0].hybrid_parent1.id, hybrid_parents[0].hybrid_parent2.id]
            return TaxonNode.objects.filter(pk__in=hybrid_parent_ids)
        return []

    def get_next_taxon(self):
        try:
            if self.valid_name:
                valid_taxonnode = TaxonNode.objects.get(pk=self.valid_name.pk)
                traversal_node = TraversalOrder.objects.get(current_id=valid_taxonnode)
            else:
                traversal_node = TraversalOrder.objects.get(current_id=self.id)
            return traversal_node.next
        except TraversalOrder.DoesNotExist:
            return None

    def get_previous_taxon(self):
        try:
            if self.valid_name:
                valid_taxonnode = TaxonNode.objects.get(pk=self.valid_name.pk)
                traversal_node = TraversalOrder.objects.get(current_id=valid_taxonnode)
            else:
                traversal_node = TraversalOrder.objects.get(current_id=self.id)
            return traversal_node.previous
        except TraversalOrder.DoesNotExist:
            return None

    def get_depth(self):
        edges = Edge.objects.filter(descendant_id=self.id)
        # excluding self and root node (for valid names only)
        if self.valid_name:
            return len(edges) - 1
            # return len(edges)
        else:
            return len(edges) - 2

    def get_parent(self):
        try:
            edge = Edge.objects.get(descendant_id=self.id, length=1)
            if edge:
                return edge.ancestor
        except Edge.DoesNotExist:
            return None

    @staticmethod
    def apply_filter(filter, queryset):
        if filter.tree:
            queryset = queryset.filter(tree=filter.tree)
        if filter.lowest_rank:
            queryset = queryset.filter(taxon_rank_id__lte=filter.lowest_rank_id)
        if filter.included_ranks:
            queryset = queryset.filter(taxon_rank_id__in=filter.included_ranks.split(';'))
        if filter.excluded_ranks:
            queryset = queryset.filter(~Q(taxon_rank_id__in=filter.excluded_ranks.split(';')))
        return queryset

    def create_post_created_act(self, remarks, citation_text):
        act = Act(type='new_taxon', taxon_node=self, remarks=remarks, citation_text=citation_text)
        act.save()

    def post_created(self, **kwargs):
        parent = kwargs.pop('parent', None)
        remarks = kwargs.pop('remarks', None)
        citation_text = kwargs.pop('citation_text', None)

        if not parent:
            parent = self.tree.root_node

        taxon_name_concept = TaxonNameConcept()
        taxon_name_concept.save()
        self.taxon_name_concept_id = taxon_name_concept.pk

        self.save()
        if self.valid_name is None:
            self.create_edges(parent=parent)
            self.insert_to_traversal_order()
        self.create_post_created_act(remarks, citation_text)

    def does_exist_in_tree(self):
        return bool(Edge.objects.filter(Q(ancestor_id=self.pk) | Q(descendant_id=self.pk)).count())

    def does_exist_is_traversal_order(self):
        return bool(TraversalOrder.objects.filter(current=self.pk).count())

    def post_changed(self, **kwargs):
        parent = kwargs.pop('parent', None)
        if parent == "":
            # for synonyms empty string might be returned as parent (front)
            parent = None
        remarks = kwargs.pop('remarks', None)
        citation_text = kwargs.pop('citation_text', None)

        if not self.does_exist_in_tree() and self.valid_name is None:
            self.create_edges(parent=parent)

            if not self.does_exist_is_traversal_order():
                self.insert_to_traversal_order()

        if self.has_parent_changed(parent):
            # updating edge list and traversal order
            # new parent must exist
            previous_parent = self.get_parent()
            previous_value = str(previous_parent) if previous_parent else ''
            act = Act(type="change_parent",
                      taxon_node=self,
                      previous_value=previous_value,
                      remarks=remarks,
                      citation_text=citation_text)
            act.save()
            self.set_new_parent(parent)

    def has_parent_changed(self, new_parent):
        if self.get_parent() == self.tree.root_node and new_parent == "":
            # parent was and is current tree root_node
            return False
        return new_parent != self.get_parent()

    def has_changed(self, field_name):
        return self.__dict__[field_name] != self.tracker.previous(field_name)

    def remove_non_self_edges(self):
        for edge in Edge.objects.filter(length__gt=0, descendant_id=self.pk):
            edge.delete()

    def remove_all_edges(self):
        for edge in Edge.objects.filter(Q(descendant_id=self.pk) | Q(ancestor_id=self.pk)):
            edge.delete()

    def transfer_synonyms_to(self, new_valid_name):
        for synonym in self.get_synonyms():
            synonym.valid_name = new_valid_name
            synonym.save()

    def change_current_to_synonym(self, new_valid_name):
        self.transfer_synonyms_to(new_valid_name)
        self.remove_from_traversal_order()

    def can_delete(self):
        is_not_root_node = self.tree is not None
        has_no_subtree = self.subtree().count() == 0
        has_no_synonyms = self.get_synonyms().count() == 0
        return is_not_root_node and has_no_subtree and has_no_synonyms

    def mark_as_deleted(self):
        # make sure that it can be deleted
        self.remove_all_edges()
        self.remove_from_traversal_order()
        CommonName.objects.filter(taxon_node=self).delete()
        # delete hybrid taxon nodes
        self.is_deleted = True
        self.save()
        act = Act(type='delete_taxon', taxon_node=self)
        act.save()


@receiver(pre_save, sender=TaxonNode)
def taxon_node_pre_save(sender, instance, *args, **kwargs):
    if instance.pk:
        try:
            remarks = instance._remarks
            citation_text = instance._citation_text
        except:
            remarks = ''
            citation_text = ''
        if instance.has_changed('epithet') or instance.has_changed('epithet_author'):
            previous_value = instance.tracker.previous('epithet') + ' ' + instance.tracker.previous('epithet_author')
            act = Act(type='edit_name', taxon_node=instance,
                      previous_value=previous_value,
                      remarks=remarks, citation_text=citation_text)
            act.save()

        if instance.has_changed('valid_name_id'):
            if instance.valid_name:
                if instance.tracker.previous('valid_name_id') is None:
                    instance.change_current_to_synonym(instance.valid_name)
                instance.remove_non_self_edges()
            else:
                instance.remove_all_edges()

            taxon_name = TaxonNode.objects.get(pk=instance.tracker.previous('valid_name_id')).taxon_name if instance.tracker.previous('valid_name_id') else ''
            synonym_type = instance.tracker.previous('synonym_type') if instance.tracker.previous('synonym_type') else ''
            previous_value = synonym_type + '__' + taxon_name
            if instance.valid_name:
                act = Act(type=("marked_as_%s" % instance.synonym_type),
                          taxon_node=instance, previous_value=previous_value,
                          remarks=remarks, citation_text=citation_text)
                act.save()
            else:
                act = Act(type="marked_as_current", taxon_node=instance,
                          previous_value=previous_value,
                          remarks=remarks, citation_text=citation_text)
                act.save()
        elif instance.has_changed('synonym_type'):
            taxon_name = instance.tracker.previous('valid_name_id').taxon_name if instance.tracker.previous('valid_name_id') else ''
            synonym_type = instance.tracker.previous('synonym_type') if instance.tracker.previous('synonym_type') else ''
            previous_value = synonym_type + '__' + taxon_name
            act = Act(type=("marked_as_%s" % instance.synonym_type),
                      taxon_node=instance, previous_value=previous_value,
                      remarks=remarks, citation_text=citation_text)
            act.save()

        if instance.has_changed('nomenclatural_status'):
            act = Act(type='change_nomen_status', taxon_node=instance,
                      previous_value=instance.tracker.previous('nomenclatural_status'),
                      remarks=remarks, citation_text=citation_text)
            act.save()


@receiver(post_save, sender=TaxonNode)
def taxon_node_post_save(sender, instance, created, **kwargs):
    if not created:
        previous_concept_id = instance.tracker.previous('taxon_name_concept_id')
        new_concept_id = instance.taxon_name_concept_id
        if previous_concept_id != new_concept_id:
            if new_concept_id is None:
                taxon_name_concept = TaxonNameConcept()
                taxon_name_concept.save()
                instance.taxon_name_concept_id = taxon_name_concept.pk
                instance.save()
            elif TaxonNode.objects.filter(taxon_name_concept_id=previous_concept_id).count() == 0:
                TaxonNameConcept.objects.get(pk=previous_concept_id).delete()

ACT_TYPES = (
            ('new_taxon', _('New taxon node created')),
            ('marked_as_synonym', _('Taxon node was marked as a synonym')),
            ('marked_as_basionym', _('Taxon node was marked as a basionym')),
            ('marked_as_current', _('Taxon node was marked as a current')),
            ('change_parent', _('Taxon node parent was changed')),
            ('edit_name', _('Taxon node name was edited')),
            ('change_nomen_status', _('Taxon node\'s nomenclatural status was changed')),
            ('delete_taxon', _('Taxon node name was deleted')),
)


class Act(models.Model):
    taxon_node = models.ForeignKey(TaxonNode, related_name='acts')
    type = models.CharField(max_length=63, choices=ACT_TYPES)
    previous_value = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    citation_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Edge(models.Model):
    ancestor = models.ForeignKey(TaxonNode, related_name='parent')
    descendant = models.ForeignKey(TaxonNode, related_name='child')
    length = models.IntegerField()


class TraversalOrder(models.Model):
    current = models.ForeignKey(TaxonNode, related_name='current_taxon')
    previous = models.ForeignKey(TaxonNode, related_name='previous_taxon')
    next = models.ForeignKey(TaxonNode, related_name='next_taxon')
    order_type = models.CharField(default='pre', max_length=31)

    @staticmethod
    def create(previous_taxon_id, current_id):
        parent_traversal_node = TraversalOrder.objects.get(current_id=previous_taxon_id)
        if previous_taxon_id != parent_traversal_node.next_id:
            next_traversal_node = TraversalOrder.objects.get(current_id=parent_traversal_node.next_id)
        else:
            next_traversal_node = parent_traversal_node

        new_traversal_node = TraversalOrder(
            current_id=current_id,
            next_id=next_traversal_node.current_id,
            previous_id=parent_traversal_node.current_id,
        )

        parent_traversal_node.next_id = current_id
        next_traversal_node.previous_id = current_id

        new_traversal_node.save()
        parent_traversal_node.save()
        if previous_taxon_id != parent_traversal_node.next_id:
            next_traversal_node.save()

    def remove(self):
        next_traversal_node = TraversalOrder.objects.get(current_id=self.next)
        previous_traversal_node = TraversalOrder.objects.get(current_id=self.previous)

        next_traversal_node.previous = previous_traversal_node.current
        next_traversal_node.save()

        previous_traversal_node.next = next_traversal_node.current
        previous_traversal_node.save()

        self.delete()


class CommonName(models.Model):
    taxon_node = models.ForeignKey(TaxonNode, null=True, related_name='vernacular_names')
    iso_639 = models.ForeignKey(Language, help_text='Language')
    common_name = models.CharField(max_length=255)
    is_preferred = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s" % (self.common_name)

    @property
    def rank(self):
        """ Returns taxon rank name (used in autocomplete searches)
        """
        taxonnode_object = TaxonNode.objects.get(pk=self.taxon_node_id)
        if taxonnode_object:
            rank = TaxonRank.objects.get(pk=taxonnode_object.taxon_rank_id)
            return rank.abbreviation.lower()
        return []


class HybridTaxonNode(models.Model):
    taxon_node = models.ForeignKey(TaxonNode)
    hybrid_parent1 = models.ForeignKey(TaxonNode, related_name='hybrid_parent_1')
    hybrid_parent2 = models.ForeignKey(TaxonNode, related_name='hybrid_parent_2')

    def __unicode__(self):
        return self.hybrid_parent1.taxon_name + ' x ' + self.hybrid_parent2.taxon_name


class Filter(models.Model):
    locale = models.ForeignKey(Language, help_text='Language', null=True, blank=True)
    lowest_rank = models.ForeignKey(TaxonRank, related_name='minimum_rank', null=True, blank=True)
    included_ranks = models.TextField(blank=True, null=True)
    excluded_ranks = models.TextField(blank=True, null=True)
    tree = models.ForeignKey(Tree, blank=True, null=True)
