from rest_framework import serializers

from apps.taxonomy.models import TaxonNameConcept


class TaxonNameConceptField(serializers.WritableField):

    def field_to_native(self, common_name, field_name):
        if common_name and common_name.taxon_name_concept:
            taxon_name_concept = TaxonNameConcept.objects.get(pk=common_name.taxon_name_concept)
            field = serializers.HyperlinkedRelatedField(view_name='taxonnode-detail')
            return field.get_url(obj=taxon_name_concept, view_name='taxonnode-detail', request=self.context.get('request', None), format=None)

    def from_native(self, taxon_url):
        if taxon_url:
            try:
                field = serializers.HyperlinkedRelatedField(view_name='taxonnode-detail', queryset=TaxonNameConcept.objects.all(), source=self)
                return field.from_native(taxon_url).pk
            except:
                raise serializers.ValidationError("'%s' is not a valid url" % taxon_url)
        return None
