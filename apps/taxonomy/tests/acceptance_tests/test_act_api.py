from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.taxonomy.tests.base import TaxonomyUnauthorizedTestMixin, TaxonomyReadOnlyTestMixin, TaxonomyAdminReadOnlyTestMixin
from apps.taxonomy.tests import factories


class ActBase(APITestCase):

    @staticmethod
    def get_obj_url():
        obj = factories.ActFactory()
        return reverse('act-detail', args=[obj.id]), obj

    @staticmethod
    def get_url():
        return reverse('act-list')

    @staticmethod
    def get_raw_data():
        data = {}
        return data


class TestActUnauthorized(TaxonomyUnauthorizedTestMixin, ActBase):
    pass


class TestActRegularUser(TaxonomyReadOnlyTestMixin, ActBase):
    pass


class TestActAdmin(TaxonomyAdminReadOnlyTestMixin, ActBase):
    pass
