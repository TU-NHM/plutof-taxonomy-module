from django.test import TestCase

from apps.taxonomy.models import Act
from apps.taxonomy.tests import factories
from apps.taxonomy.tests.base import TaxonomyBaseTestMixin


class TestActCreation(TestCase):

    def setUp(self):
        super(TestActCreation, self).setUp()
        factories.TaxonRankFactory(id=0)

    def test_creates_act_for_new_taxon(self):
        taxonnode = factories.TaxonNodeFactory()
        taxonnode.post_created()
        self.assertEqual(Act.objects.filter(taxon_node=taxonnode, type="new_taxon").count(), 1)

    def test_create_edit_name_act(self):
        taxonnode = factories.TaxonNodeFactory()
        taxonnode.epithet = "new epithet"
        taxonnode.save()
        self.assertEqual(Act.objects.filter(taxon_node=taxonnode, type="edit_name").count(), 1)

    def test_create_change_parent_act(self):
        taxonnode = TaxonomyBaseTestMixin.create_working_taxonnode()
        taxonnode_new_parent = TaxonomyBaseTestMixin.create_working_taxonnode(taxonnode.tree)
        taxonnode.post_changed(parent=taxonnode_new_parent)
        self.assertEqual(Act.objects.filter(taxon_node=taxonnode, type="change_parent").count(), 1)

    def test_not_create_change_parent_act_when_did_not_change(self):
        taxonnode = TaxonomyBaseTestMixin.create_working_taxonnode()
        taxonnode_parent = TaxonomyBaseTestMixin.create_working_taxonnode(taxonnode.tree)
        factories.EdgeFactory(ancestor=taxonnode_parent, descendant=taxonnode)
        taxonnode.post_changed(parent=taxonnode_parent)
        self.assertEqual(Act.objects.filter(taxon_node=taxonnode, type="change_parent").count(), 0)

    def test_create_change_to_synonym_act(self):
        valid_name = factories.TaxonNodeFactory()
        taxonnode = factories.TaxonNodeFactory(tree=valid_name.tree)
        taxonnode.valid_name = valid_name
        taxonnode.synonym_type = "synonym"
        taxonnode.save()
        self.assertEqual(Act.objects.filter(taxon_node=taxonnode, type="marked_as_synonym").count(), 1)

    def test_create_change_to_basionym_act(self):
        valid_name = factories.TaxonNodeFactory()
        taxonnode = factories.TaxonNodeFactory(tree=valid_name.tree)
        taxonnode.valid_name = valid_name
        taxonnode.synonym_type = "basionym"
        taxonnode.save()
        self.assertEqual(Act.objects.filter(taxon_node=taxonnode, type="marked_as_basionym").count(), 1)

    def test_create_change_nomen_status_act(self):
        taxonnode = factories.TaxonNodeFactory()
        taxonnode.nomenclatural_status = "established"
        taxonnode.save()
        self.assertEqual(Act.objects.filter(taxon_node=taxonnode, type="change_nomen_status").count(), 1)
