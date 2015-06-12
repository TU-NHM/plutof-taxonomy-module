from apps.taxonomy.serializers.hybrid_taxon_node import HybridTaxonNodeSerializer
from apps.taxonomy.models import HybridTaxonNode
from rest_framework import viewsets


class HybridTaxonNodeView(viewsets.ModelViewSet):
    queryset = HybridTaxonNode.objects.all()
    serializer_class = HybridTaxonNodeSerializer

    filter_fields = ['taxon_node', ]
