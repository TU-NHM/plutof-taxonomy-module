import json
import re

from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.taxonomy.models import Filter, CommonName


class VernacularNameListField(serializers.WritableField):

    def field_to_native(self, taxon_node, field_name):
        # TODO:
        #   Check rest_framework, if it has a method that takes a
        #   list of objects and returns a list of urls.
        if taxon_node:
            vernacular_names = CommonName.objects.filter(taxon_node=taxon_node).order_by('id')
            try:
                filter_id = self.context['request'].GET.get('filter', None)
                if filter_id:
                    filter = Filter.objects.get(pk=filter_id)
                    if filter.locale:
                        vernacular_names = vernacular_names.filter(iso_639=filter.locale)
            except:
                pass

            vernacular_names_list = []
            for vernacular_name in vernacular_names:
                vernacular_names_list.append(reverse('commonname-detail', args=[vernacular_name.id], request=self.context['request']))
            return vernacular_names_list

    def from_native(self, vernacular_names):
        if vernacular_names:
            taxon_node = self.parent.object
            vernacular_names = re.sub(r"'", "\"", vernacular_names)
            vernacular_names = json.loads('{ "list": %s}' % vernacular_names)['list']
            for obj in vernacular_names:
                try:
                    field = serializers.HyperlinkedRelatedField(view_name='commonname-detail', queryset=CommonName.objects.all(), source=self)
                    vernacular_name = field.from_native(obj)
                    vernacular_name.taxon_node = taxon_node
                    vernacular_name.save()
                except:
                    raise serializers.ValidationError("Invalid data")
            return None
