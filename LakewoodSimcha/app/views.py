"""
Definition of views.
"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from app.models import Event, Customer, Venue
from app.forms import EventForm, CustomerForm
from django.core.serializers import serialize
from array import array
import json
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.mail import send_mail
from django.db.models import F

def home(request):
    """Renders the home page."""
    #assert isinstance(request, HttpRequest)
    allEvents = []
    eventChoices = []
    eventColors = ('indigo', 'green', 'lightSkyBlue', 'plum')
    for eventType in Event.EVENT_TYPES:
        #get all events for each event type
        packages = Event.objects.filter(event_type = eventType[0]).filter(confirmed = True).all().values('id','title','start','description','venue__name')
        
        if packages.exists():
            eventChoices.append(eventType[1])
            eventGroup = []
            for package in packages:
                package['color'] = [eventColors[eventType[0]-1]]
                #attributes can be added to the event - package['borderColor'] = 'red'
                eventGroup.append(package)
            json_obj = dict(events = eventGroup)
            allEvents.append(json_obj)

    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'events':json.dumps(allEvents,default=str),
            'extra_context': {'venues':eventChoices }
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
    venues = Venue.objects.filter(venue_type =  Venue.VENUE_TYPE_MAP[booking])
    for currentVenue in venues:
        #get all events for each venue type
        #annotate will rename 'venue__color' to 'color
        packages = Event.objects.annotate(color=F('venue__color'),editable=F('confirmed'),type=F('event_type')).filter(venue = currentVenue.id).all().values('id','title','start','venue__name','venue__venue_type','type','color','editable')
        if packages.exists():
            eventGroup = []
            for package in packages:
                package['editable'] = not package['editable']#flip the value
                package['type'] = Event.EVENT_TYPES[package['type']-1][1]#event type for details
                if package['editable'] == True:
                    package['borderColor'] = "red"
                    package['title'] = "Tentative"
                eventGroup.append(package)
                #store list of all distinct venues for choicespartial
                if (currentVenue.id,package['venue__name']) not in allVenues:
                    allVenues.append((currentVenue.id,package['venue__name']))
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
            contact_venue(event, customer)
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
        'benzyp@yahoo.com',
        [customer.email],
        fail_silently=False,
    )

def contact_venue_with_edit(event, customer):
    """send an email to the venue"""
    d = dict(Event.EVENT_TYPES)
    send_mail(
        'Event date has been changed',
        customer.name + ' has change the ' + event.title + ' event to a new date. ' + event.start,
        'benzyp@yahoo.com',
        [customer.email],
        fail_silently=False,
    )

def verify_phone(request):
    event_id = request.POST.get('edit_event_id')
    phone = request.POST.get('phone')
    event_edit_start = request.POST.get('edit_event_start')
    event = Event.objects.get(id=event_id)
    valid = False
    if phone == event.customer.phone: 
        event.start = event_edit_start
        event.save()
        contact_venue_with_edit(event, event.customer)
        valid = True
    return JsonResponse(valid, safe=False)
    
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

def venue_page(request, pk):
    venue = get_object_or_404(Venue, pk=pk)
    events = Event.objects.annotate(color=F('venue__color'),editable=F('confirmed'),type=F('event_type')).filter(venue = pk).all().values('id','title','start','venue__name','venue__venue_type','type','color','editable')
    if events.exists():
        eventGroup = []
        for event in events:
            event['editable'] = not event['editable']#flip the value
            event['type'] = Event.EVENT_TYPES[event['type']-1][1]
            if event['editable'] == True:
                event['borderColor'] = "red"
                event['title'] = "Tentative"
            eventGroup.append(event)
        json_obj = dict(events = eventGroup)

    return render(
    request,
    'app/venue.html',
    {
        'events':json.dumps(json_obj,default=str),
        'venue':venue,
        'title':venue.name,
        'year':datetime.now().year,
    }
)

def help(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/help.html',
        {
            'title':'Help',
            'message':'Help page.',
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
