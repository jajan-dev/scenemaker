from django import forms
from django.db import models
from PIL import Image, ImageDraw
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
import os

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

	def restore_name(self):
		name = self.image.name.split("/")[-1]
		self.image.name = self.key(name)

	def generate_thumbnail(self):
		# original code for this method came from
		# http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

		# If there is no image associated with this.
		# do not create thumbnail
		if not self.image:
			return

		# Set our max thumbnail size in a tuple (max width, max height)
		THUMBNAIL_SIZE = (128, 72)

		DJANGO_TYPE = "image/png"
		PIL_TYPE = "png"
		FILE_EXTENSION = 'png'

		# Open original photo which we want to thumbnail using PIL's Image
		image = Image.open(StringIO(self.image.read()))

		# We use our PIL Image object to create the thumbnail, which already
		# has a thumbnail() convenience method that contrains proportions.
		# Additionally, we use Image.ANTIALIAS to make the image look better.
		# Without antialiasing the image pattern artifacts may result.
		image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

		new_width = image.size[0]
		new_height = image.size[0]
		image = image.crop((0, 0, 128, 72))
		draw = ImageDraw.Draw(image)
		if new_width < 128:
			# Fill remaining horizontal section with white
			draw.rectangle((new_width, 0, 128, 72), fill='white')
		if new_height < 72:
			# Fill remaining vertical section with white
			draw.rectangle((0, new_height, 128, 72), fill='white')
		del draw

		# Save the thumbnail
		temp_handle = StringIO()
		image.save(temp_handle, PIL_TYPE)
		temp_handle.seek(0)

		# Save image to a SimpleUploadedFile which can be saved into
		# ImageField
		suf = SimpleUploadedFile(os.path.split(self.image.name)[-1],
				temp_handle.read(), content_type="image/png")
		# Save SimpleUploadedFile into image field
		self.thumbnail.save(
			'%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
			suf,
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

	def generate_thumbnail(self):
		# original code for this method came from
		# http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

		# If there is no image associated with this.
		# do not create thumbnail
		if not self.image:
			return

		# Set our max thumbnail size in a tuple (max width, max height)
		THUMBNAIL_SIZE = (72, 72)

		DJANGO_TYPE = "image/png"
		PIL_TYPE = "png"
		FILE_EXTENSION = 'png'

		# Open original photo which we want to thumbnail using PIL's Image
		image = Image.open(StringIO(self.image.read()))

		# We use our PIL Image object to create the thumbnail, which already
		# has a thumbnail() convenience method that contrains proportions.
		# Additionally, we use Image.ANTIALIAS to make the image look better.
		# Without antialiasing the image pattern artifacts may result.
		image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

		new_width = image.size[0]
		new_height = image.size[0]
		image = image.crop((0, 0, 72, 72))
		draw = ImageDraw.Draw(image)
		if new_width < 72:
			# Fill remaining horizontal section with white
			draw.rectangle((new_width, 0, 72, 72), fill='white')
		if new_height < 72:
			# Fill remaining vertical section with white
			draw.rectangle((0, new_height, 72, 72), fill='white')
		del draw

		# Save the thumbnail
		temp_handle = StringIO()
		image.save(temp_handle, PIL_TYPE)
		temp_handle.seek(0)

		# Save image to a SimpleUploadedFile which can be saved into
		# ImageField
		suf = SimpleUploadedFile(os.path.split(self.image.name)[-1],
				temp_handle.read(), content_type="image/png")
		# Save SimpleUploadedFile into image field
		self.thumbnail.save(
			'%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
			suf,
			save=False
		)

	## Image Data
	image = models.ImageField(upload_to=key)
	thumbnail = models.ImageField(upload_to=thumbnail_key, default="prop-thumbnails/default/thumbnail.png")

	def __unicode__(self):
		return self.name