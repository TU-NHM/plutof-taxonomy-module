from django.core.management.base import BaseCommand, CommandError
from apps.taxonomy.models import TaxonNode, Edge, Tree


class Command(BaseCommand):
    args = '<tree_id tree_id ...>'
    help = 'Populates closure table with given tree nodes. Supports multiple trees.'

    node_id_list = []
    all_tree_edges = []
    initial_query = None

    """
    def prepare_edge_list_creation(self, node_id):
        children = self.initial_query.filter(parent_taxon_node=node_id)
        self.node_id_list = [child.id for child in children]
        if node_id in self.all_tree_edges:
            return Edge.objects.get(ancestor_id=node_id, descendant_id=node_id, length=0)
        initial_edge = Edge(ancestor_id=node_id, descendant_id=node_id, length=0)
        initial_edge.save()
        return initial_edge

    def connect_with_parents(self, node_id, parent_edge):
        parent_edges = Edge.objects.filter(descendant_id=parent_edge.descendant_id)
        for parent_edge in parent_edges:
            edge = Edge(ancestor_id=parent_edge.ancestor_id, descendant_id=node_id, length=parent_edge.length + 1)
            edge.save()

    def create_edge(self, node_id):
        taxon_node = TaxonNode.objects.get(pk=node_id)
        parent_edge = Edge.objects.get(descendant_id=taxon_node.parent_taxon_node_id, length=0)

        if not node_id in self.all_tree_edges:
            self_edge = Edge(ancestor_id=node_id, descendant_id=node_id, length=0)
            self_edge.save()
            self.connect_with_parents(node_id, parent_edge)

        children = self.initial_query.filter(parent_taxon_node_id=node_id)
        if children.count() > 0:
            self.node_id_list = self.node_id_list + [child.id for child in children]
    """
    # Before this command Edge list must be populated
    def handle(self, *args, **options):
        for tree_id in args:
            try:
                tree = Tree.objects.get(pk=int(tree_id))
            except Tree.DoesNotExist:
                raise CommandError('Tree "%s" does not exist')

            root_node = tree.root_node

            root_edge = Edge(ancestor_id=root_node.pk, descendant_id=root_node.pk, length=0)
            root_edge.save()

            self.initial_query = TaxonNode.objects.filter(tree_id=tree_id).filter(valid_name=None)
            for taxon_node in self.initial_query:
                try:
                    longest_edge = Edge.objects.filter(descendant_id=taxon_node.pk).order_by('-length').first().length
                    new_edge = Edge(ancestor_id=root_node.pk, descendant_id=taxon_node.pk, length=longest_edge + 1)
                    new_edge.save()
                except:
                    # print out error message
                    print "No edges for " + str(taxon_node.pk)

            """
            # for writing every edge only once
            self.all_tree_edges = [edge.descendant_id for edge in Edge.objects.filter(Q(descendant__tree_id=tree_id, length=0) | Q(descendant_id=root_node.pk, length=0))]

            self.prepare_edge_list_creation(root_node.pk)

            while self.node_id_list:
                self.create_edge(self.node_id_list.pop())
            """
