from apps.taxonomy.serializers.taxon_name_concept import TaxonNameConceptSerializer
from apps.taxonomy.models import TaxonNameConcept
from rest_framework import viewsets


class TaxonNameConceptView(viewsets.ReadOnlyModelViewSet):
    queryset = TaxonNameConcept.objects.all()
    serializer_class = TaxonNameConceptSerializer
