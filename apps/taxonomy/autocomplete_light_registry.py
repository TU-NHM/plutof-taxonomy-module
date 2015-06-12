import autocomplete_light

from apps.taxonomy.models import TaxonNode, TaxonNameConcept, Tree, TaxonRank
from taxonomy.autocomplete_light_base import BaseAutocomplete


class TaxonNodeAutocomplete(BaseAutocomplete):
    search_fields = ['^epithet']
    permission = 'change_taxonnode'
    attrs = {'placeholder': 'TaxonNode epithet'}


class TaxonNameConceptAutocomplete(BaseAutocomplete):
    search_fields = ['=id']
    attrs = {'placeholder': 'TaxonNameConcept', 'data-autocomplete-minimum-characters': 1}


class TreeAutocomplete(BaseAutocomplete):
    search_fields = ['^name']
    attrs = {'placeholder': 'Tree name'}


class TaxonRankAutocomplete(BaseAutocomplete):
    search_fields = ['^abbreviation']
    attrs = {'placeholder': 'Abbreviation'}


autocomplete_light.register(TaxonNode, TaxonNodeAutocomplete)
autocomplete_light.register(TaxonNameConcept, TaxonNameConceptAutocomplete)
autocomplete_light.register(Tree, TreeAutocomplete)
autocomplete_light.register(TaxonRank, TaxonRankAutocomplete)
