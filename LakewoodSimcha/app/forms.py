"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.forms import Form
from app.models import Event,Venue,Customer

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class EventForm(forms.ModelForm):
    #event_type = forms.IntegerField(widget=forms.Select(choices=Event.EVENT_TYPES))
    #title = forms.CharField(max_length=100)
    #venue = forms.ModelChoiceField(queryset=Venue.objects.filter(venue_type=2))
    #description = forms.CharField(max_length=250)
    class Meta:
        model = Event
        fields = ('event_type', 'title', 'venue', 'description', 'start')
        #widgets = {'start': forms.DateTimeInput(attrs={'class': 'datetime-input'})}

    def __init__(self, venue, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        #set the venue field to only include venues for the booking at hand
        self.fields['venue'].queryset = Venue.objects.filter(venue_type=venue)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ()



