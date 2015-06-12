from apps.taxonomy.models import SubtreeHelper, TraversalOrder
from apps.taxonomy.tests.base import TaxonomyBaseTestMixin


class TestChangingParentUpdatesTraversalOrder(TaxonomyBaseTestMixin):

    def test_finding_last_traversal_node(self):
        taxonnode = self.TAXON_NODE_LIST[2]
        last_traversal = SubtreeHelper.find_last_traversal_node(taxonnode)
        self.assertEqual(last_traversal.current_id, self.TAXON_NODE_LIST[4].id)

    def test_finding_last_traversal_node_when_whole_tree_given(self):
        taxonnode = self.TAXON_NODE_LIST[1]
        last_traversal = SubtreeHelper.find_last_traversal_node(taxonnode)
        self.assertEqual(last_traversal.current_id, self.TAXON_NODE_LIST[6].id)

    def test_remove_subtree_from_traversal_order(self):
        taxonnode = self.TAXON_NODE_LIST[2]
        last_traversal = SubtreeHelper.find_last_traversal_node(taxonnode)
        self.assertEqual(SubtreeHelper.find_last_traversal_node(taxonnode).next_id, self.TAXON_NODE_LIST[5].id)
        taxonnode.remove_subtree_from_traversal_order(last_traversal, True)
        self.assertEqual(SubtreeHelper.find_last_traversal_node(taxonnode).next_id, self.TAXON_NODE_LIST[2].id)

    def test_add_subtree_to_traversal_order(self):
        taxonnode = self.TAXON_NODE_LIST[2]
        new_parent = self.TAXON_NODE_LIST[6]
        last_traversal = SubtreeHelper.find_last_traversal_node(taxonnode)
        taxonnode.remove_subtree_from_traversal_order(last_traversal)
        taxonnode.add_subtree_to_traversal_order(new_parent, last_traversal)

        self.assertEqual(TraversalOrder.objects.get(current_id=self.TAXON_NODE_LIST[6].id).next_id, self.TAXON_NODE_LIST[2].id)
        self.assertEqual(TraversalOrder.objects.get(current_id=self.TAXON_NODE_LIST[2].id).previous_id, self.TAXON_NODE_LIST[6].id)
        self.assertEqual(TraversalOrder.objects.get(current_id=self.TAXON_NODE_LIST[1].id).next_id, self.TAXON_NODE_LIST[5].id)
        self.assertEqual(TraversalOrder.objects.get(current_id=self.TAXON_NODE_LIST[5].id).previous_id, self.TAXON_NODE_LIST[1].id)
        self.assertEqual(TraversalOrder.objects.get(current_id=self.TAXON_NODE_LIST[1].id).previous_id, self.TAXON_NODE_LIST[4].id)
        self.assertEqual(TraversalOrder.objects.get(current_id=self.TAXON_NODE_LIST[4].id).next_id, self.TAXON_NODE_LIST[1].id)
