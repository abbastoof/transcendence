from django.urls import path

from .views import RegisterViewSet, UserViewSet, FriendsViewSet
from .user_session_views import UserLoginView, UserLogoutView

urlpatterns = [
    path("user/register/",RegisterViewSet.as_view({"post": "create_user",}),name="user-register",),
    path("user/register/sendemailotp/",RegisterViewSet.as_view({"post": "send_email_otp",}),name="send-email-otp",),
    path("user/register/verifyemailotp/",RegisterViewSet.as_view({"post": "verify_email_otp",}),name="verify-email-otp",),
    path("user/register/availableuser/",RegisterViewSet.as_view({"post": "available_username_email",}),name="available-user-obj",),
    path("user/",UserViewSet.as_view({"get": "users_list",}),name="users-list",),
    path("user/login/",UserLoginView.as_view({"post": "login",}),name="user-login",),
    path("user/login/verifyotp/",UserLoginView.as_view({"post": "verify_otp",}),name="verify-otp",),
    path("user/<int:pk>/",UserViewSet.as_view({"get": "retrieve_user","patch": "update_user","delete": "destroy_user",}),name="user-detail",),
    path("user/<int:pk>/logout/", UserLogoutView.as_view({"post": "logout",}),name="user-logout",),
    path("user/<int:user_pk>/friends/", FriendsViewSet.as_view({"get": "friends_list"}), name="friends-list"),
    path("user/<int:user_pk>/request/", FriendsViewSet.as_view({"post": "send_friend_request"}), name="send-request"),
    path("user/<int:user_pk>/accept/<int:pk>/", FriendsViewSet.as_view({"put": "accept_friend_request"}), name="accept-request"),
    path("user/<int:user_pk>/pending/", FriendsViewSet.as_view({"get": "friend_requests"}), name="friend-request-list"),
    path("user/<int:user_pk>/reject/<int:pk>/", FriendsViewSet.as_view({"put": "reject_friend_request"}), name="reject-request"),
    path("user/<int:user_pk>/friends/<int:pk>/remove/", FriendsViewSet.as_view({"delete": "remove_friend"}), name="remove-friend"),
]
