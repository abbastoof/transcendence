from django.urls import path
from .views import RegisterViewSet, UserViewSet

urlpatterns = [
	path('user', RegisterViewSet.as_view({
		'post': 'create_user',
	})),
	path('user', UserViewSet.as_view({
		'get' : 'users_list',
	})),
	path('user/<int:pk>', UserViewSet.as_view({
		'get': 'retrieve_user',
		'put': 'update_user',
		'delete': 'destroy_user',
	})),
]
