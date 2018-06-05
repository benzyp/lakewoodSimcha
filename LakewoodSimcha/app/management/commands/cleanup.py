from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from app.models import Event, Venue, Customer
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'cleans out expired bookings'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        today = timezone.now()
        events = Event.objects.filter(confirmed=False).filter(created__lte=today).all()
        for event in events:
            if (today - event.created).total_seconds() > (event.venue.duration * 3600):#difference between creeated time * 3600 to get hours 
                #6 hours or more send an email 
                #if
                send_mail(
                    'Your tentative booking ' + event.title + ' is set to expire ',
                    'Your booking on ' + event.start.strftime("%A, %d. %B %Y %I:%M%p") + ' will expire in ' + str(event.venue.duration)  + 
                    ' hours. \nPlease be in touch with ' + event.venue.name + ' via phone: ' + event.venue.phone + ' or email: ' + event.venue.email + ' to confirm and complete your booking.\n\n' +
                    'Thank you,\n\nLakewood Simcha',
                    'benzyp@yahoo.com',
                    [event.customer.email],
                    fail_silently=False,
                )
                #less than 6 hours delete the event

        self.stdout.write(self.style.SUCCESS('Successful output'))