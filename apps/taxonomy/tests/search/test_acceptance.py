from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

import haystack

from apps.taxonomy.tests.factories import TaxonNodeFactory, TreeFactory, TaxonRankFactory

TEST_INDEX = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'TIMEOUT': 60 * 10,
        'INDEX_NAME': 'test_index',
    },
}


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class TestTaxonSearchAcceptance(APITestCase):

    def setUp(self):
        haystack.connections.reload('default')
        self.user = User.objects.create_user('tester', 'tester@plutof.ee', 'TesterPassword')
        self.client.login(username='tester', password='TesterPassword')
        TaxonRankFactory(id=0)
        tree = TreeFactory()
        TaxonNodeFactory(tree=tree)
        call_command('clear_index', interactive=False, verbosity=0)
        super(APITestCase, self).setUp()

    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)

    def test_taxon_search_valid_query(self):
        """
        Ensure that GET request to taxon search endpoint
        will return valid search results
        """
        call_command('update_index', 'taxonomy', interactive=False)
        response = self.client.get(reverse('taxon-search'), {'search_query': "tree"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_taxon_search_invalid_query(self):
        """
        Ensure that GET request to taxon search endpoint
        returns error response if invalid query
        """
        response = self.client.get(reverse('taxon-search'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.content, '{"search_query": ["This field is required."]}')
