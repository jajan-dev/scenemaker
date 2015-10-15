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
	response = {
		"id" : model.id,
		"name" : model.name,
		"description" : model.description,
		"url" : model.image.url
	}
	response["thumbnail"] = model.thumbnail.url
	return response

@csrf_exempt
def add_scene_prop(request, scene_id):
	if request.method == "POST":
		data = json.loads(request.body)
		try:
			scene = Scene.objects.get(id=scene_id)
			try:
				prop_id = data["prop"]
				prop = Prop.objects.get(id=prop_id)
				new_sceneprop = SceneProp(scene=scene, prop_file=prop)
				new_sceneprop.save()
				scene.save()
				response_data = {
					"success" : True,
					"prop" : {
						"scene_prop_id" : new_sceneprop.id,
						"name" : prop.name,
						"description" : prop.description,
						"url" : prop.image.url,
						"scale" : new_sceneprop.scale,
						"position_x" : new_sceneprop.position_x,
						"position_y" : new_sceneprop.position_y,
						"index" : new_sceneprop.index,
						"rotation" : new_sceneprop.rotation
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
def scene_prop(request, scene_prop_id):
	if request.method == "DELETE":
		try:
			scene_prop = SceneProp.objects.get(id=scene_prop_id)
			scene = scene_prop.scene
			scene_prop.delete()
			scene.save()
			response_data = { "success" : True }
			return HttpResponse(json.dumps(response_data), content_type="application/json")

		except ObjectDoesNotExist:
			return HttpResponse(status=404)
	else:
		return HttpResponseNotAllowed('DELETE')

@csrf_exempt
def props(request):
	domain = request.get_host()
	if request.method == "GET":
		# GET ALL (NON-FORBIDDEN)
		response_data = { "props" : [] }
		props = Prop.objects.all()
		for prop in props:
			response_data["props"].append(asset_response(prop))
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	elif request.method == "POST":
		# NEW Prop
		prop_model = Prop(name=request.POST.get("name"), description=request.POST.get("description"))
		prop_model.save()
		prop_model.image = request.FILES["prop"]
		prop_model.save()
		response_data = {
			"prop" : asset_response(prop_model),
			"success" : True
		}
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	else:
		return HttpResponseNotAllowed(['GET', 'POST'])

@csrf_exempt
def prop(request, prop_id):
	if request.method == "GET":
		domain = request.get_host()
		# GET - READ
		try:
			prop = Prop.objects.get(id=prop_id)
			response_data = {
				"success" : True,
				"prop" : asset_response(prop)
			}
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
	elif request.method == "PUT":
		# PUT - UPDATE - later
		pass
	elif request.method == "DELETE":
		prop = Prop.objects.get(id=prop_id)
		# Unset From all scenes and delete scene_prop
		scene_props = SceneProp.objects.filter(prop_file=prop)
		for scene_prop in scene_props:
			scene = scene_prop.scene
			scene_prop.delete()
			scene.save()
		# Delete File
		if prop.image:
			if not settings.USE_AWS and prop.image.path:
				# Delete from MEDIA_ROOT
				os.remove(prop.image.path)
			elif settings.USE_AWS and prop.image.name:
				# Delete from AWS S3
				connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
				bucket = Bucket(connection, settings.AWS_STORAGE_BUCKET_NAME)
				fileKey = Key(bucket)
				fileKey.key = prop.image.name
				bucket.delete_key(fileKey)
		# Delete From Database
		prop.delete()
		response_data = { "success" : True }
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	else:
		return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])
	return HttpResponse("API call for prop #" + prop_id)

def props_by_name(request):
	if request.method == "GET":
		try:
			response_data = []
			name = request.GET.get('name','')
			if name == '':
				return HttpResponse(json.dumps(response_data), content_type="application/json")
			props = Prop.objects.filter(name=name)
			for prop in props:
				response_data.append(asset_response(prop))
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
	else:
		return HttpResponseNotAllowed(['GET'])

