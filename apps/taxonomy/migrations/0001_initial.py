# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Act',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=63, choices=[(b'new_taxon', 'New taxon node created'), (b'marked_as_synonym', 'Taxon node was marked as a synonym'), (b'marked_as_basionym', 'Taxon node was marked as a basionym'), (b'marked_as_current', 'Taxon node was marked as a current'), (b'change_parent', 'Taxon node parent was changed'), (b'edit_name', 'Taxon node name was edited'), (b'change_nomen_status', "Taxon node's nomenclatural status was changed"), (b'delete_taxon', 'Taxon node name was deleted')])),
                ('previous_value', models.CharField(max_length=255, null=True, blank=True)),
                ('remarks', models.TextField(null=True, blank=True)),
                ('citation_text', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CommonName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('common_name', models.CharField(max_length=255)),
                ('is_preferred', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('length', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('included_ranks', models.TextField(null=True, blank=True)),
                ('excluded_ranks', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HybridTaxonNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('iso_639', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaxonNameConcept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaxonNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(help_text=b'User defined ID', max_length=255, null=True, verbose_name=b'User defined ID', blank=True)),
                ('uid', models.CharField(max_length=255, null=True, blank=True)),
                ('epithet', models.CharField(max_length=255)),
                ('synonym_type', models.CharField(blank=True, max_length=63, null=True, choices=[(b'synonym', 'Synonym'), (b'basionym', 'Basionym'), (b'invalid', 'Invalid')])),
                ('nomenclatural_status', models.CharField(blank=True, max_length=63, null=True, choices=[(b'established', 'Established'), (b'compliant', 'Compliant'), (b'non-compliant', 'Non-compliant'), (b'registered', 'Registered')])),
                ('epithet_author', models.CharField(max_length=255, verbose_name=b'Author', blank=True)),
                ('year_described_in', models.CharField(max_length=63, null=True, blank=True)),
                ('use_parentheses', models.BooleanField(default=False)),
                ('owner_id', models.IntegerField(null=True)),
                ('created_by', models.IntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.IntegerField(null=True)),
                ('updated_at', models.DateTimeField(default=b'2000-01-01 00:00:00+03:00', blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_fossil', models.BooleanField(default=False)),
                ('parent_described_in', models.ForeignKey(related_name='original_parent', on_delete=django.db.models.deletion.PROTECT, blank=True, to='taxonomy.TaxonNode', null=True)),
                ('taxon_name_concept', models.ForeignKey(related_name='taxa', blank=True, to='taxonomy.TaxonNameConcept', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaxonRank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('abbreviation', models.CharField(max_length=255)),
                ('zoology_rank', models.CharField(max_length=255)),
                ('botany_rank', models.CharField(max_length=255)),
                ('bacteria_rank', models.CharField(max_length=255)),
                ('prefix', models.CharField(max_length=255)),
                ('suffix', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TraversalOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_type', models.CharField(default=b'pre', max_length=31)),
                ('current', models.ForeignKey(related_name='current_taxon', to='taxonomy.TaxonNode')),
                ('next', models.ForeignKey(related_name='next_taxon', to='taxonomy.TaxonNode')),
                ('previous', models.ForeignKey(related_name='previous_taxon', to='taxonomy.TaxonNode')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('owner_id', models.IntegerField(null=True)),
                ('created_by', models.IntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.IntegerField(null=True)),
                ('updated_at', models.DateTimeField(default=b'2000-01-01 00:00:00+03:00', blank=True)),
                ('is_public', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('origin_tree', models.ForeignKey(related_name='origin', blank=True, to='taxonomy.Tree', null=True)),
                ('root_node', models.ForeignKey(related_name='root', blank=True, to='taxonomy.TaxonNode', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='taxonnode',
            name='taxon_rank',
            field=models.ForeignKey(to='taxonomy.TaxonRank', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taxonnode',
            name='tree',
            field=models.ForeignKey(to='taxonomy.Tree', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taxonnode',
            name='valid_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='taxonomy.TaxonNode', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hybridtaxonnode',
            name='hybrid_parent1',
            field=models.ForeignKey(related_name='hybrid_parent_1', to='taxonomy.TaxonNode'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hybridtaxonnode',
            name='hybrid_parent2',
            field=models.ForeignKey(related_name='hybrid_parent_2', to='taxonomy.TaxonNode'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hybridtaxonnode',
            name='taxon_node',
            field=models.ForeignKey(to='taxonomy.TaxonNode'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filter',
            name='locale',
            field=models.ForeignKey(blank=True, to='taxonomy.Language', help_text=b'Language', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filter',
            name='lowest_rank',
            field=models.ForeignKey(related_name='minimum_rank', blank=True, to='taxonomy.TaxonRank', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filter',
            name='tree',
            field=models.ForeignKey(blank=True, to='taxonomy.Tree', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='ancestor',
            field=models.ForeignKey(related_name='parent', to='taxonomy.TaxonNode'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='descendant',
            field=models.ForeignKey(related_name='child', to='taxonomy.TaxonNode'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commonname',
            name='iso_639',
            field=models.ForeignKey(help_text=b'Language', to='taxonomy.Language'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commonname',
            name='taxon_node',
            field=models.ForeignKey(related_name='vernacular_names', to='taxonomy.TaxonNode', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='taxon_node',
            field=models.ForeignKey(related_name='acts', to='taxonomy.TaxonNode'),
            preserve_default=True,
        ),
    ]
