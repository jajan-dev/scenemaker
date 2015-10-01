from django.shortcuts import render, render_to_response
from django.http import *
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.conf import settings
from django.core.files.storage import default_storage as storage
from django.core.files.base import ContentFile
from boto.s3.connection import S3Connection, Bucket, Key
import json, os, time

from django.core.exceptions import ObjectDoesNotExist

from API.models import *

def asset_response(model):
	return {
		"id" : model.id,
		"name" : model.name,
		"description" : model.description,
		"url" : model.image.url
	}

@csrf_exempt
def add_scene_background(request, scene_id):
	if request.method == "POST":
		data = json.loads(request.body)
		try:
			scene = Scene.objects.get(id=scene_id)
			try:
				background_id = data["background"]
				background = Background.objects.get(id=background_id)
				scene.background = background
				scene.save()
				response_data = { 
					"success" : True,
					"background" : { 
						"id" : background_id, 
						"name" :  background.name,
						"description" : background.description,
						"url" : background.image.url
					} 
				}
				return HttpResponse(json.dumps(response_data), content_type="application/json")
			except ObjectDoesNotExist:
				return HttpResponse(status=404)
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
	else:
		return HttpResponseNotAllowed('POST')

@csrf_exempt
def backgrounds(request):
	domain = request.get_host()
	if request.method == "GET":
		# GET MANY
		response_data = { "backgrounds" : [] }
		backgrounds = Background.objects.all()
		for background in backgrounds:
			response_data["backgrounds"].append(asset_response(background))
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	elif request.method == "POST":
		# NEW Background
		background_model = Background(name=request.POST.get("name"), description=request.POST.get("description"))
		background_model.save()
		background_model.image = request.FILES["background"]
		background_model.save()
		response_data = {
			"background" : asset_response(background_model),
			"success" : True
		}
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	else:
		return HttpResponseNotAllowed(['GET', 'POST'])

@csrf_exempt
def background(request, background_id):
	domain = request.get_host()
	if request.method == "GET":
		# GET - READ
		try:
			background = Background.objects.get(id=background_id)
			response_data = {
				"success" : True,
				"background" : asset_response(background)
			}
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
	elif request.method == "PUT":
		# PUT - UPDATE - later
		pass
	elif request.method == "DELETE":
		background = Background.objects.get(id=background_id)
		# Unset From all scenes
		background.scenes.clear()
		# Delete File
		if background.image:
			if not settings.USE_AWS and background.image.path:
				# Delete from MEDIA_ROOT
				os.remove(background.image.path)
			elif settings.USE_AWS and background.image.name:
				# Delete from AWS S3
				connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
				bucket = Bucket(connection, settings.AWS_STORAGE_BUCKET_NAME)
				fileKey = Key(bucket)
				fileKey.key = background.image.name
				bucket.delete_key(fileKey)
		# Delete from database
		background.delete()
		response_data = { "success" : True }
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	else:
		return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])
	return HttpResponse("API call for background #" + background_id)

