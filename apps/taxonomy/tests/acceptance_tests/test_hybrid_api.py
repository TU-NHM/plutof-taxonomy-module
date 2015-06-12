from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.taxonomy.tests.base import TaxonomyUnauthorizedTestMixin, TaxonomyUserTestMixin, TaxonomyAdminTestMixin
from apps.taxonomy.tests.factories import HybridTaxonNodeFactory, TaxonNodeFactory, TreeFactory


class HybridTaxonNodeBase(APITestCase):

    def get_obj_url(self):
        obj = HybridTaxonNodeFactory()
        return reverse('hybridtaxonnode-detail', args=[obj.id]), obj

    @staticmethod
    def get_url():
        return reverse('hybridtaxonnode-list')

    def get_raw_data(self):
        data = {"taxon_node": reverse('taxonnode-detail', args=[TaxonNodeFactory(tree=TreeFactory()).id]),
                "hybrid_parent1": reverse('taxonnode-detail', args=[TaxonNodeFactory(tree=TreeFactory()).id]),
                "hybrid_parent2": reverse('taxonnode-detail', args=[TaxonNodeFactory(tree=TreeFactory()).id])}
        return data


class TestHybridTaxonNodeUnauthorized(TaxonomyUnauthorizedTestMixin, HybridTaxonNodeBase):
    pass


class TestHybridTaxonNodeRegularUser(TaxonomyUserTestMixin, HybridTaxonNodeBase):
    pass


class TestHybridTaxonNodeAdmin(TaxonomyAdminTestMixin, HybridTaxonNodeBase):
    pass
