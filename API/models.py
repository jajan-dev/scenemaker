from django.db import models

class Scene(models.Model):
	
	## Metadata
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=500)
	version = models.CharField(max_length=16)
	
	## Background
	background = models.ForeignKey('Background', related_name='scene', related_query_name='scene')
	background_scale = models.DecimalField(decimal_places=2,max_digits=8)

	## Props
	props = models.ManyToManyField('Prop', through='SceneProp')


class SceneProp(models.Model):

	## Relationships
	scene = models.ForeignKey('Scene')
	prop_file = models.ForeignKey('Prop')

	## Image Information
	scale = models.DecimalField(decimal_places=2,max_digits=8)
	position_x = models.IntegerField()
	position_y = models.IntegerField()
	index = models.IntegerField()
	rotation = models.DecimalField(decimal_places=2,max_digits=8)


class Background(models.Model):

	## Metadata
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=500)

	## Image Data
	image = models.ImageField(upload_to='backgrounds')


class Prop(models.Model):

	## Metadata
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=500)

	## Image Data
	image = models.ImageField(upload_to='props')