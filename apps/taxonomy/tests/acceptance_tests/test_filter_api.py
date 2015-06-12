from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.taxonomy.tests.base import UnauthorizedTestMixin, UserTestMixin, AdminTestMixin
from apps.taxonomy.tests.factories import FilterFactory


class FilterBase(APITestCase):

    def get_obj_url(self):
        obj = FilterFactory()
        return reverse('filter-detail', args=[obj.id]), obj

    @staticmethod
    def get_url():
        return reverse('filter-list')

    def get_raw_data(self):
        data = {}
        return data


class TestFilterUnauthorized(UnauthorizedTestMixin, FilterBase):
    pass


class TestFilterRegularUser(UserTestMixin, FilterBase):
    pass


class TestFilterAdmin(AdminTestMixin, FilterBase):
    pass
