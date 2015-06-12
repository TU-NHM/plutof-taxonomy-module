from apps.taxonomy.serializers.taxon_rank import TaxonRankSerializer
from apps.taxonomy.models import TaxonRank
from rest_framework import viewsets


class TaxonRankView(viewsets.ReadOnlyModelViewSet):
    queryset = TaxonRank.objects.all()
    serializer_class = TaxonRankSerializer
