from django.db import models

# Create your models here.


class Person(models.Model):
    unique_id = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=200, blank=True)
    date_killed = models.DateField(blank=True)
    age = models.IntegerField(blank=True)
    state = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    race = models.CharField(max_length=10, blank=True)
    killed_by = models.CharField(max_length=10, blank=True)
    picture = models.ImageField(
        upload_to='photos', default='photos/default_profile.png')
    kbp_link = models.CharField(max_length=200, blank=True)
    news_link = models.CharField(max_length=200, blank=True)
