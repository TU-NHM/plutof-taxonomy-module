from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.taxonomy.tests.base import UnauthorizedTestMixin, ReadOnlyTestMixin, AdminReadOnlyTestMixin
from apps.taxonomy.tests.factories import TaxonRankFactory


class TaxonRankBase(APITestCase):

    @staticmethod
    def get_obj_url():
        obj = TaxonRankFactory()
        return reverse('taxonrank-detail', args=[obj.id]), obj

    @staticmethod
    def get_url():
        return reverse('taxonrank-list')

    @staticmethod
    def get_raw_data():
        data = {}
        return data


class TestTaxonRankUnauthorized(UnauthorizedTestMixin, TaxonRankBase):
    pass


class TestTaxonRankRegularUser(ReadOnlyTestMixin, TaxonRankBase):
    pass


class TestTaxonRankAdmin(AdminReadOnlyTestMixin, TaxonRankBase):
    pass
