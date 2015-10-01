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

'''
Jajan ScenePlayer API Method

Gets the resources (background and prop image information) for a given scene
@scene_id: the ID of the scene to obtain resource information for
'''
@csrf_exempt
def scene_resources(request, scene_id):
	if request.method == "GET":
		try:
			domain = request.get_host()
			scene = Scene.objects.get(id=scene_id)
			response_data = {}
			response_data["scene"] = {
				"name" : scene.name,
				"version" : scene.version.isoformat(' '),
				"props" : []
			}
			if scene.thumbnail is not None:
				response_data["scene"]["thumbnail"] = scene.thumbnail.url
			if scene.background is not None:
				background = Background.objects.get(id=scene.background.id)
				response_data["scene"]["background"] = {
					"id" : background.id,
					"name" : background.name,
					"description" : background.description,
					"url" : background.image.url
				}
			scene_props = SceneProp.objects.filter(scene=scene)
			for scene_prop in scene_props:
				prop = scene_prop.prop_file
				if prop is not None:
					obj = {
						"id" : prop.id,
						"name" : prop.name,
						"description" : prop.description,
						"url" : prop.image.url
					}
					response_data["scene"]["props"].append(obj)
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
	else:
		return HttpResponseNotAllowed('GET')
	return HttpResponse(scene_id)

'''
Jajan ScenePlayer API Method

Gets the placement (background and prop geometric information) for a given scene
@scene_id: the ID of the scene to obtain resource information for
'''
@csrf_exempt
def scene_placement(request, scene_id):
	if request.method == "GET":
		try:
			domain = request.get_host()
			scene = Scene.objects.get(id=scene_id)
			response_data = {}
			response_data["scene"] = {
				"name" : scene.name,
				"version" : scene.version.isoformat(' '),
				"background" : {
					"id" : "",
					"name" : "",
					"position-x" : 0,
					"position-y" : 0,
					"scale" : 1.0
				},
				"props" : []
			}
			if scene.background is not None:
				background = Background.objects.get(id=scene.background.id)
				response_data["scene"]["background"] = {
					"id" : background.id,
					"name" : background.name,
					"position-x" : 0,
					"position-y" : 0,
					"scale" : float(scene.background_scale)
				}
			scene_props = SceneProp.objects.filter(scene=scene)
			for scene_prop in scene_props:
				prop = scene_prop.prop_file
				if prop is not None:
					obj = {
						"id" : prop.id,
						"name" : prop.name,
						"position-x" : scene_prop.position_x,
						"position-y" : scene_prop.position_y,
						"movable" : scene_prop.movable,
						"scale" : float(scene_prop.scale),
						"index" : scene_prop.index,
						"rotation" : float(scene_prop.rotation),
						"visible" : scene_prop.visible,
						"always_visible" : scene_prop.always_visible
					}
					response_data["scene"]["props"].append(obj)
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
	else:
		return HttpResponseNotAllowed('GET')
	return HttpResponse(scene_id)

