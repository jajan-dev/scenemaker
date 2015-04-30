from django import forms
from django.db import models

class Scene(models.Model):
	
	## Metadata
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=500, blank=True)
	version = models.DateTimeField(auto_now=True)

	## Thumbnail Key
	def key(self, filename):
		url = "scene-thumbnails/%s/%s" % (self.id, "thumbnail.png")
		return url

	## Thumbnail
	thumbnail = models.ImageField(upload_to=key, blank=True, null=True)
	
	## Background
	background = models.ForeignKey('Background', related_name='scenes', related_query_name='scenes', blank=True, null=True)
	background_scale = models.DecimalField(decimal_places=2, max_digits=8, default=1.0)

	## Props
	props = models.ManyToManyField('Prop', through='SceneProp')

	## Story
	next_scene = models.ForeignKey('Scene', related_name='scenes', related_query_name='scenes', blank=True, null=True)

	def __unicode__(self):
		return self.name


class SceneProp(models.Model):

	## Relationships
	scene = models.ForeignKey('Scene')
	prop_file = models.ForeignKey('Prop')

	## Prop Information
	scale = models.DecimalField(decimal_places=2,max_digits=8, default=1.0)
	position_x = models.IntegerField(default=0)
	position_y = models.IntegerField(default=0)
	movable = models.BooleanField(default=False)
	index = models.IntegerField(default=500)
	rotation = models.DecimalField(decimal_places=2,max_digits=8, default=0.0)
	visible = models.BooleanField(default=False)
	always_visible = models.BooleanField(default=False)

	def __unicode__(self):
		return self.scene.name + " - " + self.prop_file.name


class Background(models.Model):

	## Metadata
	name = models.CharField(max_length=50)
	keyword = models.CharField(max_length=50, blank=True)
	description = models.CharField(max_length=500, blank=True)

	## Image Key
	def key(self, filename):
		url = "backgrounds/%s/%s" % (self.id, filename)
		return url

	## Image Data
	image = models.ImageField(upload_to=key)

	def __unicode__(self):
		return self.name


class Prop(models.Model):

	## Metadata
	name = models.CharField(max_length=50)
	keyword = models.CharField(max_length=50, blank=True)
	description = models.CharField(max_length=500, blank=True)

	## Image Key
	def key(self, filename):
		url = "props/%s/%s" % (self.id, filename)
		return url

	## Image Data
	image = models.ImageField(upload_to=key)

	def __unicode__(self):
		return self.name