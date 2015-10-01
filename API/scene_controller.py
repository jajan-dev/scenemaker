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

def scene_response(scene):
	# The scene response to return
	scene_rep = {
		"id" : scene.id,
		"name" : scene.name,
		"version" : scene.version.isoformat(' '),
		"description" : scene.description,
		"background" : {
			"id" : "",
			"name" : "",
			"description" : "",
			"url" : "/static/editor/img/blank-background.jpg"
		},
		"background_scale" : float(scene.background_scale),
		"props" : []
	}
	# Get the thumbnail for the scene
	if scene.thumbnail is not None:
		try:
			scene_rep["thumbnail"] = scene.thumbnail.url
		except ValueError:
			scene_rep["thumbnail"] = None
	# Get the background for the scene
	if scene.background is not None:
		background = Background.objects.get(id=scene.background.id)
		scene_rep["background"] = {
			"id" : background.id,
			"name" : background.name,
			"description" : background.description,
			"url" : background.image.url
		}
	# Get all the props in the scene
	for scene_prop in SceneProp.objects.filter(scene=scene):
		prop = scene_prop.prop_file
		if prop is not None and scene_prop is not None:
			prop_rep = {
				"scene_prop_id" : scene_prop.id,
				"prop_id" : prop.id,
				"name" : prop.name,
				"description" : prop.description,
				"url" : prop.image.url,
				"position_x" : scene_prop.position_x,
				"position_y" : scene_prop.position_y,
				"movable" : scene_prop.movable,
				"scale" : float(scene_prop.scale),
				"index" : scene_prop.index,
				"rotation" : float(scene_prop.rotation),
				"visible" : scene_prop.visible,
				"always_visible" : scene_prop.always_visible
			}
			scene_rep["props"].append(prop_rep)

	return scene_rep

def create_new_scene(data):
	# Create a new scene model (default background scale)
	new_scene = Scene(name=data['name'], description=data['description'], background_scale=1.0)
	# Add thumbnail for new scene
	decoded_image = data["thumbnail"].decode('base64')
	new_scene.thumbnail = ContentFile(decoded_image, "thumbnail.png")
	# Insert new scene into database
	new_scene.save()
	# Generate new scene response
	response_data = {
		"success" : True,
		"scene" : {
			"id" : new_scene.id,
			"name" : new_scene.name,
			"description" : new_scene.description,
			"version" : new_scene.version.isoformat(' '),
			"background" : {
				"id" : "",
				"name" : "",
				"description" : "",
				"url" : "/static/editor/img/blank-background.jpg"
			},
			"background_scale" : new_scene.background_scale,
			"props" : []
		}
	}
	return response_data

def update_scene(scene, data):
	if not data.has_key("update"):
		return HttpResponse(status=400)
	if not data["update"].has_key("type"):
		return HttpResponse(status=400)
	update = data["update"]
	if update["type"] == "META":
		# Name, Description, Version
		if update.has_key("name"):
			scene.name = update["name"]
		if update.has_key("description"):
			scene.description = update["description"]
	elif update["type"] == "SCENE":
		if update.has_key("thumbnail"):
			decoded_image = update["thumbnail"].decode('base64')
			scene.thumbnail = ContentFile(decoded_image, "thumbnail.png")
	elif update["type"] == "BACKGROUND":
		# Background Scale
		if update.has_key("background_scale") and update["background_scale"] >= 0:
			scene.background_scale = update["background_scale"]
	elif update["type"] == "PROP":
		# SceneProp attributes
		try:
			if update.has_key("scene_prop"):
				scene_prop = SceneProp.objects.get(id=update["scene_prop"])
			else:
				return HttpResponse(status=400)
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
		if update.has_key("scale") and update["scale"] >= 0:
			scene_prop.scale = update["scale"]
		if update.has_key("position_x"):
			scene_prop.position_x = update["position_x"]
		if update.has_key("position_y"):
			scene_prop.position_y = update["position_y"]
		if update.has_key("movable"):
			scene_prop.movable = update["movable"]
		if update.has_key("index") and update["index"] >= 500 and update["index"] <= 4000:
			scene_prop.index = update["index"]
		if update.has_key("rotation"):
			scene_prop.rotation = update["rotation"]
		if update.has_key("visible"):
			scene_prop.visible = update["visible"]
		if update.has_key("always_visible"):
			scene_prop.always_visible = update["always_visible"]
		scene_prop.save()
	else:
		return HttpResponse(status=400)
	scene.save()

def delete_scene(scene):
	# Delete all scene props in the scene
	scene_props = SceneProp.objects.filter(scene=scene)
	for scene_prop in scene_props:
		scene = scene_prop.scene
		scene_prop.delete()
		scene.save()
	# Delete the scene itself
	scene.delete()

@csrf_exempt
def scenes(request):
	if request.method == "GET":
		# GET ALL Scenes
		try:
			# Get Objects from newest to oldest
			scenes = Scene.objects.order_by('-version')
			response_data = { "scenes" : [], "success" : True }
			# Iterate over ALL scenes
			for scene in scenes:
				response_data["scenes"].append(scene_response(scene))
			# Return a list of all scenes
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
	elif request.method == "POST":
		# CREATE a single new scene
		try:
			# Get new scene information
			data = json.loads(request.body)
			# Return new scene response
			response_data = create_new_scene(data)
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except Exception:
			return HttpResponse(status=500)
	else:
		return HttpResponseNotAllowed(['GET', 'POST'])

@csrf_exempt
def scene(request, scene_id):
	try:
		scene = Scene.objects.get(id=scene_id)
		if request.method == "GET":
			# GET a single scene
			response_data = {}
			response_data["scene"] = scene_response(scene)
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		elif request.method == "PUT":
			# UPDATE a single scene
			data = json.loads(request.body)
			update_scene(scene, data)
			response_data = { "success" : True }
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		elif request.method == "DELETE":
			# DELETE a single scene
			delete_scene(scene)
			response_data = { "success" : True }
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		else:
			return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])
	except ObjectDoesNotExist:
		return HttpResponse(status=404)
	return HttpResponse(status=200)

