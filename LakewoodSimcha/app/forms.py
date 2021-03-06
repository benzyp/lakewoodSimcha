"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.forms import Form
from app.models import Event,Venue,Customer
from datetimewidget.widgets import DateTimeWidget

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
    class Meta:
        model = Event
        fields = ('start','event_type', 'title', 'venue', 'description')
        dateTimeOptions = { 'showMeridian':True }
        widgets = {#Use localization and bootstrap 3
            'start': DateTimeWidget(attrs={'id':"start"}, usel10n = True, bootstrap_version=3, options=dateTimeOptions)            
        }

    def __init__(self, venue, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        #set the venue field to only include venues for the booking at hand
        self.fields['venue'].queryset = Venue.objects.filter(venue_type=venue)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ()

class AdminEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('start','confirmed','venue')
        dateTimeOptions = { 'showMeridian':True }
        widgets = {'venue': forms.HiddenInput(),'start':DateTimeWidget(attrs={'id':"start"},usel10n = True, bootstrap_version=3, options=dateTimeOptions)}
        labels = {'venue':_('')}

class EditDateForm(forms.Form):
    phone = forms.CharField(max_length=10)
    dateTimeOptions = { 'showMeridian':True } 
    edit_event_start = forms.DateTimeField(label = 'New Date', widget=DateTimeWidget(attrs={'id':"start"},usel10n = True, bootstrap_version=3, options=dateTimeOptions))

class UploadFileForm(forms.Form):
    venue = forms.IntegerField(widget = forms.HiddenInput(), label = '')
    file = forms.FileField()