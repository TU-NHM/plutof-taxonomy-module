from django.core.management.base import BaseCommand
from apps.taxonomy.models import Edge, TraversalOrder, Tree


class Command(BaseCommand):
    args = '<tree_id>'
    help = 'Populates an empty TraversalOrder table with all trees when no args are given. Possible to create traversal order for a specific tree.'

    node_id_list = []
    """
    Preparations for creating traversal orders.
    One single node must be given whose children will be
    recurssively traversed and put into db
    """
    def prepare_traversal_creation(self, node_id):
        # exclude non-current taxonnodes
        children = Edge.objects.filter(ancestor_id=node_id, length=1).filter(descendant_id__valid_name=None)

        self.node_id_list = [child.descendant_id for child in children]
        self.node_id_list.reverse()
        initial_node = TraversalOrder(current_id=node_id, next_id=node_id, previous_id=node_id)
        initial_node.save()
        return initial_node

    """
    For creating traversal orders list must contain one single node that
    is the same node as args for this method. Also last_node must be the
    same node
    """
    def create_traversal_order(self, node_id, previous, next):
        traversal_node = TraversalOrder(current_id=node_id, previous_id=previous.current_id, next_id=previous.next_id)
        traversal_node.save()
        # update next nodes previous value
        next.previous_id = node_id
        next.save()
        # update previous nodes next value
        previous.next_id = node_id
        previous.save()

        # exclude non-current taxonnodes
        children = Edge.objects.filter(ancestor_id=node_id, length=1).filter(descendant_id__valid_name=None)

        if children.count() > 0:
            # => this cmd does not reverse the list of objects, should be list of ids instead
            children_ids = [child.descendant_id for child in children]
            children_ids.reverse()
            self.node_id_list = self.node_id_list + children_ids

        return traversal_node

    def handle(self, *args, **options):
        if len(args):
            trees = Tree.objects.filter(pk=args[0])
            can_proceed = True
        else:
            can_proceed = len(TraversalOrder.objects.all()) == 0
            trees = Tree.objects.all()

        if can_proceed:
            for tree in trees:
                # exclude non-current taxonnodes
                first_level_edges = Edge.objects.filter(ancestor_id=tree.root_node_id, length=1).filter(descendant_id__valid_name=None)
                all_edges = Edge.objects.filter(ancestor_id=tree.root_node_id, length__gte=1).filter(descendant_id__valid_name=None)
                """
                Check if only first level edges are added/cloned. In this case
                go through root children list to create rounded traversal order
                """
                if first_level_edges.count() == all_edges.count():
                    root_children_ids = [edge.descendant_id for edge in first_level_edges]
                    root_children_ids.reverse()
                    if len(root_children_ids):
                        first_taxon_id = root_children_ids.pop()
                        first_taxon_traversal_node = self.prepare_traversal_creation(first_taxon_id)
                        traversal_node = first_taxon_traversal_node

                        while root_children_ids:
                            traversal_node = self.create_traversal_order(root_children_ids.pop(), traversal_node, first_taxon_traversal_node)
                else:
                    for first_level_edge in first_level_edges:
                        higher_level_taxon_id = first_level_edge.descendant_id
                        higher_level_taxon_traversal_node = self.prepare_traversal_creation(higher_level_taxon_id)
                        if len(self.node_id_list):
                            traversal_node = self.create_traversal_order(self.node_id_list.pop(), previous=higher_level_taxon_traversal_node, next=higher_level_taxon_traversal_node)

                            while self.node_id_list:
                                traversal_node = self.create_traversal_order(self.node_id_list.pop(), traversal_node, higher_level_taxon_traversal_node)
