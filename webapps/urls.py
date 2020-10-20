"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from socialnetwork import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.global_stream, name='home'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('follower', views.follower_stream, name='follower'),
    path('profile', views.profile, name='profile'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('photo/<int:id>', views.get_photo, name='photo'),
    path('user_profile/<int:id>', views.get_profile, name='user_profile'),
    path('follow_unfollow/<int:id>', views.follow_unfollow, name='follow_unfollow'),
    path('create_post', views.create_post, name='create_post'),
    path('socialnetwork/refresh-global', views.refreshGlobal, name='refresh-global'),
    path('socialnetwork/refresh-follower', views.refreshFollower, name='refresh-follower'),
    path('socialnetwork/add-comment', views.addComment, name='add-comment'),
]
