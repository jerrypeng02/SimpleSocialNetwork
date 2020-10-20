from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    bio_input_text = models.CharField(max_length=10000)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    profile_picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    follows = models.ManyToManyField('Profile')


class Post(models.Model):
    post_input_text = models.CharField(max_length=200)
    post_date_time = models.DateTimeField()
    post_text = models.CharField(max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)


class Comment(models.Model):
    comment_input_text = models.CharField(max_length=200)
    comment_date_time = models.DateTimeField()
    comment_text = models.CharField(max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, default=None, on_delete=models.PROTECT)
