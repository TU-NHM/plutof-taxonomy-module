from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from django.core.exceptions import ObjectDoesNotExist

from apps.taxonomy.tests.base import TaxonomyUnauthorizedTestMixin, TaxonomyUserTestMixin, TaxonomyAdminTestMixin
from apps.taxonomy.tests.factories import CommonNameFactory, TaxonNodeFactory, TreeFactory, LanguageFactory
from apps.taxonomy.models import Language


class CommonNameBase(APITestCase):

    def get_obj_url(self):
        obj = CommonNameFactory(taxon_node=TaxonNodeFactory())
        return reverse('commonname-detail', args=[obj.id]), obj

    @staticmethod
    def get_url():
        return reverse('commonname-list')

    def get_raw_data(self):
        taxon_node_url = reverse('taxonnode-detail', args=[TaxonNodeFactory(tree=TreeFactory()).id])
        try:
            language = Language.objects.get(iso_639='est')
            language_url = reverse('language-detail', args=[language.iso_639])
        except ObjectDoesNotExist:
            language = LanguageFactory(iso_639='est')
            language_url = reverse('language-detail', args=[language.iso_639])
        data = {"taxon_node": taxon_node_url,
                "iso_639": language_url,
                "common_name": "Common name has changed",
                "is_preferred": False}

        return data


class TestCommonNameUnauthorized(TaxonomyUnauthorizedTestMixin, CommonNameBase):
    pass


class TestCommonNameRegularUser(TaxonomyUserTestMixin, CommonNameBase):
    pass


class TestCommonNameAdmin(TaxonomyAdminTestMixin, CommonNameBase):
    pass
