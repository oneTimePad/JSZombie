from django.db import models

# Create your models here.



class Zombie(models.Model):

    host = models.CharField(max_length=100)
    facility = models.CharField(max_length=200)

class Attacker(models.Model):
    sesskey = models.CharField(max_length=200)
