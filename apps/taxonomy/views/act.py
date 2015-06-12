import django_filters

from apps.taxonomy.serializers.act import ActSerializer
from apps.taxonomy.models import Act
from rest_framework import viewsets


class ActFilter(django_filters.FilterSet):
    min_datetime = django_filters.DateTimeFilter(name="created_at", lookup_type='gte')
    max_datetime = django_filters.DateTimeFilter(name="created_at", lookup_type='lte')
    tree = django_filters.NumberFilter(name="taxon_node__tree_id", lookup_type='exact')

    class Meta:
        model = Act
        fields = ['type', 'taxon_node', 'min_datetime', 'max_datetime', 'tree']


class ActView(viewsets.ReadOnlyModelViewSet):
    queryset = Act.objects.all().order_by('id')
    serializer_class = ActSerializer
    filter_class = ActFilter
