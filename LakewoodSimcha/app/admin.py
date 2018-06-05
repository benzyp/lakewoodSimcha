from django.contrib import admin
from app.models import Venue, Customer, Event, Vendor#,EventType
from django.contrib.auth.admin import UserAdmin #as BaseUserAdmin
from django.contrib.auth.models import User


#admin.site.register(EventType)
admin.site.register(Venue)
admin.site.register(Customer)
admin.site.register(Event)
class EventAdmin:
   list_select_related = { 'customer'}
admin.site.register(Vendor)

class VenueInline(admin.StackedInline):
    model = Venue
    can_delete = False
    verbose_name_plural = 'Venue'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (VenueInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
