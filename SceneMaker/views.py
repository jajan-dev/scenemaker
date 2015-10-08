from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

def index(request):
	return render(request, 'editor/editor.html', { 'SCENEMAKER_URL' : settings.SCENEMAKER_URL })

def login(request):
	return HttpResponse("Login")

def logout(request):
	return HttpResponse("Logout")

def signup(request):
	return HttpResponse("Signup")