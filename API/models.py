from django import forms
from django.db import models

class Scene(models.Model):
	
	## Metadata
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=500, blank=True)
	version = models.DateTimeField(auto_now=True)

	## Thumbnail
	thumbnail = models.ImageField(upload_to='scene-thumbnails/', blank=True, null=True)
	
	## Background
	background = models.ForeignKey('Background', related_name='scenes', related_query_name='scenes', blank=True, null=True)
	background_scale = models.DecimalField(decimal_places=2, max_digits=8, default=1.0)

	## Props
	props = models.ManyToManyField('Prop', through='SceneProp')


class SceneProp(models.Model):

	## Relationships
	scene = models.ForeignKey('Scene')
	prop_file = models.ForeignKey('Prop')

	## Prop Information
	scale = models.DecimalField(decimal_places=2,max_digits=8, default=1.0)
	position_x = models.IntegerField(default=0)
	position_y = models.IntegerField(default=0)
	index = models.IntegerField(default=500)
	rotation = models.DecimalField(decimal_places=2,max_digits=8, default=0.0)


class Background(models.Model):

	## Metadata
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=500, blank=True)

	## Image Data
	image = models.ImageField(upload_to='backgrounds/')


class Prop(models.Model):

	## Metadata
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=500, blank=True)

	## Image Data
	image = models.ImageField(upload_to='props/')