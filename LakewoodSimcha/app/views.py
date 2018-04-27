"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def book(request, booking):
    """Renders the home page."""
    bookingType = booking
    assert isinstance(request, HttpRequest)
    venues = get_venues(bookingType)
    return render(
        request,
        'app/book.html',
        {
            'title':'Book',
            'year':datetime.now().year,
            'booking': bookingType,
            #'extra_context': {'display':'Wedding','venues':[{'id':'neemashachaim','display':'Ne''emas Hachaim'},{'id':'ateresreva','display':'Ateres Reva'},{'id':'fountainballroom','display':'Fountain Ballroom'}] }

            'extra_context': venues
        }
    )

def get_venues(bookingType):
    if bookingType == 'wedding':
        return {'display':'Wedding','venues':[{'id':'neemashachaim','display':'Ne''emas Hachaim'},{'id':'ateresreva','display':'Ateres Reva'},{'id':'fountainballroom','display':'Fountain Ballroom'}] }
    if bookingType == 'hall':
        return {'display':'Hall','ceckboxes':{{'id':'bnosbracha','display':'Bnos Bracha'},{'id':'tashbar','display':'Tashbar'},{'id':'zichronshneur','display':'Zichron Shneur'}} }
    if bookingType == 'restaurant':
        return {'display':'Restaurant','ceckboxes':{{'id':'circa','display':'Circa'},{'id':'glattbite','display':'Glatt Bite'},{'id':'rands','display':'R & S'}} }

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
