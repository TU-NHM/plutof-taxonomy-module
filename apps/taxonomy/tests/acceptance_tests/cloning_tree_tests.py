from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from apps.taxonomy.models import TaxonNode, Edge
from rest_framework import status
from rest_framework.test import APITestCase
# import json


class TestCloningExistingTree(APITestCase):

    fixtures = ['apps/taxonomy/fixtures/taxonrank.json',
                'apps/taxonomy/fixtures/test_taxonnameconcept.json',
                'apps/taxonomy/fixtures/test_tree.json',
                'apps/taxonomy/fixtures/test_taxonnode.json',
                'apps/taxonomy/fixtures/test_edge.json',
                'apps/taxonomy/fixtures/test_traversalorder.json'
                ]

    def setUp(self):
        self.synonym = TaxonNode(valid_name_id=7, parent_described_in_id=3, epithet="synonymous", tree_id=1, taxon_rank_id=30)
        self.synonym.save()
        self.user = User.objects.create_user('tyrion', 'tyrion@lannister.com', 'lannister')
        self.client.login(username='tyrion', password='lannister')
        self.url = reverse('tree-list')
        self.name = 'new clone'

    def test_cloning_existing_tree(self):
        """ Cloning full tree creates exactly the same tree
        """
        origin_tree_url = reverse('tree-detail', kwargs={'pk': 1})
        response = self.client.post(self.url, {"origin_tree": origin_tree_url,
                                               "name": self.name}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaxonNode.objects.filter(tree_id=2).count(), TaxonNode.objects.filter(tree_id=1).count())
        self.assertEqual(TaxonNode.objects.count(), 18)

    def test_cloning_partial_tree(self):
        """ Cloning partial tree creates tree starting from given node
            Also checks if all synonyms are correct
        """
        root_node_id = 6
        root_node = reverse('taxonnode-detail', kwargs={'pk': root_node_id})
        response = self.client.post(self.url, {"root_node": root_node,
                                               "name": self.name}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaxonNode.objects.filter(tree_id=2, valid_name=None).count(),
                         Edge.objects.filter(ancestor_id=root_node_id).count()
                         )

        self.assertEqual(TaxonNode.objects.count(), 13)

        synonym_in_new_tree = TaxonNode.objects.get(pk=8).get_related_taxa()[0]
        self.assertEqual(synonym_in_new_tree.parent_described_in.tree_id, 2)
        self.assertEqual(synonym_in_new_tree.parent_described_in.get_related_taxa().count(), 1)
