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
    return save_event_form(request, form, 'app/admin/partial_event_update.html')

def save_event_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
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

#def upload_events
    