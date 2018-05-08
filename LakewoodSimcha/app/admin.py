from django.contrib import admin
from app.models import Venue, Customer, Event, Vendor #,EventType

#admin.site.register(EventType)
admin.site.register(Venue)
admin.site.register(Customer)
admin.site.register(Event)
class EventAdmin:
   list_select_related = { 'customer'}
admin.site.register(Vendor)