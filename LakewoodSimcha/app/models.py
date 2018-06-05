"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
#from app.admin import UserAdmin
# Create your models here.

#class EventType(models.Model):
#    name = models.CharField(max_length=100)

#class Profile(models.Model):
#    user = models.OneToOneField(User, on_delete=models.CASCADE)
#    foo = models.TextField(max_length=50, blank=True)

#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        Profile.objects.create(user=instance)

#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#    instance.profile.save()

class Venue(models.Model): 
    VENUE_TYPE_MAP = {'wedding':1,'hall':2,'restaurant':3,'other':4}
    WEDDING = 1
    HALL = 2
    RESTAURANT = 3
    OTHER = 4
    VENUE_TYPES = (
       (WEDDING, 'Wedding'),
       (HALL, 'Hall'),
       (RESTAURANT, 'Restaurant'),
       (OTHER, 'Other')
    )
    name = models.CharField(max_length=100)
    venue_type = models.PositiveSmallIntegerField(choices = VENUE_TYPES)
    price = models.DecimalField(max_digits=7, decimal_places=2,null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=9, decimal_places=7)
    color = models.CharField(max_length=25, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True)
    phone = models.CharField(max_length=10,blank=False)
    email = models.EmailField()
    duration = models.IntegerField()

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    #if created:
        #Venue.objects.create(user=instance)  when a new user is created it throws an error because venue.venue_type can't be null
        #workaround is to create the user and connect manually
    if hasattr(instance, 'venue'):
        instance.venue.save()

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10,blank=False)

class Event(models.Model):
    WEDDING = 1
    BARMITZVA = 2
    DINNER = 3
    VORT = 4
    EVENT_TYPES = (
       (WEDDING, 'Wedding' ),
       (BARMITZVA, 'Bar Mitzvah'),
       (DINNER, 'Dinner'),
       (VORT, 'Vort')
    )
    title = models.CharField(max_length=100)
    event_type = models.PositiveSmallIntegerField(choices = EVENT_TYPES)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    venue = models.ForeignKey(Venue,blank=True,null=True)
    description = models.CharField(max_length=250, blank=True)
    confirmed = models.BooleanField(default=False)
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField()

class Vendor(models.Model):
    CATERING = 1
    MUSIC = 2
    PHOTO = 3
    HAIR = 4
    MAKEUP = 5
    SERVICE_TYPES = (
       (CATERING, 'Catering'),
       (MUSIC, 'Music' ),
       (PHOTO, 'Photography'),
       (HAIR, 'Hairdressing'),
       (MAKEUP, 'Makeup')
    )
    name = models.CharField(max_length=100)
    service = models.PositiveSmallIntegerField(choices = SERVICE_TYPES)




