"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from app.models import Event, Venue
from app.forms import EventForm, CustomerForm
from django.core.serializers import serialize
from array import array
import json
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.mail import send_mail

def home(request):
    """Renders the home page."""
    #assert isinstance(request, HttpRequest)
    #eventTypes = EventType.objects.all()
    allEvents = []
    for eventType in Event.EVENT_TYPES:
        #get all events for each event type
        packages = Event.objects.filter(event_type = eventType[0]).all().values('id','title','start','color')
        
        if packages.exists():
            eventGroup = []
            for package in packages:
                eventGroup.append(package)
            json_obj = dict(events = eventGroup)
            allEvents.append(json_obj)

    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'events':json.dumps(allEvents,default=str)
            #,'events':serialize('json',event_list,fields=('id','title','startTime','color'))
        }
    )

def book(request, booking):
    """Allows a user to create an event. The event is not confirmed and will only display on the book page. The customer is created along with the booking."""
    bookingType = booking
    data = dict()
    assert isinstance(request, HttpRequest)

    if request.method == 'POST':
        
        form = EventForm(venue = Venue.VENUE_TYPE_MAP[booking], data = request.POST)
        customerForm = CustomerForm(request.POST)
        if all([form.is_valid(), customerForm.is_valid()]):
            customer = customerForm.save()
            event = form.save(commit = False)
            event.customer = customer
            event.save()
            #contact venue with the event details
            contact_venue(event, customer)
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = EventForm(venue = Venue.VENUE_TYPE_MAP[booking])
        customerForm = CustomerForm()

    allEvents = []
    allVenues = []
    for venueType in Venue.VENUE_TYPES:
        #get all events for each venue type
        packages = Event.objects.filter(venue = venueType[0]).filter(venue__venue_type = Venue.VENUE_TYPE_MAP[booking]).all().values('id','title','start','color','venue__name','venue__venue_type')
        
        if packages.exists():
            eventGroup = []
            for package in packages:
                eventGroup.append(package)
                #store list of all distinct venues for choicespartial
                if package['venue__name'] not in allVenues:
                    allVenues.append(package['venue__name'])
            json_obj = dict(events = eventGroup)
            allEvents.append(json_obj)

    if request.method == 'GET':
        return render(
            request,
            'app/book.html',
            {
                'form':EventForm(venue = Venue.VENUE_TYPE_MAP[booking]),
                'customerForm':CustomerForm(),
                'events':json.dumps(allEvents,default=str),
                'title':'Book',
                'year':datetime.now().year,
                'booking': bookingType,
                'extra_context': get_venues(bookingType, allVenues)
            }
        )
    elif request.method == 'POST':
        context = {'form': form, 'customerForm':customerForm}
        data['html_form'] = render_to_string('app/partial_book_create.html',
            context,
            request=request
        )
        return JsonResponse(data)

def create_event(request):
    #creates the new event form
    data = dict()

    if request.method == 'POST':

        form = EventForm(request.POST)
        customerForm = CustomerForm(request.POST)
        if all([form.is_valid(), customerForm.is_valid()]):
            customer = customerForm.save()
            event = form.save(commit = False)
            event.customer = customer
            event.save()

            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = EventForm(Venue.VENUE_TYPE_MAP[booking])
        customerForm = CustomerForm()
    context = {'form': form, 'customerForm':customerForm}
    data['html_form'] = render_to_string('app/partial_book_create.html',
        context,
        request=request
    )
    return JsonResponse(data)

def get_venues(bookingType, allVenues):
    """Gets all the venues for the booking type so that they can be toggled on/off."""
    if bookingType == 'wedding':
        return {'display':'Wedding','venues':allVenues }
    if bookingType == 'hall':
        return {'display':'Hall','venues':allVenues }
    if bookingType == 'restaurant':
        return {'display':'Restaurant','venues':allVenues }

def contact_venue(event, customer):
    """send an email to the venue"""
    d = dict(Event.EVENT_TYPES)
    send_mail(
        'A new booking at ' + event.venue.name,
        customer.name + ' has booked a ' + d[event.event_type] + ' at ' + event.venue.name + ' on ' + event.start.strftime("%A, %d. %B %Y %I:%M%p"),
        'bzpern@gmail',
        ['benzyp@yahoo.com'],
        fail_silently=False,
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )
