from django.test import TestCase

from apps.taxonomy.tests import factories

from django.contrib.auth.models import User

from rest_framework import status


class BaseTestMixin(object):
    """
    Base class for testing
    """
    read_list_status = None
    read_options_status = None
    read_head_status = None
    create_status = None
    read_detail_status = None
    change_status = None
    patch_status = None
    delete_status = None
    change_own_status = None
    read_detail_own_status = None

    def test_can_read_list(self):
        """
        Ensure that instance list can/can't be read
        """
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, self.read_list_status)

    def test_can_read_options(self):
        """
        Ensure that endpoint OPTION's can/can't be read
        """
        response = self.client.options(self.get_url())
        self.assertEqual(response.status_code, self.read_options_status)

    def test_can_read_head(self):
        """
        Ensure that endpoint HEAD can/can't be read
        """
        response = self.client.head(self.get_url())
        self.assertEqual(response.status_code, self.read_head_status)

    def test_can_create(self):
        """
        Ensure that new instance can/can't be created - POST
        """
        response = self.client.post(self.get_url(), self.get_raw_data(), 'json')
        self.assertEqual(response.status_code, self.create_status)

    def test_can_read_detail(self):
        """
        Ensure that existing instance can/can't be read
        """
        url_obj = self.get_obj_url()
        response = self.client.get(url_obj[0])
        self.assertEqual(response.status_code, self.read_detail_status)

    def test_can_change(self):
        """
        Ensure that existing instance can/can't be changed with PUT
        """
        url_obj = self.get_obj_url()
        response = self.client.put(url_obj[0], self.get_raw_data(), 'json')
        self.assertEqual(response.status_code, self.change_status)

    def test_can_patch(self):
        """
        Ensure that existing instance can/can't be changed with PATCH
        """
        url_obj = self.get_obj_url()
        response = self.client.patch(url_obj[0], {}, 'json')
        self.assertEqual(response.status_code, self.patch_status)

    def test_can_delete(self):
        """
        Ensure that existing instance can/can't be deleted
        """
        url_obj = self.get_obj_url()
        response = self.client.delete(url_obj[0])
        self.assertEqual(response.status_code, self.delete_status)


class UnauthorizedTestMixin(BaseTestMixin):
    """
    Testing different methods while not logged in as any user
    """
    read_list_status = status.HTTP_401_UNAUTHORIZED
    read_options_status = status.HTTP_401_UNAUTHORIZED
    read_head_status = status.HTTP_401_UNAUTHORIZED
    create_status = status.HTTP_401_UNAUTHORIZED
    read_detail_status = status.HTTP_401_UNAUTHORIZED
    change_status = status.HTTP_401_UNAUTHORIZED
    patch_status = status.HTTP_401_UNAUTHORIZED
    delete_status = status.HTTP_401_UNAUTHORIZED

    def setUp(self):
        self.user = None


class UserTestMixin(BaseTestMixin):
    """
    Testing different methods while logged in as regular user
    """
    read_list_status = status.HTTP_200_OK
    read_options_status = status.HTTP_200_OK
    read_head_status = status.HTTP_200_OK
    create_status = status.HTTP_201_CREATED
    read_detail_status = status.HTTP_200_OK
    change_status = status.HTTP_200_OK
    # patch_status = status.HTTP_405_METHOD_NOT_ALLOWED
    patch_status = status.HTTP_200_OK
    delete_status = status.HTTP_204_NO_CONTENT

    def setUp(self):
        """
        Creating necessary instances into database
        """
        self.user = User.objects.create_user('tester', 'tester@plutof.ee', 'TesterPassword')
        self.client.login(username='tester', password='TesterPassword')


class UnauthorizedPublicTestMixin(UnauthorizedTestMixin):
    """
    Testing different methods on a public-readable endpoint while not logged in as any user
    """
    read_list_status = status.HTTP_200_OK
    read_options_status = status.HTTP_200_OK
    read_head_status = status.HTTP_200_OK
    read_detail_status = status.HTTP_200_OK
    create_status = status.HTTP_405_METHOD_NOT_ALLOWED
    change_status = status.HTTP_405_METHOD_NOT_ALLOWED
    delete_status = status.HTTP_405_METHOD_NOT_ALLOWED
    patch_status = status.HTTP_405_METHOD_NOT_ALLOWED
    delete_status = status.HTTP_405_METHOD_NOT_ALLOWED


class AdminTestMixin(UserTestMixin):
    """
    Testing different methods while logged in as regular user
    """
    def setUp(self):
        """
        Creating necessary instances into database
        """
        self.user = User.objects.create_superuser('super', 'super@plutof.ee', 'complexpass')
        self.client.login(username='super', password='complexpass')


class ReadOnlyTestMixin(UserTestMixin):
    """
    Testing different methods while logged in as regular user
    """
    create_status = status.HTTP_405_METHOD_NOT_ALLOWED
    change_status = status.HTTP_405_METHOD_NOT_ALLOWED
    delete_status = status.HTTP_405_METHOD_NOT_ALLOWED
    patch_status = status.HTTP_405_METHOD_NOT_ALLOWED


class AdminReadOnlyTestMixin(AdminTestMixin):
    """
    Testing different methods while logged in as regular user
    """
    create_status = status.HTTP_405_METHOD_NOT_ALLOWED
    change_status = status.HTTP_405_METHOD_NOT_ALLOWED
    delete_status = status.HTTP_405_METHOD_NOT_ALLOWED
    patch_status = status.HTTP_405_METHOD_NOT_ALLOWED


class PlutoFModelUserTestMixin(UserTestMixin):
    """

    """
    read_detail_status = status.HTTP_200_OK
    change_status = status.HTTP_200_OK
    delete_status = status.HTTP_204_NO_CONTENT
    change_own_status = status.HTTP_200_OK
    delete_own_status = status.HTTP_204_NO_CONTENT
    read_detail_own_status = status.HTTP_200_OK

    def test_can_change_own(self):
        url_obj = self.get_obj_url()
        response = self.client.put(url_obj[0], self.get_raw_data(), 'json')
        self.assertEqual(response.status_code, self.change_own_status)

    def test_can_delete_own(self):
        """
        Ensure that existing instance can/can't be deleted
        """
        url_obj = self.get_obj_url()
        response = self.client.delete(url_obj[0])
        self.assertEqual(response.status_code, self.delete_own_status)

    def test_can_read_detail_own(self):
        url_obj = self.get_obj_url()
        response = self.client.get(url_obj[0])
        self.assertEqual(response.status_code, self.read_detail_own_status)


class TaxonomyUnauthorizedTestMixin(UnauthorizedTestMixin):

    def setUp(self):
        super(TaxonomyUnauthorizedTestMixin, self).setUp()
        factories.TaxonRankFactory(id=0)


class TaxonomyReadOnlyTestMixin(ReadOnlyTestMixin):

    def setUp(self):
        super(TaxonomyReadOnlyTestMixin, self).setUp()
        factories.TaxonRankFactory(id=0)


class TaxonomyUserTestMixin(UserTestMixin):

    def setUp(self):
        super(TaxonomyUserTestMixin, self).setUp()
        factories.TaxonRankFactory(id=0)


class TaxonomyPlutoFModelUserTestMixin(PlutoFModelUserTestMixin):

    def setUp(self):
        super(TaxonomyPlutoFModelUserTestMixin, self).setUp()
        factories.TaxonRankFactory(id=0)


class TaxonomyAdminReadOnlyTestMixin(AdminReadOnlyTestMixin):

    def setUp(self):
        super(TaxonomyAdminReadOnlyTestMixin, self).setUp()
        factories.TaxonRankFactory(id=0)


class TaxonomyAdminTestMixin(AdminTestMixin):

    def setUp(self):
        super(TaxonomyAdminTestMixin, self).setUp()
        factories.TaxonRankFactory(id=0)


