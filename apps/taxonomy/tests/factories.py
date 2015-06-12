import factory

from apps.taxonomy import models


class LanguageFactory(factory.django.DjangoModelFactory):
    iso_639 = 'est'
    name = 'estonian'

    class Meta:
        model = models.Language


class TaxonRankFactory(factory.django.DjangoModelFactory):
    abbreviation = 'kgd'
    zoology_rank = 'kgd'
    botany_rank = 'kgd'
    bacteria_rank = 'kgd'
    prefix = 'kgd'
    suffix = 'kgd'

    class Meta:
        model = models.TaxonRank


class TreeFactory(factory.django.DjangoModelFactory):
    name = 'Tree 1'
    origin_tree = None
    root_node = None  # factory.SubFactory(TaxonNodeFactory)

    class Meta:
        model = models.Tree


class TaxonNameConceptFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.TaxonNameConcept


class TaxonNodeFactory(factory.django.DjangoModelFactory):
    tree = factory.SubFactory(TreeFactory)
    epithet = 'kingdom'
    parent_described_in = None
    valid_name = None
    taxon_rank = factory.SubFactory(TaxonRankFactory)
    taxon_name_concept = None
    epithet_author = 'author'
    is_fossil = False

    class Meta:
        model = models.TaxonNode


class ActFactory(factory.django.DjangoModelFactory):
    taxon_node = factory.SubFactory(TaxonNodeFactory)
    type = 'new_taxon'

    class Meta:
        model = models.Act


class EdgeFactory(factory.django.DjangoModelFactory):
    ancestor = factory.SubFactory(TaxonNodeFactory)
    descendant = factory.SubFactory(TaxonNodeFactory)
    length = 1

    class Meta:
        model = models.Edge


class TraversalOrderFactory(factory.django.DjangoModelFactory):
    current = factory.SubFactory(TaxonNodeFactory)
    previous = factory.SubFactory(TaxonNodeFactory)
    next = factory.SubFactory(TaxonNodeFactory)
    order_type = 'pre'

    class Meta:
        model = models.TraversalOrder


class CommonNameFactory(factory.django.DjangoModelFactory):
    taxon_node = factory.SubFactory(TaxonNodeFactory)
    iso_639 = factory.SubFactory(LanguageFactory)
    common_name = "Common Kingdom"

    class Meta:
        model = models.CommonName


class HybridTaxonNodeFactory(factory.django.DjangoModelFactory):
    taxon_node = factory.SubFactory(TaxonNodeFactory)
    hybrid_parent1 = factory.SubFactory(TaxonNodeFactory)
    hybrid_parent2 = factory.SubFactory(TaxonNodeFactory)

    class Meta:
        model = models.HybridTaxonNode


class FilterFactory(factory.django.DjangoModelFactory):
    locale = factory.SubFactory(LanguageFactory)
    lowest_rank = factory.SubFactory(TaxonRankFactory)

    class Meta:
        model = models.Filter
