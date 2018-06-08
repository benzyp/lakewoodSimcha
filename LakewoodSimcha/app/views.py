"""
Definition of views.
"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from app.models import Event, Customer, Venue
from app.forms import EditDateForm, EventForm, CustomerForm
from django.core.serializers import serialize
from array import array
import json
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.mail import send_mail
from django.db.models import F
from django.utils import timezone
from django.conf import settings
import pytz

def home(request):
    """Renders the home page."""
    #assert isinstance(request, HttpRequest)
    allEvents = []
    eventChoices = []
    allColors = []
    eventColors = ('indigo', 'green', 'lightSkyBlue', 'plum')
    for eventType in Event.EVENT_TYPES:
        #get all events for each event type later than today
        today = timezone.now()
        packages = Event.objects.filter(event_type = eventType[0]).filter(confirmed = True).filter(start__gte=today).all().values('id','title','start','description','venue__name')
        
        if packages.exists():
            eventChoices.append(eventType[1])
            allColors.append(eventColors[eventType[0]-1])
            eventGroup = []
            for package in packages:
                package['color'] = [eventColors[eventType[0]-1]]
                package['start'] = normalize(package['start'])#convert UTC time to eastern
                #attributes can be added to the event - package['borderColor'] = 'red'
                eventGroup.append(package)
            json_obj = dict(events = eventGroup)
            allEvents.append(json_obj)
    zipData = zip(eventChoices, allColors)#zip the event types and colors together for template
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'events':json.dumps(allEvents,default=str),
            'extra_context': zipData
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
            event.created = timezone.now()
            event.save()
            #contact venue with the event details
            contact_venue_on_booking(event, customer, request)
            contact_customer_on_booking(event, customer)
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = EventForm(venue = Venue.VENUE_TYPE_MAP[booking])
        customerForm = CustomerForm()

    allEvents = []
    allVenues = []
    allColors = []
    #filter dates today or later
    today = timezone.now()
    venues = Venue.objects.filter(venue_type =  Venue.VENUE_TYPE_MAP[booking])
    for currentVenue in venues:
        #get all events for each venue type
        #annotate will rename 'venue__color' to 'color
        packages = Event.objects.annotate(color=F('venue__color'),editable=F('confirmed'),type=F('event_type')).filter(venue = currentVenue.id).filter(start__gte=today).all().values('id','title','start','venue__name','venue__venue_type','type','color','editable')
        if packages.exists():
            eventGroup = []
            for package in packages:
                package['editable'] = not package['editable']#flip the value
                package['type'] = Event.EVENT_TYPES[package['type']-1][1]#event type for details popup
                package['start'] = normalize(package['start']) #convert UTC time to eastern
                if package['editable'] == True:
                    package['borderColor'] = "red"
                    package['title'] = "Tentative"
                eventGroup.append(package)
                #store list of all distinct venues for choicespartial
                if (currentVenue.id,package['venue__name']) not in allVenues:
                    allVenues.append((currentVenue.id,package['venue__name']))
                    allColors.append(currentVenue.color)
            json_obj = dict(events = eventGroup)
            allEvents.append(json_obj)
    zipData = zip( allVenues, allColors)#zip the event types and colors together for template
    if request.method == 'GET':
        return render(
            request,
            'app/book.html',
            {
                'form':EventForm(venue = Venue.VENUE_TYPE_MAP[booking]),
                'customerForm':CustomerForm(),
                'editDateForm':EditDateForm(),
                'events':json.dumps(allEvents,default=str),
                'title':'Book',
                'year':datetime.now().year,
                'booking': bookingType,
                'extra_context': zipData
            }
        )
    elif request.method == 'POST':
        context = {'form': form, 'customerForm':customerForm}
        data['html_form'] = render_to_string('app/partial_book_create.html',
            context,
            request=request
        )
        data['updated_events'] = json.dumps(allEvents, default=str)
        return JsonResponse(data)

#def create_event(request):
#    #creates the new event form
#    data = dict()

#    if request.method == 'POST':

#        form = EventForm(request.POST)
#        customerForm = CustomerForm(request.POST)
#        if all([form.is_valid(), customerForm.is_valid()]):
#            customer = customerForm.save()
#            event = form.save(commit = False)
#            event.customer = customer
#            event.save()
#            #contact_venue_on_booking(event, customer)
#            venue = Venue.objectS.get(event.venue.id)
#            contact_customer_on_booking(event, venue)
#            data['form_is_valid'] = True
#        else:
#            data['form_is_valid'] = False
#    else:
#        form = EventForm(Venue.VENUE_TYPE_MAP[booking])
#        customerForm = CustomerForm()
#    context = {'form': form, 'customerForm':customerForm}
#    data['html_form'] = render_to_string('app/partial_book_create.html',
#        context,
#        request=request
#    )
#    return JsonResponse(data)

def contact_venue_on_booking(event, customer, request):
    """send an email to the venue"""
    d = dict(Event.EVENT_TYPES)
    try:
        send_mail(
            event.title + ' booking at ' + event.venue.name,
            customer.name + ' has tentatively booked a ' + d[event.event_type] + ' at ' + event.venue.name + ' on ' + event.start.strftime("%A, %d. %B %Y %I:%M%p") + '.\nPlease be in touch with ' + customer.name + ' via email: ' + customer.email + ' or phone: ' + customer.phone + '.' +
            '\nTo confirm this booking please use the following link ' + request.build_absolute_uri("/") + 'events/' + str(event.venue.id),
            'benzyp@yahoo.com',
            [customer.email],
            fail_silently=False,
        )
    except Exception as e:
        ex = e

def contact_customer_on_booking(event, customer):
    """send an email to the customer"""
    d = dict(Event.EVENT_TYPES)
    
    try:
        send_mail(
            'Your tentative booking ' + event.title + ' was sent to ' + event.venue.name,
            'Your booking on ' + event.start.strftime("%A, %d. %B %Y %I:%M%p") + ' has been sent to ' + event.venue.name + ' and will expire in ' + str(event.venue.duration)  + 
            ' hours. \nPlease be in touch with ' + event.venue.name + ' via phone: ' + event.venue.phone + ' or email: ' + event.venue.email + ' to confirm and complete your booking.\n\n' +
            'Thank you,\n\nLakewood Simcha',
            'benzyp@yahoo.com',
            [customer.email],
            fail_silently=False,
        )
    except Exception as e:
        ex = e

def contact_venue_with_edit(event, customer, request):
    """send an email to the venue"""
    d = dict(Event.EVENT_TYPES)
    send_mail(
        'Event date has been changed',
        customer.name + ' has change the ' + event.title + ' event to a new date. ' + event.start.strftime("%A, %d %B %Y %I:%M%p") + '.\nPlease be in touch with ' + customer.name + ' via email: ' + customer.email + ' or phone: ' + customer.phone + '.' +
        '\nTo confirm this booking please use the following link ' + request.build_absolute_uri("/") + 'events/' + str(event.venue.id),
        'benzyp@yahoo.com',
        [customer.email],
        fail_silently=False,
    )

def verify_phone(request):
    event_id = request.POST.get('edit_event_id')
    phone = request.POST.get('phone')
    event_edit_start = localize(request.POST.get('edit_event_start'))
    event = Event.objects.get(id=event_id)
    valid = False
    if phone == event.customer.phone: 
        event.start = event_edit_start
        event.created = timezone.now()
        event.save()
        contact_venue_with_edit(event, event.customer, request)
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
    today = timezone.now()
    events = Event.objects.annotate(color=F('venue__color'),editable=F('confirmed'),type=F('event_type')).filter(venue = pk).filter(start__gte=today).all().values('id','title','start','venue__name','venue__venue_type','type','color','editable')
    if events.exists():
        eventGroup = []
        for event in events:
            event['editable'] = not event['editable']#flip the value
            event['type'] = Event.EVENT_TYPES[event['type']-1][1]
            event['start'] = normalize(event['start'])#convert UTC time to eastern
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

def normalize(to_convert):
    """Converts UTC aware internal times to eastern."""
    tz = pytz.timezone(settings.TIME_ZONE)
    return tz.normalize(to_convert)

def localize(to_convert):
    """Converts naive datetime to localize."""
    tz = pytz.timezone(settings.TIME_ZONE)
    return tz.localize(datetime.strptime(to_convert, '%Y-%m-%d %I:%M:%S %p'))