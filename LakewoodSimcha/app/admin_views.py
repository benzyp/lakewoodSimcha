"""
Definition of admin views.
"""

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from app.models import Event, Customer, Venue
from app.forms import EventForm, CustomerForm, AdminEventForm
from django.core.serializers import serialize
from array import array
import json
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.mail import send_mail
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    data = dict()
    if request.method == 'POST':
        if event.confirmed == 0:
            email_deleted_event(pk)
        event.customer.delete()
        event.delete()
        data['form_is_valid'] = True  # This is just to play along with the existing code
        events = Event.objects.filter(venue__id = event.venue.id)
        data['html_event_list'] = render_to_string('app/admin/partial_event_list.html', {
            'events': events
        })
    else:
        context = {'event': event}
        data['html_form'] = render_to_string('app/admin/partial_event_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)

def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        #form = EventForm(request.POST, instance=event)
        form = AdminEventForm(request.POST, instance=event,auto_id=False)
    else:
        #form = EventForm(event.event_type, instance=event)
        form = AdminEventForm(instance=event)
    return save_event_form(request, form, 'app/admin/partial_event_update.html',pk)

def save_event_form(request, form, template_name, pk):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            #Leaving this for now as a manual process - venue must delete existing bookings ot let the job expire them
            ##if booking is confirmed, delete all other pending bookings with notifications
            #if form.cleaned_data['confirmed']:
            #    confirm_booking(pk)
            form.save()
            data['form_is_valid'] = True
            #retrieve events for refresh of events list
            events = Event.objects.filter(venue = request.POST['venue'])
            data['html_event_list'] = render_to_string('app/admin/partial_event_list.html', {
                'events': events
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required(login_url='/login/')
def event_list(request, pk):
    #verify user id
    if not request.user.venue.id == int(pk):
        return redirect('/login/?next=%s' % request.path)
    events = Event.objects.filter(venue__id = pk)
    return render(request, 'app/admin/event_list.html', {'events': events, 'year':datetime.now().year,'allEvents':json.dumps(events,default=str)})

def email_deleted_event(pk):
    """send an email to customer with an unconfirmed booking that's being deleted."""
    event = Event.objects.get(id=pk)
    try:
        send_mail(
            event.title + ' booking at ' + event.venue.name + ' has been deleted.',
            event.start.strftime("%A, %d. %B %Y %I:%M%p") + ' at ' + event.venue.name + ' has been booked.\n\nPlease book a new date at ' + event.venue.name,
            'benzyp@yahoo.com',
            [event.customer.email],
            fail_silently=False,
        )
    except Exception as e:
        ex = e

#def confirm_booking(pk):
#    event = Event.objects.filter(id=pk).get()
#    #get any other tentative bookings for the same date/venue
#    tentativeEvents = Event.objects.filter(venue__id = event.venue.id).filter(start__gte=event.start.date()).filter(confirmed=0)..all()
#    #for BF and LT allow for double booking on Sunday
#    if event.StopAsyncIteration.weekday() == 6:
#        if event.venue.id == 3:
#            return
#    foreach event in tentativeEvents:
        
#        email_customer()
#        delete
#def upload_events
    