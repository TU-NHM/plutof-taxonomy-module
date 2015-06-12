# DRF
from rest_framework import viewsets, renderers, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
# Misc
from apps.taxonomy.serializers.taxon import TaxonSerializer
from apps.taxonomy.models import TaxonNode, Filter
from apps.taxonomy.fields.taxon_parent_field import TaxonParentField


class TaxonView(viewsets.ModelViewSet):
    queryset = TaxonNode.objects.exclude(tree_id=None).order_by('id')
    serializer_class = TaxonSerializer

    filter_fields = ['tree', ]

    def apply_filter(self, queryset):
        filter_id = self.request.QUERY_PARAMS.get('filter', None)
        if filter_id:
            try:
                filter_obj = Filter.objects.get(id=filter_id)
            except Filter.ObjectDoesNotExist:
                return TaxonNode.objects.none()
            return TaxonNode.apply_filter(filter_obj, queryset)
        return queryset.order_by('id')

    def get_paginated_serializer(self, request, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return serializer

    def paginate_queryset(self, queryset, *args, **kwargs):
        queryset = self.apply_filter(queryset)
        return super(TaxonView, self).paginate_queryset(queryset, *args, **kwargs)

    @detail_route(renderer_classes=[renderers.UnicodeJSONRenderer, renderers.BrowsableAPIRenderer])
    def subtree(self, request, *args, **kwargs):
        taxon = self.get_object()
        queryset = taxon.subtree()
        serializer = self.get_paginated_serializer(request, queryset)
        return Response(serializer.data)

    @detail_route(renderer_classes=[renderers.UnicodeJSONRenderer, renderers.BrowsableAPIRenderer])
    def higher_taxa(self, request, *args, **kwargs):
        taxon = self.get_object()
        levels = request.GET.get('levels', None)
        queryset = taxon.higher_taxa(levels)
        serializer = self.get_paginated_serializer(request, queryset)
        return Response(serializer.data)

    @detail_route(renderer_classes=[renderers.UnicodeJSONRenderer, renderers.BrowsableAPIRenderer])
    def higher_taxa_intersection(self, request, *args, **kwargs):
        taxon = self.get_object()
        given_ids = request.GET.get('given_ids', None)
        queryset = taxon.higher_taxa_intersection(given_ids)
        serializer = self.get_paginated_serializer(request, queryset)
        return Response(serializer.data)

    @detail_route(renderer_classes=[renderers.UnicodeJSONRenderer, renderers.BrowsableAPIRenderer])
    def direct_children(self, request, *args, **kwargs):
        taxon = self.get_object()
        queryset = taxon.get_children()
        serializer = self.get_paginated_serializer(request, queryset)
        return Response(serializer.data)

    def post_save(self, taxon_node, created):
        parent_url = self.request.DATA.get('parent')
        remarks = self.request.DATA.get('remarks', '')
        citation_text = self.request.DATA.get('citation_text', '')

        field = TaxonParentField()
        parent = field.from_native(parent_url)

        if created:
            taxon_node.post_created(parent=parent, remarks=remarks, citation_text=citation_text)
        else:
            taxon_node.post_changed(parent=parent, remarks=remarks, citation_text=citation_text)
        super(TaxonView, self).post_save(taxon_node)

    def pre_save(self, obj):
        obj._remarks = self.request.DATA.get('remarks', '')
        obj._citation_text = self.request.DATA.get('citation_text', '')
        if self.request.DATA.get('valid_name'):
            self.request.DATA['parent'] = ""
        super(TaxonView, self).pre_save(obj)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.can_delete():
            obj.mark_as_deleted()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # return an error that this objet cannot be deleted
            return Response({'Error': 'This taxon cannot be deleted'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