class TaxonomyBaseTestMixin(TestCase):
    TAXON_NODE_LIST = []

    @staticmethod
    def create_working_taxonnode(tree=None, no_traversal=False):
        if tree:
            taxonnode = factories.TaxonNodeFactory(tree=tree)
        else:
            taxonnode = factories.TaxonNodeFactory()
        factories.EdgeFactory(ancestor=taxonnode, descendant=taxonnode, length=0)
        if not no_traversal:
            factories.TraversalOrderFactory(current=taxonnode, previous=taxonnode, next=taxonnode)
        # if tree is given, then these have already been done
        if not tree:
            factories.TraversalOrderFactory(current=taxonnode.tree.root_node, previous=taxonnode.tree.root_node, next=taxonnode.tree.root_node)
            factories.EdgeFactory(ancestor=taxonnode.tree.root_node, descendant=taxonnode.tree.root_node)
        return taxonnode

    def setUp(self):
        super(TaxonomyBaseTestMixin, self).setUp()
        factories.TaxonRankFactory(id=0)
        tree = factories.TreeFactory(name="Tree 1")
        # create nodes
        taxonnode_1 = tree.root_node
        taxonnode_2 = self.create_working_taxonnode(tree, True)
        taxonnode_3 = self.create_working_taxonnode(tree, True)
        taxonnode_4 = self.create_working_taxonnode(tree, True)
        taxonnode_5 = self.create_working_taxonnode(tree, True)
        taxonnode_6 = self.create_working_taxonnode(tree, True)
        taxonnode_7 = self.create_working_taxonnode(tree, True)
        taxonnode_8 = self.create_working_taxonnode(tree)
        taxonnode_8.valid_name, taxonnode_8.synonym_type, taxonnode_8.parent_described_in = taxonnode_7, "synonym", taxonnode_6
        taxonnode_8.save()
        self.TAXON_NODE_LIST = [taxonnode_1, taxonnode_2, taxonnode_3, taxonnode_4, taxonnode_5, taxonnode_6, taxonnode_7, taxonnode_8]

        # connect node 1 to its children
        factories.EdgeFactory(ancestor=taxonnode_1, descendant=taxonnode_2, length=1)
        factories.EdgeFactory(ancestor=taxonnode_1, descendant=taxonnode_3, length=2)
        factories.EdgeFactory(ancestor=taxonnode_1, descendant=taxonnode_4, length=3)
        factories.EdgeFactory(ancestor=taxonnode_1, descendant=taxonnode_5, length=3)
        factories.EdgeFactory(ancestor=taxonnode_1, descendant=taxonnode_6, length=2)
        factories.EdgeFactory(ancestor=taxonnode_1, descendant=taxonnode_7, length=3)
        # connect node 2 to its children
        factories.EdgeFactory(ancestor=taxonnode_2, descendant=taxonnode_3, length=1)
        factories.EdgeFactory(ancestor=taxonnode_2, descendant=taxonnode_4, length=2)
        factories.EdgeFactory(ancestor=taxonnode_2, descendant=taxonnode_5, length=2)
        factories.EdgeFactory(ancestor=taxonnode_2, descendant=taxonnode_6, length=1)
        factories.EdgeFactory(ancestor=taxonnode_2, descendant=taxonnode_7, length=2)
        # connect node 3 to its children
        factories.EdgeFactory(ancestor=taxonnode_3, descendant=taxonnode_4, length=1)
        factories.EdgeFactory(ancestor=taxonnode_3, descendant=taxonnode_5, length=1)
        # connect node 6 to its children
        factories.EdgeFactory(ancestor=taxonnode_6, descendant=taxonnode_7, length=1)

        # create traversalorders
        factories.TraversalOrderFactory(current=taxonnode_2, previous=taxonnode_7, next=taxonnode_3)
        factories.TraversalOrderFactory(current=taxonnode_3, previous=taxonnode_2, next=taxonnode_4)
        factories.TraversalOrderFactory(current=taxonnode_4, previous=taxonnode_3, next=taxonnode_5)
        factories.TraversalOrderFactory(current=taxonnode_5, previous=taxonnode_4, next=taxonnode_6)
        factories.TraversalOrderFactory(current=taxonnode_6, previous=taxonnode_5, next=taxonnode_7)
        factories.TraversalOrderFactory(current=taxonnode_7, previous=taxonnode_6, next=taxonnode_2)
