from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.taxonomy.tests.base import UnauthorizedTestMixin, PlutoFModelUserTestMixin, AdminTestMixin
from apps.taxonomy.tests import factories
from apps.taxonomy.tests.base import TaxonomyBaseTestMixin


class TaxonNodeBase(APITestCase):

    @staticmethod
    def get_obj_url(user=None):
        obj = factories.TaxonNodeFactory(tree=factories.TreeFactory())
        factories.EdgeFactory(ancestor=obj.tree.root_node, descendant=obj.tree.root_node)
        return reverse('taxonnode-detail', args=[obj.id]), obj

    @staticmethod
    def get_url():
        return reverse('taxonnode-list')

    def get_raw_data(self):
        tree = factories.TreeFactory()
        tree_url = reverse('tree-detail', args=[tree.id])
        factories.EdgeFactory(ancestor=tree.root_node, descendant=tree.root_node)
        factories.TraversalOrderFactory(current=tree.root_node, previous=tree.root_node, next=tree.root_node)
        taxon_rank_url = reverse('taxonrank-detail', args=[factories.TaxonRankFactory().id])
        data = {"tree": tree_url,
                "epithet": "epithet has changed",
                "taxon_rank": taxon_rank_url
                }
        return data


class TaxonNodeChangeParentMethods():
    change_own_status = None

    def create_taxonnode_with_parent(self):
        taxonnode = TaxonomyBaseTestMixin.create_working_taxonnode()
        taxonnode.save()
        taxonnode.tree.save()
        taxonnode_parent = TaxonomyBaseTestMixin.create_working_taxonnode(tree=taxonnode.tree)
        factories.EdgeFactory(ancestor=taxonnode_parent, descendant=taxonnode)
        return taxonnode

    def get_put_data(self, taxonnode, set_new_taxonnode_parent=False):
        tree_url = reverse('tree-detail', args=[taxonnode.tree.id])
        taxonnode_parent_new = TaxonomyBaseTestMixin.create_working_taxonnode(tree=taxonnode.tree)
        new_parent_url = reverse('taxonnode-detail', args=[taxonnode_parent_new.id]) if set_new_taxonnode_parent else None
        taxon_rank_url = reverse('taxonrank-detail', args=[factories.TaxonRankFactory().id])
        data = {"tree": tree_url,
                "epithet": "epithet has changed",
                "taxon_rank": taxon_rank_url,
                "parent": new_parent_url
                }
        return data

    def common_base(self, set_new_taxonnode_parent=False):
        taxonnode = self.create_taxonnode_with_parent()
        taxonnode_url = reverse('taxonnode-detail', args=[taxonnode.id])

        raw_put_data = self.get_put_data(taxonnode, set_new_taxonnode_parent)
        response = self.client.put(taxonnode_url, raw_put_data, 'json')
        self.assertEqual(response.status_code, self.change_own_status)
        if self.user:
            if set_new_taxonnode_parent:
                self.assertTrue(response.data["parent"].endswith(raw_put_data["parent"]))
            else:
                self.assertEqual(None, response.data["parent"])

    def test_changing_parent_of_existing_own_taxonnode(self):
        self.common_base(True)

    def test_changing_parent_to_no_parent(self):
        self.common_base()


class TestTaxonNodeUnauthorized(UnauthorizedTestMixin, TaxonNodeChangeParentMethods, TaxonNodeBase):
    change_own_status = status.HTTP_401_UNAUTHORIZED

    def setUp(self):
        super(TestTaxonNodeUnauthorized, self).setUp()
        factories.TaxonRankFactory(id=0)


class TestTaxonNodeRegularUser(PlutoFModelUserTestMixin, TaxonNodeChangeParentMethods, TaxonNodeBase):
    change_own_status = status.HTTP_200_OK

    def setUp(self):
        super(TestTaxonNodeRegularUser, self).setUp()
        factories.TaxonRankFactory(id=0)


class TestTaxonNodeAdmin(AdminTestMixin, TaxonNodeChangeParentMethods, TaxonNodeBase):
    change_own_status = status.HTTP_200_OK

    def setUp(self):
        super(TestTaxonNodeAdmin, self).setUp()
        factories.TaxonRankFactory(id=0)
