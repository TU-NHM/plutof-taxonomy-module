from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.taxonomy.tests.base import TaxonomyUnauthorizedTestMixin, TaxonomyUserTestMixin, TaxonomyAdminTestMixin
from apps.taxonomy.tests.factories import TreeFactory


class TreeBase(APITestCase):

    @staticmethod
    def get_obj_url(user=None):
        obj = TreeFactory()
        return reverse('tree-detail', args=[obj.id]), obj

    @staticmethod
    def get_url():
        return reverse('tree-list')

    @staticmethod
    def get_raw_data():
        data = {"name": "Tree 1 - changed"}
        return data


class TestTreeUnauthorized(TaxonomyUnauthorizedTestMixin, TreeBase):
    pass


class TestTreeRegularUser(TaxonomyUserTestMixin, TreeBase):
    pass


class TestTreeAdmin(TaxonomyAdminTestMixin, TreeBase):
    pass
