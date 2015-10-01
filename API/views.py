from django.shortcuts import render
from django.http import *
from django.conf import settings

from API.models import *

def api(request):
	if request.method == "GET":
		return render(request, 'API/index.html')
	else:
		return HttpResponseNotAllowed(["GET"])
