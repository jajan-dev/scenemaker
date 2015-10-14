from django import forms
from django.db import models
from PIL import Image, ImageDraw
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

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

	def thumbnail_key(self, filename):
		url = "background-thumbnails/%s/%s" % (self.id, "thumbnail.png")
		return url

	def set_thumbnail(self, image):
		self.thumbnail = image
		size = (128, 72)
		self.thumbnail.file.seek(0)
		img = Image.open(StringIO(self.thumbnail.file.read()))
		img.thumbnail(size, Image.ANTIALIAS)
		new_width = img.width
		new_height = img.height
		format = img.format
		img = img.crop((0, 0, 128, 72))
		draw = ImageDraw.Draw(img)
		if new_width < 128:
			# Fill remaining horizontal section with white
			draw.rectangle((new_width, 0, 128, 72), fill='white')
		if new_height < 72:
			# Fill remaining vertical section with white
			draw.rectangle((0, new_height, 128, 72), fill='white')
		del draw
		imageString = StringIO()
		img.save(imageString, format)

		c_type = self.thumbnail.file.content_type.replace('images', 'image')
		imf = InMemoryUploadedFile(imageString, None, self.thumbnail.name, c_type, imageString.len, None)
		imf.seek(0)
		self.thumbnail.save(
				self.thumbnail.name,
				imf,
				save=False
			)

	## Image Data
	image = models.ImageField(upload_to=key)
	thumbnail = models.ImageField(upload_to=thumbnail_key, default="background-thumbnails/default/thumbnail.png")

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

	def thumbnail_key(self, filename):
		url = "prop-thumbnails/%s/%s" % (self.id, "thumbnail.png")
		return url

	## Image Data
	image = models.ImageField(upload_to=key)

	def __unicode__(self):
		return self.name