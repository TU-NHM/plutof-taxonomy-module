from apps.taxonomy.models import Language
from rest_framework import serializers


class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Language
        fields = [
            'iso_639', 'url', 'name'
        ]
