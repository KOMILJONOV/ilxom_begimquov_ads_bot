from django.db import models

# Create your models here.


class User(models.Model):
    chat_id = models.IntegerField(primary_key=True)


class Admin(models.Model):
    chat_id = models.IntegerField(primary_key=True)