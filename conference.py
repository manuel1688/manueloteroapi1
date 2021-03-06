#!/usr/bin/env python

"""
conference.py -- Udacity conference server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: conference.py,v 1.25 2014/05/24 23:42:19 wesc Exp wesc $

created by wesc on 2014 apr 21

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'


from datetime import datetime
import json
import os
import time

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from models import Profile
from models import ProfileMiniForm
from models import ProfileForm
from models import TeeShirtSize
from models import Conference
from models import ConferenceForm
from models import Reservation
from models import ReservationForm
from models import Greeting
from models import GreetingForm

from utils import getUserId

from settings import WEB_CLIENT_ID



EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


DEFAULTS = {
    "city": "Default City",
    "maxAttendees": 0,
    "seatsAvailable": 0,
    "topics": [ "Default", "Topic" ],
}

@endpoints.api( name='conference',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class ConferenceApi(remote.Service):
    """Conference API v0.1"""

# - - - Profile objects - - - - - - - - - - - - - - - - - - -

    def _copyConferenceToForm(self, conf, displayName):
        """Copy relevant fields from Conference to ConferenceForm."""
        cf = ConferenceForm()
        for field in cf.all_fields():
            if hasattr(conf, field.name):
                # convert Date to date string; just copy others
                if field.name.endswith('Date'):
                    setattr(cf, field.name, str(getattr(conf, field.name)))
                else:
                    setattr(cf, field.name, getattr(conf, field.name))
            elif field.name == "websafeKey":
                setattr(cf, field.name, conf.key.urlsafe())
        if displayName:
            setattr(cf, 'organizerDisplayName', displayName)
        cf.check_initialized()
        return cf


    def _createConferenceObject(self, request):
        """Create or update Conference object, returning ConferenceForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()
        #if not user:
        #    raise endpoints.UnauthorizedException('Authorization required')
        #user_id = getUserId(user)
        user_id = 'manuel.otero.16@gmail.com'
        print user_id
        if not request.name:
            raise endpoints.BadRequestException("Conference 'name' field required")

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        del data['websafeKey']
        del data['organizerDisplayName']

        # add default values for those missing (both data model & outbound Message)
        for df in DEFAULTS:
            if data[df] in (None, []):
                data[df] = DEFAULTS[df]
                setattr(request, df, DEFAULTS[df])

        # convert dates from strings to Date objects; set month based on start_date
        if data['startDate']:
            data['startDate'] = datetime.strptime(data['startDate'][:10], "%Y-%m-%d").date()
            data['month'] = data['startDate'].month
        else:
            data['month'] = 0
        if data['endDate']:
            data['endDate'] = datetime.strptime(data['endDate'][:10], "%Y-%m-%d").date()

        # set seatsAvailable to be same as maxAttendees on creation
        # both for data model & outbound Message
        if data["maxAttendees"] > 0:
            data["seatsAvailable"] = data["maxAttendees"]
            setattr(request, "seatsAvailable", data["maxAttendees"])

        # make Profile Key from user ID
        p_key = ndb.Key(Profile, user_id)
        # allocate new Conference ID with Profile key as parent
        c_id = Conference.allocate_ids(size=1, parent=p_key)[0]
        # make Conference key from ID
        c_key = ndb.Key(Conference, c_id, parent=p_key)
        data['key'] = c_key
        data['organizerUserId'] = request.organizerUserId = user_id
        print(data)
        # create Conference & return (modified) ConferenceForm
        Conference(**data).put()

        return request

    def _createReservationObject(self, request):
            """Create or update Conference object, returning ConferenceForm/request."""
            # preload necessary data items
            user = endpoints.get_current_user()
            #if not user:
            #    raise endpoints.UnauthorizedException('Authorization required')
            #user_id = getUserId(user)
            user_id = 'manuel.otero.16@gmail.com'
            print user_id
            print request
            print '### --- RESERVACIONES: --- ###'
          

        

            if not request.name:
                raise endpoints.BadRequestException("Conference 'name' field required")

            # copy ConferenceForm/ProtoRPC Message into dict
            data = {field.name: getattr(request, field.name) for field in request.all_fields()}
            

            startDate = datetime.strptime(data['startDate'][:10], "%Y-%m-%d")
            endDate = datetime.strptime(data['endDate'][:10], "%Y-%m-%d")
            qp = Reservation.query()
            qp.filter(ndb.AND(Reservation.startDate <= startDate),ndb.AND(Reservation.endDate >= endDate))
            qp.fetch()
            
            for result in qp:
                print 'R-----'
                print result.name
                print result.startDate
                print result.endDate

            # convert dates from strings to Date objects; set month based on start_date
            if data['startDate']:
                data['startDate'] = datetime.strptime(data['startDate'][:10], "%Y-%m-%d").date()
                data['month'] = data['startDate'].month
            else:
                data['month'] = 0
            if data['endDate']:
                data['endDate'] = datetime.strptime(data['endDate'][:10], "%Y-%m-%d").date()

            

            # make Profile Key from user ID
            p_key = ndb.Key(Profile, user_id)
            # allocate new Conference ID with Profile key as parent
            c_id = Reservation.allocate_ids(size=1, parent=p_key)[0]
            # make Conference key from ID
            c_key = ndb.Key(Reservation, c_id, parent=p_key)
            data['key'] = c_key
            data['organizerUserId'] = request.organizerUserId = user_id
            print(data)
            # create Conference & return (modified) ConferenceForm
            Reservation(**data).put()

            return request

    def _copyProfileToForm(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                # convert t-shirt string to Enum; just copy others
                if field.name == 'teeShirtSize':
                    setattr(pf, field.name, getattr(TeeShirtSize, getattr(prof, field.name)))
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf


    def _getProfileFromUser(self):
        """Return user Profile from datastore, creating new one if non-existent."""
        ## TODO 2
        ## step 1: make sure user is authed
        ## uncomment the following lines:
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        profile = None
        ## step 2: create a new Profile from logged in user data
        ## you can use user.nickname() to get displayName
        ## and user.email() to get mainEmail
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        profile = p_key.get()

        if not profile:
            profile = Profile(
                key = p_key,
                displayName = user.nickname(), 
                mainEmail= user.email(),
                teeShirtSize = str(TeeShirtSize.NOT_SPECIFIED),
            )
            profile.put()
            
        return profile      # return Profile


    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()

        # if saveProfile(), process user-modifyable fields
        if save_request:
            for field in ('displayName', 'teeShirtSize'):
                if hasattr(save_request, field):
                    val = getattr(save_request, field)
                    if val:
                        setattr(prof, field, str(val))
            prof.put()           
        # return ProfileForm
        return self._copyProfileToForm(prof)


    @endpoints.method(message_types.VoidMessage, ProfileForm,
            path='profile', http_method='GET', name='getProfile')
    def getProfile(self, request):
        """Return user profile."""
        return self._doProfile()

    # TODO 1
    # 1. change request class
    # 2. pass request to _doProfile function --- HECHO
    @endpoints.method(ProfileMiniForm, ProfileForm,
            path='profile', http_method='POST', name='saveProfile')
    def saveProfile(self, request):
        """Update & return user profile."""
        return self._doProfile(request)

    @endpoints.method(ReservationForm, ReservationForm, path='reservation',
            http_method='POST', name='createReservation')
    def createReservation(self, request):
        """Create new conference."""
        return self._createReservationObject(request)

    @endpoints.method(GreetingForm,GreetingForm,path='file',
            http_method='POST', name='uploadFile')
    def uploadFile(self, request):
       
        print 'FILE !!! --- ENTRE!!!'
        print request
        print 'Content'
      
       

        return GreetingForm(name="Hola")









# registers API
api = endpoints.api_server([ConferenceApi]) 
