from django.conf.urls import patterns, include, url

from API import views

urlpatterns = patterns('',
	url(r'^$', views.api),
	url(r'^scenes/resources/(?P<scene_id>\d+)', views.scene_resources, name='scene_resources'),
	url(r'^scenes/placement/(?P<scene_id>\d+)', views.scene_placement, name='scene_placement'),
	url(r'^scenes/(?P<scene_id>\d+)/background/set', views.add_scene_background, name='add_scene_background'),
	url(r'^scenes/(?P<scene_id>\d+)/props/add', views.add_scene_prop, name='add_scene_prop'),
	url(r'^scenes/(?P<scene_id>\d+)', views.scene, name='scene'),
	url(r'^scenes', views.scenes, name='scenes'),
	url(r'^backgrounds/(?P<background_id>\d+)', views.background, name='background'),
	url(r'^backgrounds', views.backgrounds, name='backgrounds'),
	url(r'^props/(?P<prop_id>\d+)', views.prop, name='prop'),
	url(r'^props', views.props, name='props'),
)