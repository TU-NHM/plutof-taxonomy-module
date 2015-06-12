from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import viewsets, renderers
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status

from apps.taxonomy.models import Tree, TaxonNode
from apps.taxonomy.serializers.tree import TreeSerializer
from apps.taxonomy.serializers.taxon import TaxonSerializer


class TreeView(viewsets.ModelViewSet):
    """ Limit for taxon names allowed on cloned subtree is set to 5000.
    You will get a warning message when trying to clone larger trees.
    """
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer

    def native_to_object(self, model, native_data):
        if (hasattr(native_data, "isdigit") and native_data.isdigit()) or (type(native_data) is int):
            object_id = native_data
        elif hasattr(native_data, "split"):
            object_id = native_data.split('/')[-2]
        else:
            return None
        try:
            return model.objects.get(id=object_id)
        except model.DoesNotExist:
            return None

    def pre_save(self, tree, *args, **kwargs):
        initial_tree = self.request.DATA.get('origin_tree', None)
        root_node = self.native_to_object(TaxonNode, self.request.DATA.get('root_node', None))
        if initial_tree:
            initial_tree = self.native_to_object(Tree, initial_tree)
        elif (not initial_tree) and root_node:
            initial_tree = root_node.tree
        if root_node:
            if not (root_node.tree == initial_tree):
                """ root_node does not belong to the given tree,
                use root_node's tree as origin tree instead
                """
                tree.origin_tree = root_node.tree
            else:
                tree.origin_tree = initial_tree
        super(TreeView, self).pre_save(tree, *args, **kwargs)

    @detail_route(renderer_classes=[renderers.UnicodeJSONRenderer, renderers.BrowsableAPIRenderer])
    def root_children(self, request, *args, **kwargs):
        tree = self.get_object()
        queryset = tree.get_root_children()
        paginator = Paginator(queryset, self.paginate_by)
        page = request.QUERY_PARAMS.get('page')
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaxonSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
