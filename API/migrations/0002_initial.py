# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Scene'
        db.create_table(u'API_scene', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('version', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('background', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='scenes', null=True, to=orm['API.Background'])),
            ('background_scale', self.gf('django.db.models.fields.DecimalField')(default=1.0, max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal(u'API', ['Scene'])

        # Adding model 'SceneProp'
        db.create_table(u'API_sceneprop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scene', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['API.Scene'])),
            ('prop_file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['API.Prop'])),
            ('scale', self.gf('django.db.models.fields.DecimalField')(default=1.0, max_digits=8, decimal_places=2)),
            ('position_x', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('position_y', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('movable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')(default=500)),
            ('rotation', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=8, decimal_places=2)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'API', ['SceneProp'])

        # Adding model 'Background'
        db.create_table(u'API_background', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('keyword', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'API', ['Background'])

        # Adding model 'Prop'
        db.create_table(u'API_prop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('keyword', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'API', ['Prop'])


    def backwards(self, orm):
        # Deleting model 'Scene'
        db.delete_table(u'API_scene')

        # Deleting model 'SceneProp'
        db.delete_table(u'API_sceneprop')

        # Deleting model 'Background'
        db.delete_table(u'API_background')

        # Deleting model 'Prop'
        db.delete_table(u'API_prop')


    models = {
        u'API.background': {
            'Meta': {'object_name': 'Background'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'API.prop': {
            'Meta': {'object_name': 'Prop'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'API.scene': {
            'Meta': {'object_name': 'Scene'},
            'background': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'scenes'", 'null': 'True', 'to': u"orm['API.Background']"}),
            'background_scale': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'max_digits': '8', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'props': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['API.Prop']", 'through': u"orm['API.SceneProp']", 'symmetrical': 'False'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'API.sceneprop': {
            'Meta': {'object_name': 'SceneProp'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'movable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'position_x': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'position_y': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'prop_file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['API.Prop']"}),
            'rotation': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '8', 'decimal_places': '2'}),
            'scale': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'max_digits': '8', 'decimal_places': '2'}),
            'scene': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['API.Scene']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['API']