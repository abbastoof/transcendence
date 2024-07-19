from django.urls import path

from .views import RegisterViewSet, UserViewSet, FriendsViewSet
from .user_session_views import UserLoginView, UserLogoutView

urlpatterns = [
    path("user/register/",RegisterViewSet.as_view({"post": "create_user",}),name="register-user",),
    path("user/",UserViewSet.as_view({"get": "users_list",}),name="users-list",),
    path("user/login/",UserLoginView.as_view({"post": "login",}),name="user-login",),
    path("user/<int:pk>/",UserViewSet.as_view({"get": "retrieve_user","put": "update_user","delete": "destroy_user",}),name="user-detail",),
    path("user/<int:pk>/logout/", UserLogoutView.as_view({"post": "logout",}),name="user-logout",),
    path("user/<int:user_pk>/friends/", FriendsViewSet.as_view({"get": "friends_list"}), name="friends-list"),
    path("user/<int:user_pk>/friends/<int:pk>/", FriendsViewSet.as_view({"put": "accept_friend_request", "post": "send_friend_request"}), name="friends-request"),
    path("user/<int:user_pk>/pending/", FriendsViewSet.as_view({"get": "friend_requests"}), name="friend_request-list"),
    path("user/<int:user_pk>/pending/<int:pk>", FriendsViewSet.as_view({"put": "reject_friend_request"}), name="reject-request"),
    path("user/<int:user_pk>/friends/<int:pk>/remove/", FriendsViewSet.as_view({"delete": "remove_friend"}), name="remove-friend"),
]
