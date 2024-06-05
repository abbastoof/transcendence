from django.urls import path
from .views import RegisterViewSet

urlpatterns = [
	path('users', RegisterViewSet.as_view({
		'get' : 'list',
		'post': 'create',
	})),

	path('users/<str:pk>', RegisterViewSet.as_view({
		'get': 'retrieve',
		'put': 'update',
		'delete': 'destroy',
	})),
]
