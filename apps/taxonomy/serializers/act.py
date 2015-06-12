from apps.taxonomy.models import Act
from rest_framework import serializers


class ActSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Act
        fields = [
            'id', 'url', 'taxon_node', 'type', 'previous_value',
            'remarks', 'citation_text', 'created_at'
        ]
