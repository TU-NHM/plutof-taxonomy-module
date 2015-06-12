from apps.taxonomy.serializers.vernacular_name import VernacularNameSerializer
from apps.taxonomy.models import CommonName
from rest_framework import viewsets


class VernacularNameView(viewsets.ModelViewSet):
    queryset = CommonName.objects.all()
    serializer_class = VernacularNameSerializer

    filter_fields = ['taxon_node', ]
