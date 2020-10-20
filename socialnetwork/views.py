import json

from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from socialnetwork.forms import LoginForm, RegisterForm, ProfileForm, PostForm
from socialnetwork.models import Profile, Post, Comment


@login_required
@ensure_csrf_cookie
def refreshGlobal(request):
    postList = []
    for post in reversed(Post.objects.all().order_by('post_date_time')):
        newPost = {
            'id': post.id,
            'post_text': post.post_text,
            'post_date_time': post.post_date_time.isoformat(),
            'name': post.user.first_name + ' ' + post.user.last_name,
            'user_id': post.user.id
        }
        postList.append(newPost)

    commentList = []
    for comment in Comment.objects.all().order_by('comment_date_time'):
        newComment = {
            'id': comment.id,
            'comment_text': comment.comment_text,
            'comment_date_time': comment.comment_date_time.isoformat(),
            'post_id': comment.post.id,
            'name': comment.user.first_name + ' ' + comment.user.last_name,
            'user_id': comment.user.id
        }
        commentList.append(newComment)

    response_data = {'posts': postList, 'comments': commentList}
    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')


@login_required
@ensure_csrf_cookie
def refreshFollower(request):
    loginUser = Profile.objects.get(user=request.user)
    followingUser = []
    for i in range(loginUser.follows.count()):
        followingUser.append(loginUser.follows.all()[i].user)
    followingPost = Post.objects.filter(user__in=followingUser)

    postList = []
    for post in reversed(Post.objects.filter(user__in=followingUser).order_by('post_date_time')):
        newPost = {
            'id': post.id,
            'post_text': post.post_text,
            'post_date_time': post.post_date_time.isoformat(),
            'name': post.user.first_name + ' ' + post.user.last_name,
            'user_id': post.user.id
        }
        postList.append(newPost)

    commentList = []
    for comment in Comment.objects.filter(post__in=followingPost).order_by('comment_date_time'):
        newComment = {
            'id': comment.id,
            'comment_text': comment.comment_text,
            'comment_date_time': comment.comment_date_time.isoformat(),
            'post_id': comment.post.id,
            'name': comment.user.first_name + ' ' + comment.user.last_name,
            'user_id': comment.user.id
        }
        commentList.append(newComment)

    response_data = {'posts': postList, 'comments': commentList}
    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')


@login_required
def addComment(request):
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)

    if 'comment_text' not in request.POST or not request.POST['comment_text']:
        return _my_json_error_response("You must enter text to add comment.")

    if 'post_id' not in request.POST or not request.POST['post_id']:
        return _my_json_error_response("Invalid post id.", status=404)

    post_id = request.POST['post_id']
    try:
        int(post_id)
    except ValueError:
        return _my_json_error_response("Invalid post id format.", status=404)

    post = Post.objects.get(id=post_id)
    newComment = Comment(comment_text=request.POST['comment_text'],
                         comment_date_time=timezone.now(),
                         post=post,
                         user=request.user)
    newComment.save()

    response_data = []
    for comment in Comment.objects.all().order_by('comment_date_time'):
        newComment = {
            'id': comment.id,
            'comment_text': comment.comment_text,
            'comment_date_time': comment.comment_date_time.isoformat(),
            'post_id': comment.post.id,
            'name': comment.user.first_name + ' ' + comment.user.last_name,
            'user_id': comment.user.id
        }
        response_data.append(newComment)

    response_json = json.dumps(response_data)
    return HttpResponse(response_json, content_type='application/json')


def _my_json_error_response(message, status=200):
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)


@login_required
def global_stream(request):
    postForm = PostForm()
    post = reversed(Post.objects.all().order_by('post_date_time'))
    context = {'form': postForm, 'posts': post}
    return render(request, 'socialnetwork/global.html', context)


@login_required
def follower_stream(request):
    context = {}
    loginUser = Profile.objects.get(user=request.user)
    followingUser = []
    for i in range(loginUser.follows.count()):
        followingUser.append(loginUser.follows.all()[i].user)

    post = reversed(Post.objects.filter(user__in=followingUser).order_by('post_date_time'))
    context['posts'] = post
    return render(request, 'socialnetwork/follower.html', context)


@login_required
def profile(request):
    context = {}
    loginUser = Profile.objects.get(user=request.user)
    context['form'] = ProfileForm(instance=loginUser)
    context['profile'] = loginUser
    followingUser = []
    for i in range(loginUser.follows.count()):
        followingUser.append(loginUser.follows.all()[i].user)
    context['following'] = followingUser

    return render(request, 'socialnetwork/profile.html', context)


@login_required
def update_profile(request):
    context = {}
    newProfile = Profile.objects.get(user=request.user)
    newForm = ProfileForm(request.POST, request.FILES, instance=newProfile)
    if not newForm.is_valid():
        context['form'] = newForm
    else:
        # Must copy content_type into a new model field because the model
        # FileField will not store this in the database.  (The uploaded file
        # is actually a different object than what's return from a DB read.)
        newProfile.content_type = newForm.cleaned_data['profile_picture'].content_type
        newForm.save()
    context['form'] = newForm
    context['profile'] = newProfile
    return render(request, 'socialnetwork/profile.html', context)


@login_required
def get_photo(request, id):
    picture = get_object_or_404(Profile, id=id)

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not picture.profile_picture:
        raise Http404

    return HttpResponse(picture.profile_picture, content_type=picture.content_type)


@login_required
def get_profile(request, id):
    if request.user.id == id:
        return profile(request)

    context = {}
    if Profile.objects.filter(id=id).exists():
        userProfile = Profile.objects.get(id=id)
        context['bio'] = userProfile.bio_input_text
        context['profile'] = userProfile
        context['firstName'] = User.objects.get(id=id).first_name
        context['lastName'] = User.objects.get(id=id).last_name
        context['followUnfollow'] = Profile.objects.get(user=request.user).follows.filter(id=id)

    return render(request, 'socialnetwork/otherprofile.html', context)


@login_required
def follow_unfollow(request, id):
    loginUser = Profile.objects.get(user=request.user)
    viewingUser = Profile.objects.get(id=id)
    if not loginUser.follows.filter(id=viewingUser.id).exists():
        loginUser.follows.add(viewingUser)
    else:
        loginUser.follows.remove(viewingUser)
    return get_profile(request, id)


@login_required
def create_post(request):
    post = Post(user=request.user)
    postForm = PostForm(request.POST, instance=post)
    if not postForm.is_valid():
        context = {'form': postForm}
        return render(request, 'socialnetwork/global.html', context)

    post.post_text = postForm.cleaned_data['post_input_text']
    post.post_date_time = timezone.now()

    post.post_profile = Profile(user=request.user)
    postForm.save()
    context = {'form': PostForm(), 'posts': reversed(Post.objects.all().order_by('post_date_time'))}
    return render(request, 'socialnetwork/global.html', context)


def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'socialnetwork/login.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))


def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)

    loginUser = Profile(user=request.user)
    loginUser.save()

    return redirect(reverse('home'))
