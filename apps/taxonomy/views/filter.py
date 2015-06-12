from apps.taxonomy.serializers.filter import FilterSerializer
from apps.taxonomy.models import Filter
from rest_framework import viewsets


class FilterView(viewsets.ModelViewSet):
    """
    Included ranks and Excluded ranks must be a list that can be formed of:
    1) links to taxon rank objects,
    2) ids as int, or
    3) str of taxon ranks.
    E.g: ["http://taxonomyplutof.ut.ee/api/v1/taxonomy/taxonranks/10/","10",10]
    """
    queryset = Filter.objects.all()
    serializer_class = FilterSerializer
