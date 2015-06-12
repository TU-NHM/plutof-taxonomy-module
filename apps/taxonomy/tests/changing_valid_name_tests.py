from django.core.exceptions import ValidationError

from apps.taxonomy.models import Edge, TraversalOrder
from apps.taxonomy.tests.base import TaxonomyBaseTestMixin


class TestChangingCurrentName(TaxonomyBaseTestMixin):

    def test_change_current_to_synonym_only_with_non_children(self):
        taxonnode = self.TAXON_NODE_LIST[2]
        taxonnode.valid_name = self.TAXON_NODE_LIST[5]
        taxonnode.synonym_type = 'synonym'
        self.assertRaisesMessage(ValidationError, 'Synonym cannot have direct children.', taxonnode.clean_fields, {})

    def test_change_current_to_synonym_removes_edges(self):
        taxonnode = self.TAXON_NODE_LIST[3]
        taxonnode.valid_name = self.TAXON_NODE_LIST[4]
        taxonnode.synonym_type = 'synonym'
        self.assertTrue(Edge.objects.filter(descendant_id=taxonnode.pk).count() > 2)
        taxonnode.save()
        self.assertEqual(Edge.objects.filter(descendant_id=taxonnode.pk).count(), 1)

    def test_change_current_to_synonym_removes_from_traversal_order(self):
        taxonnode = self.TAXON_NODE_LIST[3]
        taxonnode.valid_name = self.TAXON_NODE_LIST[4]
        taxonnode.synonym_type = 'synonym'
        self.assertTrue(TraversalOrder.objects.get(current_id=taxonnode.pk))
        taxonnode.save()
        self.assertFalse(TraversalOrder.objects.filter(current_id=taxonnode.pk).count())

    def test_change_current_to_synonym_updates_previous_synonyms(self):
        taxonnode = self.TAXON_NODE_LIST[6]
        taxonnode.valid_name = self.TAXON_NODE_LIST[4]
        taxonnode.synonym_type = 'synonym'
        self.assertTrue(len(taxonnode.get_synonyms()))
        taxonnode.save()
        self.assertFalse(len(taxonnode.get_synonyms()))
        self.assertEqual(len(taxonnode.valid_name.get_synonyms()), 2)
        self.assertEqual(Edge.objects.filter(descendant=self.TAXON_NODE_LIST[7]).count(), 1)

    def test_change_synonym_to_current_removes_all_edges(self):
        taxonnode = self.TAXON_NODE_LIST[7]
        taxonnode.valid_name = None
        taxonnode.synonym_type = ''
        taxonnode.save()
        self.assertFalse(bool(Edge.objects.filter(descendant_id=taxonnode.pk).count()))

    def test_change_synonym_to_current_creates_new_edges(self):
        taxonnode = self.TAXON_NODE_LIST[7]
        taxonnode.valid_name = None
        taxonnode.synonym_type = ''
        taxonnode.save()
        taxonnode.post_changed(parent=self.TAXON_NODE_LIST[5])
        self.assertEqual(Edge.objects.filter(descendant_id=taxonnode.pk).count(), 4)

    def test_change_synonym_to_current_inserts_to_traversal_order(self):
        taxonnode = self.TAXON_NODE_LIST[7]
        self.assertFalse(TraversalOrder.objects.filter(current_id=taxonnode.pk).count())
        taxonnode.valid_name = None
        taxonnode.synonym_type = ''
        taxonnode.save()
        taxonnode.post_changed(parent=self.TAXON_NODE_LIST[5])
        self.assertTrue(TraversalOrder.objects.filter(current_id=taxonnode.pk).count())
        self.assertEqual(TraversalOrder.objects.get(current_id=taxonnode.pk).previous.pk, self.TAXON_NODE_LIST[5].id)
