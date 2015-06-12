from apps.taxonomy.serializers.language import LanguageSerializer
from apps.taxonomy.models import Language
from rest_framework import viewsets


class LanguageView(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
