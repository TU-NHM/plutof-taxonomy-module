import mock

from apps.taxonomy.models import TaxonNode, Edge, TraversalOrder
from apps.taxonomy.tests.base import TaxonomyBaseTestMixin
from apps.taxonomy.tests.factories import TreeFactory, TaxonNodeFactory


class TestChangingParentUpdatesEdgeList(TaxonomyBaseTestMixin):

    def test_has_parent_changed(self):
        taxonnode = self.TAXON_NODE_LIST[1]
        new_parent = ""
        self.assertFalse(taxonnode.has_parent_changed(new_parent))
        taxonnode = self.TAXON_NODE_LIST[2]
        self.assertTrue(taxonnode.has_parent_changed(new_parent))

    def test_adding_node_to_only_first_level_node(self):
        tree = TreeFactory()
        taxonnode = TaxonNodeFactory(tree=tree, epithet='epithet')
        node_order = TraversalOrder(next=taxonnode, previous=taxonnode, current=taxonnode)
        node_order.save()
        new_taxonnode = TaxonNodeFactory(tree=tree, epithet='new_epithet')
        TraversalOrder.create(taxonnode.pk, new_taxonnode.pk)
        initial_order = TraversalOrder.objects.get(current_id=taxonnode.pk)
        self.assertEqual(initial_order.next_id, new_taxonnode.pk)
        self.assertEqual(initial_order.previous_id, new_taxonnode.pk)

    @mock.patch('apps.taxonomy.models.TaxonNode.detach_subtree_from_tree', mock.Mock())
    def test_change_parent_detaches_selected_node_with_subtree_from_tree(self):
        taxonnode = self.TAXON_NODE_LIST[4]
        new_parent = self.TAXON_NODE_LIST[5]
        taxonnode.set_new_parent(new_parent)
        TaxonNode.detach_subtree_from_tree.assert_called_once_with()

    def test_detaching_leaf_node_from_tree_removes_all_higher_edges(self):
        taxonnode = self.TAXON_NODE_LIST[4]
        taxonnode.detach_subtree_from_tree()
        self.assertEqual(Edge.objects.filter(descendant=taxonnode).count(), 1)

    def test_detaching_subtree_from_tree_removes_all_higher_edges(self):
        taxonnode = self.TAXON_NODE_LIST[2]
        taxonnode.detach_subtree_from_tree()
        self.assertEqual(Edge.objects.filter(descendant=taxonnode).count(), 1)
        self.assertEqual(Edge.objects.filter(ancestor=taxonnode).count(), 3)

    def test_detaching_subtree_removes_all_edges_outside_of_subtree(self):
        taxonnode = self.TAXON_NODE_LIST[2]
        taxonnode.detach_subtree_from_tree()
        self.assertEqual(Edge.objects.filter(descendant=self.TAXON_NODE_LIST[3]).count(), 2)

    def test_detaching_subtree_does_not_affect_synonym_edges(self):
        taxonnode = self.TAXON_NODE_LIST[5]
        taxonnode.detach_subtree_from_tree()
        self.assertEqual(Edge.objects.filter(descendant=self.TAXON_NODE_LIST[6]).count(), 2)
        self.assertEqual(Edge.objects.filter(descendant=self.TAXON_NODE_LIST[7]).count(), 1)

    @mock.patch('apps.taxonomy.models.TaxonNode.attach_subtree_with_parent', mock.Mock())
    def test_change_parent_attaches_subtree_with_new_parent(self):
        taxonnode = self.TAXON_NODE_LIST[4]
        new_parent = self.TAXON_NODE_LIST[5]
        taxonnode.set_new_parent(new_parent)
        TaxonNode.attach_subtree_with_parent.assert_called_once_with(new_parent)

    def test_attaching_leaf_node_with_parent_adds_edges(self):
        taxonnode = self.TAXON_NODE_LIST[4]
        new_parent = self.TAXON_NODE_LIST[5]
        taxonnode.detach_subtree_from_tree()
        taxonnode.attach_subtree_with_parent(new_parent)
        self.assertEqual(Edge.objects.filter(descendant=taxonnode).count(), 4)

    def test_attaching_subtree_with_parent_adds_edges(self):
        taxonnode = self.TAXON_NODE_LIST[2]
        new_parent = self.TAXON_NODE_LIST[5]
        taxonnode.set_new_parent(new_parent)
        self.assertEqual(Edge.objects.filter(descendant=self.TAXON_NODE_LIST[3]).count(), 5)

    def test_attaching_subtree_with_no_parent_adds_edges_with_root_node(self):
        taxonnode = self.TAXON_NODE_LIST[2]
        taxonnode.set_new_parent(None)
        self.assertEqual(Edge.objects.filter(descendant=self.TAXON_NODE_LIST[3]).count(), 3)

    def test_attaching_subtree_with_parent_does_not_change_synonym_edges(self):
        taxonnode = self.TAXON_NODE_LIST[5]
        new_parent = self.TAXON_NODE_LIST[2]
        taxonnode.set_new_parent(new_parent)
        self.assertEqual(Edge.objects.filter(descendant=self.TAXON_NODE_LIST[7]).count(), 1)

    def test_attaching_leaf_node_with_synonyms_does_not_change_synonym_edges(self):
        taxonnode = self.TAXON_NODE_LIST[6]
        new_parent = self.TAXON_NODE_LIST[2]
        taxonnode.set_new_parent(new_parent)
        self.assertEqual(Edge.objects.filter(descendant=self.TAXON_NODE_LIST[7]).count(), 1)
