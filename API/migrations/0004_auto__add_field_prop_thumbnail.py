# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Prop.thumbnail'
        db.add_column(u'API_prop', 'thumbnail',
                      self.gf('django.db.models.fields.files.ImageField')(default='prop-thumbnails/default/thumbnail.png', max_length=100),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Prop.thumbnail'
        db.delete_column(u'API_prop', 'thumbnail')


    models = {
        u'API.background': {
            'Meta': {'object_name': 'Background'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'default': "'background-thumbnails/default/thumbnail.png'", 'max_length': '100'})
        },
        u'API.prop': {
            'Meta': {'object_name': 'Prop'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'default': "'prop-thumbnails/default/thumbnail.png'", 'max_length': '100'})
        },
        u'API.scene': {
            'Meta': {'object_name': 'Scene'},
            'background': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'scenes'", 'null': 'True', 'to': u"orm['API.Background']"}),
            'background_scale': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'max_digits': '8', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'next_scene': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'scenes'", 'null': 'True', 'to': u"orm['API.Scene']"}),
            'props': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['API.Prop']", 'through': u"orm['API.SceneProp']", 'symmetrical': 'False'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'API.sceneprop': {
            'Meta': {'object_name': 'SceneProp'},
            'always_visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'movable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'position_x': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'position_y': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'prop_file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['API.Prop']"}),
            'rotation': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '8', 'decimal_places': '2'}),
            'scale': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'max_digits': '8', 'decimal_places': '2'}),
            'scene': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['API.Scene']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['API']