import ast
from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.taxonomy.models import TaxonRank


class TaxonRankListField(serializers.WritableField):

    def to_native(self, ranks):
        if ranks:
            rank_list = []
            for rank_id in ranks.split(';'):
                try:
                    rank = TaxonRank.objects.get(pk=rank_id)
                except (TaxonRank.DoesNotExist, ValueError):
                    continue
                rank_list.append(reverse('taxonrank-detail', args=[rank.id], request=self.context['request']))
            return rank_list

    def from_native(self, ranks):
        if ranks:
            rank_list = []
            # this check is for api form since in the form a list can not be entered in char field
            if type(ranks) is unicode:
                try:
                    ranks = ast.literal_eval(ranks)
                except (ValueError, SyntaxError):
                    raise serializers.ValidationError("Field contains invalid data")
            for obj in ranks:
                if (hasattr(obj, "isdigit") and obj.isdigit()) or (type(obj) is int):
                    obj = reverse('taxonrank-detail', args=[int(obj)])
                try:
                    # gets the tanxonrank object. can be done in a more shorter way than initializing a field (for performance)?
                    field = serializers.HyperlinkedRelatedField(view_name='taxonrank-detail', queryset=TaxonRank.objects.all(), source=self)
                    rank = field.from_native(obj)
                    rank_list.append(unicode(rank.pk))
                except:
                    raise serializers.ValidationError("Element in list refers to a rank that does not exist")
            return ";".join(rank_list)
