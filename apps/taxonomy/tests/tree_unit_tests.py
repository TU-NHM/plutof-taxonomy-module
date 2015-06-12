from apps.taxonomy.models import TaxonNode, Edge
from apps.taxonomy.tests.base import TaxonomyBaseTestMixin
from apps.taxonomy.tests.factories import TreeFactory, TaxonNameConceptFactory


class TestCloneTreeStartingFromTaxonNode(TaxonomyBaseTestMixin):

    def test_creating_new_tree_creates_root_node(self):
        tree = TreeFactory()
        self.assertEqual(TaxonNode.objects.get(id=tree.root_node.id).tree, None)

    def test_cloning(self):
        tree = self.TAXON_NODE_LIST[1].tree
        for i in range(7):
            self.TAXON_NODE_LIST[i].taxon_name_concept = TaxonNameConceptFactory()
            self.TAXON_NODE_LIST[i].save()

        # def test_connecting_new_root_node_with_previous_starting_node(self):
        new_tree = TreeFactory(name="New tree")
        new_tree.clone_starting_from_taxon_node(tree.root_node)
        self.assertEqual(new_tree.root_node.taxon_name_concept, tree.root_node.taxon_name_concept)

        # def test_clone_each_taxon_node(self):
        self.assertEqual(tree.get_taxon_count(), new_tree.get_taxon_count())

        # def test_connect_nodes_with_parents(self):
        self.assertEqual(Edge.objects.filter(ancestor=new_tree.root_node).count(), 7)

        # def test_each_clone_gets_edge_to_self(self):
        new_node = self.TAXON_NODE_LIST[3].get_related_taxa()[0]
        self.assertEqual(Edge.objects.filter(ancestor=new_node, length=0).count(), 1)
        self.assertEqual(Edge.objects.filter(descendant=new_node).count(), 4)

        # def test_cloning_synonym_with_valid_name(self):
        self.assertEqual(len(self.TAXON_NODE_LIST[7].get_related_taxa()), 1)

        # def test_connecting_synonym_with_valid_name_in_edgelist(self):
        synonym = self.TAXON_NODE_LIST[7].get_related_taxa()[0]
        self.assertEqual(Edge.objects.filter(descendant=synonym).count(), 1)

        # def test_generating_traversal_order(self):
        old_node = self.TAXON_NODE_LIST[3]
        new_node = old_node.get_related_taxa()[0]
        self.assertEqual(old_node.get_next_taxon().taxon_name_concept, new_node.get_next_taxon().taxon_name_concept)
