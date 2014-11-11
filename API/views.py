from django.shortcuts import render, render_to_response
from django.http import *
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.conf import settings
import json, os

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
					"version" : scene.version,
					"description" : scene.description,
					"background" : {},
					"background_scale" : float(scene.background_scale),
					"props" : []
				}
				if scene.background is not None:
					background = Background.objects.get(id=scene.background.id)
					scene_rep["background"] = {
						"id" : background.id,
						"name" : background.name,
						"description" : background.description,
						"url" : "http://" + domain + background.image.url
					}
				for scene_prop in SceneProp.objects.filter(scene=scene):
					prop = scene_prop.prop_file
					if prop is not None and scene_prop is not None:
						prop_rep = {
							"scene_prop_id" : scene_prop.id,
							"prop_id" : prop.id,
							"name" : prop.name,
							"description" : prop.description,
							"url" : "http://" + domain + prop.image.url,
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
			new_scene = Scene(name=data['name'], description=data['description'], version="1.0.0", background_scale=1.0)
			new_scene.save()
			response_data = {
				"success" : True,
				"scene" : {
					"id" : new_scene.id,
					"name" : new_scene.name,
					"description" : new_scene.description,
					"version" : new_scene.version,
					"background" : {
						"id" : "",
						"name" : "",
						"description" : "",
						"url" : ""
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
	if request.method == "GET":
		try:
			scene = Scene.objects.get(id=scene_id)
			response_data = {}
			response_data["scene"] = {
				"id" : scene.id,
				"name" : scene.name,
				"description" : scene.description,
				"version" : scene.version
			}
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			print "Scene does not exist"
			return HttpResponse("Scene does not exist")
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
			if update.has_key("version"):
				scene.version = update["version"]
			scene.save()
		elif update["type"] == "BACKGROUND":
			# Background (foreign key), Background Scale
			if update.has_key("background"):
				background = Background.objects.get(id=update["background"])
				scene.background = background
			if update.has_key("background_scale"):
				scene.background_scale = update["background_scale"]
			scene.save()
		elif update["type"] == "PROP":
			# SceneProp attributes
			try:
				scene_prop = SceneProp.objects.get(id=update["scene_prop"])
			except ObjectDoesNotExist:
				return HttpResponse(status=404)
			if update.has_key("scale"):
				scene_prop.scale = update["scale"]
			if update.has_key("position_x"):
				scene_prop.position_x = update["position_x"]
			if update.has_key("position_y"):
				scene_prop.position_y = update["position_y"]
			if update.has_key("index"):
				scene_prop.index = update["index"]
			if update.has_key("rotation"):
				scene_prop.rotation = update["rotation"]
			scene_prop.save()
		else:
			return HttpResponse(status=400)
	elif request.method == "DELETE":
		# DELETE - later
		pass
	else:
		return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])

	return HttpResponse("scene: " + scene_id)

@csrf_exempt
def scene_resources(request, scene_id):
	if request.method == "GET":
		try:
			domain = request.get_host()
			scene = Scene.objects.get(id=scene_id)
			response_data = {}
			response_data["scene"] = {
				"name" : scene.name,
				"version" : scene.version,
				"props" : []
			}
			if scene.background is not None:
				background = Background.objects.get(id=scene.background.id)
				response_data["scene"]["background"] = {
					"id" : background.id,
					"name" : background.name,
					"description" : background.description,
					"url" : "http://" + domain + background.image.url
				}
			scene_props = SceneProp.objects.filter(scene=scene)
			for scene_prop in scene_props:
				prop = scene_prop.prop_file
				if prop is not None:
					obj = {
						"id" : prop.id,
						"name" : prop.name,
						"description" : prop.description,
						"url" : "http://" + domain + prop.image.url
					}
					response_data["scene"]["props"].append(obj)
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			print "Scene does not exist"
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
				"version" : scene.version,
				"background" : "" ,
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
			print "Scene does not exist"
	else:
		return HttpResponseNotAllowed('GET')
	return HttpResponse(scene_id)

@csrf_exempt
def add_scene_background(request, scene_id):
	if request.method == "POST":
		print request.body
		data = json.loads(request.body)
		print data
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
						"url" : "http://" + request.get_host() + background.image.url
					} 
				}
				return HttpResponse(json.dumps(response_data), content_type="application/json")
			except ObjectDoesNotExist:
				print "Background does not exist"
		except ObjectDoesNotExist:
			print "Scene does not exist"
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
				response_data = {
					"success" : True,
					"prop" : {
						"scene_prop_id" : new_sceneprop.id,
						"name" : prop.name,
						"description" : prop.description,
						"url" : "http://" + request.get_host() + prop.image.url,
						"scale" : new_sceneprop.scale,
						"position_x" : new_sceneprop.position_x,
						"position_y" : new_sceneprop.position_y,
						"index" : new_sceneprop.index,
						"rotation" : new_sceneprop.rotation
					}
				}
				return HttpResponse(json.dumps(response_data), content_type="application/json")
			except ObjectDoesNotExist:
				print "Prop does not exist"
		except ObjectDoesNotExist:
			print "Scene does not exist"
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
			obj = {
				"id" : background.id,
				"name" : background.name,
				"description" : background.description,
				"url" : "http://" + domain + background.image.url
			}
			response_data["backgrounds"].append(obj)
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	elif request.method == "POST":
		# NEW Background
		background_model = Background(name=request.POST.get("name"), description=request.POST.get("description"), image=request.FILES["background"])
		background_model.save()
		background_rep = { 
			"id" : background_model.id, 
			"name" :  background_model.name, 
			"description" : background_model.description, 
			"url" : "http://" + domain + background_model.image.url 
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
			response_data = {}
			response_data["background"] = {
				"id" : background.id,
				"name" : background.name,
				"description" : background.description,
				"url" : "http://" + domain + background.image.url
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
		background.scene_set.clear()
		# Delete File
		if background.image:
			if background.image.path:
				os.remove(background.image.path)
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
				"url" : "http://" + domain + prop.image.url
			}
			response_data["props"].append(obj)
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	elif request.method == "POST":
		# NEW Background
		prop_model = Prop(name=request.POST.get("name"), description=request.POST.get("description"), image=request.FILES["prop"])
		prop_model.save()
		prop_rep = {
			"id" : prop_model.id, 
			"name" :  prop_model.name, 
			"description" : prop_model.description,
			"url" : "http://" + domain + prop_model.image.url 
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
			response_data = {}
			response_data["prop"] = {
				"id" : prop.id,
				"name" : prop.name,
				"description" : prop.description,
				"url" : "http://" + domain + prop.image.url
			}
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			print "Prop does not exist"
	elif request.method == "PUT":
		# PUT - UPDATE - later
		pass
	elif request.method == "DELETE":
		prop = Prop.objects.get(id=prop_id)
		# Unset From all scenes and delete scene_prop
		scenes = Scene.objects.filter(background=background)
		for scene in scenes:
			scene.props.remove(prop)
			scene_prop = SceneProp.objects.get(scene=scene,prop_file=prop)
			scene_prop.delete()
		# Delete File
		if prop.image:
			if prop.image.path:
				os.remove(prop.image.path)
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
	import time
	ts = str(int(time.time()))
	absolute_path = '%s/%s%s-%s' % (settings.MEDIA_ROOT, str(path), ts, str(filename))
	fd = open(absolute_path, 'wb')
	for chunk in file.chunks():
		fd.write(chunk)
	fd.close()
	return '%s-%s' % (ts, str(filename))