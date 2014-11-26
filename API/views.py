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

def api(request):
	if request.method == "GET":
		return render(request, 'API/index.html')
	else:
		return HttpResponseNotAllowed(["GET"])

@csrf_exempt
def scenes(request):
	if request.method == "GET":
		# GET ALL - later
		try:
			domain = request.get_host()
			scenes = Scene.objects.all()
			response_data = { "scenes" : [], "success" : True }
			for scene in scenes:
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
				if scene.thumbnail is not None:
					scene_rep["thumbnail"] = scene.thumbnail.url
				if scene.background is not None:
					background = Background.objects.get(id=scene.background.id)
					scene_rep["background"] = {
						"id" : background.id,
						"name" : background.name,
						"description" : background.description,
						"url" : background.image.url
					}
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
							"scale" : float(scene_prop.scale),
							"index" : scene_prop.index,
							"rotation" : float(scene_prop.rotation)
						}
						scene_rep["props"].append(prop_rep)
				response_data["scenes"].append(scene_rep)
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
	elif request.method == "POST":
		# New Scene (Default Background Settings)
		try:
			data = json.loads(request.body)
			new_scene = Scene(name=data['name'], description=data['description'], background_scale=1.0)
			new_scene.save()
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
			response_data = {}
			scene_rep = {
				"id" : scene.id,
				"name" : scene.name,
				"version" : scene.version.isoformat(' '),
				"description" : scene.description,
				"background" : {
					"id" : "",
					"name" : "",
					"description" : "",
					"url" : "/static/editor/img/blank-background"
				},
				"background_scale" : float(scene.background_scale),
				"props" : []
			}
			if scene.thumbnail is not None:
				scene_rep["thumbnail"] = scene.thumbnail.url
			if scene.background is not None:
				background = Background.objects.get(id=scene.background.id)
				scene_rep["background"] = {
					"id" : background.id,
					"name" : background.name,
					"description" : background.description,
					"url" : background.image.url
				}
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
						"scale" : float(scene_prop.scale),
						"index" : scene_prop.index,
						"rotation" : float(scene_prop.rotation)
					}
					scene_rep["props"].append(prop_rep)
			response_data["scene"] = scene_rep
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		elif request.method == "PUT":
			# Update Scene
			scene = Scene.objects.get(id=scene_id)
			data = json.loads(request.body)
			if not data.has_key("update"):
				return HttpResponse(status=400)
			if not data["update"].has_key("type"):
				return HttpResponse(status=400)
			update = data["update"]
			if update["type"] == "META":
				# Name, Description, Version")
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
				if update.has_key("index") and update["index"] >= 500 and update["index"] <= 4000:
					scene_prop.index = update["index"]
				if update.has_key("rotation"):
					scene_prop.rotation = update["rotation"]
				scene_prop.save()
			else:
				return HttpResponse(status=400)
			scene.save()
			response_data = { "success" : True }
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		elif request.method == "DELETE":
			scene = Scene.objects.get(id=scene_id)
			# delete all scene_props from the scene
			scene_props = SceneProp.objects.filter(scene=scene)
			for scene_prop in scene_props:
				scene = scene_prop.scene
				scene_prop.delete()
				scene.save()
			# delete scene
			scene.delete()
			response_data = { "success" : True }
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		else:
			return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])
	except ObjectDoesNotExist:
		return HttpResponse(status=404)
	return HttpResponse(status=200)

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
						"scale" : float(scene_prop.scale),
						"index" : scene_prop.index,
						"rotation" : float(scene_prop.rotation)
					}
					response_data["scene"]["props"].append(obj)
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
	else:
		return HttpResponseNotAllowed('GET')
	return HttpResponse(scene_id)

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
def backgrounds(request):
	domain = request.get_host()
	if request.method == "GET":
		# GET MANY
		response_data = { "backgrounds" : [] }
		backgrounds = Background.objects.all()
		for background in backgrounds:
			obj = {
				"id" : background.id,
				"name" : background.name,
				"description" : background.description,
				"url" : background.image.url
			}
			response_data["backgrounds"].append(obj)
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	elif request.method == "POST":
		# NEW Background
		background_model = Background(name=request.POST.get("name"), description=request.POST.get("description"))
		background_model.image = request.FILES["background"]
		background_model.save()
		background_rep = { 
			"id" : background_model.id, 
			"name" :  background_model.name, 
			"description" : background_model.description, 
			"url" : background_model.image.url 
		}
		response_data = {
			"background" : background_rep,
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
				"background" : {
					"id" : background.id,
					"name" : background.name,
					"description" : background.description,
					"url" : background.image.url
				}
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

@csrf_exempt
def props(request):
	domain = request.get_host()
	if request.method == "GET":
		# GET ALL (NON-FORBIDDEN)
		response_data = { "props" : [] }
		props = Prop.objects.all()
		for prop in props:
			obj = {
				"id" : prop.id,
				"name" : prop.name,
				"description" : prop.description,
				"url" : prop.image.url
			}
			response_data["props"].append(obj)
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	elif request.method == "POST":
		# NEW Prop
		prop_model = Prop(name=request.POST.get("name"), description=request.POST.get("description"))
		prop_model.image = request.FILES["prop"]
		prop_model.save()
		prop_rep = {
			"id" : prop_model.id, 
			"name" :  prop_model.name, 
			"description" : prop_model.description,
			"url" : prop_model.image.url 
		}
		response_data = {
			"prop" : prop_rep,
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
				"prop" : {
					"id" : prop.id,
					"name" : prop.name,
					"description" : prop.description,
					"url" : prop.image.url
				}
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

def save_file(file, path=''):
	''' Little helper to save a file
	'''
	filename = file._get_name()
	ts = str(int(time.time()))
	absolute_path = '%s/%s%s-%s' % (settings.MEDIA_ROOT, str(path), ts, str(filename))
	fd = storage.open(absolute_path, 'wb')
	for chunk in file.chunks():
		fd.write(chunk)
	fd.close()
	return '%s-%s' % (ts, str(filename))