from django.shortcuts import render, render_to_response
from django.http import *
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import json

from django.core.exceptions import ObjectDoesNotExist

from API.models import *

def api(request):
	if request.method == "GET":
		return render(request, 'api/index.html')
	else:
		return HttpResponseNotAllowed(["GET"])

@csrf_exempt
def scenes(request):
	if request.method == "GET":
		# GET ALL (NON-FORBIDDEN)
		return HttpResponse("Scenes Search : For Later...")
	elif request.method == "POST":
		# POST - CREATE
		try:
			data = json.loads(request.body)
			new_scene = Scene(name=data['name'], description=data['description'], version="1.0.0")
			response_data = { "id" : new_scene.id }
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except Exception:
			return HttpResponse("Something went wrong while trying to create a new scene")

@csrf_exempt
def scene(request, scene_id):
	if request.method == "GET":
		# GET - READ
		try:
			scene = Scene.objects.get(id=scene_id)
			response_data = {}
			response_data["scene"] = {"id" : scene.id, "name" : scene.name, "description" : scene.description, "version" : scene.version}
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			print "Scene does not exist"
			return HttpResponse("Scene does not exist")
	elif request.method == "PUT":
		# PUT - UPDATE - TODO
		pass
	elif request.method == "DELETE":
		# DELETE - DELETE - TODO
		pass
	else:
		return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])

	return HttpResponse("scene: " + scene_id)

@csrf_exempt
def scene_resources(request, scene_id):
	if request.method == "GET":
		try:
			scene = Scene.objects.get(id=scene_id)
			response_data = {}
			response_data["scene"] = { "name" : scene.name, "version" : scene.version, "background" : "" , "props" : []}
			background = Background.objects.get(id=scene.background.id)
			response_data["scene"]["background"] = { "id" : background.id, "name" : background.name, "description" : background.description, "url" : background.image.url }
			scene_props = SceneProp.objects.filter(scene=scene)
			for scene_prop in scene_props:
				prop = scene_prop.prop_file
				obj = { "id" : prop.id, "name" : prop.name, "description" : prop.description, "url" : prop.image.url}
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
			scene = Scene.objects.get(id=scene_id)
			response_data = {}
			response_data["scene"] = { "name" : scene.name, "version" : scene.version, "background" : "" , "props" : []}
			background = Background.objects.get(id=scene.background.id)
			response_data["scene"]["background"] = { "id" : background.id, "name" : background.name, "position-x" : 0, "position-y" : 0, "scale" : float(scene.background_scale)}
			scene_props = SceneProp.objects.filter(scene=scene)
			for scene_prop in scene_props:
				prop = scene_prop.prop_file
				obj = { "id" : prop.id, "name" : prop.name, "position-x" : scene_prop.position_x, "position-y" : scene_prop.position_y, "scale" : float(scene_prop.scale), "index" : scene_prop.index, "rotation" : float(scene_prop.rotation) }
				response_data["scene"]["props"].append(obj)
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			print "Scene does not exist"
	else:
		return HttpResponseNotAllowed('GET')
	return HttpResponse(scene_id)

@csrf_exempt
def backgrounds(request):
	if request.method == "GET":
		# GET ALL (NON-FORBIDDEN)
		response_data = { "backgrounds" : [] }
		backgrounds = Background.objects.all()
		for background in backgrounds:
			obj = { "id" : background.id, "name" : background.name, "description" : background.description, "url" : background.image.url }
			response_data["backgrounds"].append(obj)
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	return HttpResponse("backgrounds")

@csrf_exempt
def background(request, background_id):
	if request.method == "GET":
		# GET - READ
		try:
			background = Background.objects.get(id=background_id)
			response_data = {}
			response_data["background"] = { "id" : background.id, "name" : background.name, "description" : background.description, "url" : background.image.url }
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			print "Background does not exist"
	elif request.method == "PUT":
		# PUT - UPDATE - TODO
		pass
	elif request.method == "DELETE":
		# DELETE - DELETE - TODO
		pass
	else:
		return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])
	return HttpResponse("API call for background #" + background_id)

@csrf_exempt
def props(request):
	if request.method == "GET":
		# GET ALL (NON-FORBIDDEN)
		response_data = { "props" : [] }
		props = Prop.objects.all()
		for prop in props:
			obj = { "id" : prop.id, "name" : prop.name, "description" : prop.description, "url" : prop.image.url }
			response_data["props"].append(obj)
		return HttpResponse(json.dumps(response_data), content_type="application/json")
		pass
	return HttpResponse("props")

@csrf_exempt
def prop(request, prop_id):
	if request.method == "GET":
		# GET - READ
		try:
			prop = Prop.objects.get(id=prop_id)
			response_data = {}
			response_data["prop"] = { "id" : prop.id, "name" : prop.name, "description" : prop.description, "url" : prop.image.url }
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		except ObjectDoesNotExist:
			print "Prop does not exist"
	elif request.method == "PUT":
		# PUT - UPDATE - TODO
		pass
	elif request.method == "DELETE":
		# DELETE - DELETE - TODO
		pass
	else:
		return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])
	return HttpResponse("API call for prop #" + prop_id)