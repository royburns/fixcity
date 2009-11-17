# Parses the json output feed from seeclickfix and creates racks from results
# Expected to be run from cron at regular intervals

from datetime import datetime
from django.conf import settings
from django.contrib.gis.geos.point import Point
from django.core.management.base import BaseCommand
from django.utils import simplejson as json
from pickle import dump
from pickle import load
from fixcity.bmabr.models import Rack
from fixcity.bmabr.views import SRID
import httplib2
import os

def create_rack(json_data):
    """create a bike rack given json_data as returned by seeclickfix"""
    title = json_data['summary']
    address = json_data['address']
    description = json_data['description']
    date = create_datetime_from_jsonstring(json_data['created_at'])
    # skip photo for now
    lat = json_data['lat']
    lng = json_data['lng']
    location = str(Point(lng, lat, srid=SRID))
    rack = Rack(title=title,
                description=description,
                address=address,
                date=date,
                location=location,
                )
    return rack

def fetch_feed(feed_url):
    """fetch a json feed from seeclick fix and load into a python object"""

    # this stub is what it would typically look like
    #return [{"rating":1,"description":"I need a bike rack for my mobster fixie crew.","page":1,"lat":40.7172736790292,"object_id":"issue9738","address":"1315 Grand St, New York, NY 11211","lng":-73.9256286621094,"summary":"Junkyard bike rack","issue_id":9738,"id":"issue9738","created_at":"11/12/2009 at 05:45PM","updated_at_raw":"2009/11/12 17:45:36 -0500","status":"Open","updated_at":"11/12/2009 at 05:45PM"}]

    http = httplib2.Http()
    response, content = http.request(feed_url)
    assert response.status == 200, "Did not receive 200 response from seeclickfix"
    return json.loads(content)

def get_latest_pickle_path():
    curpath = os.path.abspath(__file__)
    dirname = os.path.dirname(curpath)
    return os.path.join(dirname, 'latest.pickle')

def get_latest_date_seen():
    curpath = os.path.abspath(__file__)
    dirname = os.path.dirname(curpath)
    pickle_path = get_latest_pickle_path()
    try:
        f = open(pickle_path)
        latest_date = load(f)
        f.close()
    except IOError:
        # use a date for racks that we haven't seen yet
        latest_date = datetime(2009, 1, 1)
    return latest_date

def set_latest_date_seen(date):
    """keep track of the latest date to avoid making repetitions"""
    pickle_path = get_latest_pickle_path()
    f = open(pickle_path, 'w')
    dump(date, f)
    f.close()

def create_datetime_from_jsonstring(s):
    """return a datetime object given a string in a seeclickfix format"""
    return datetime.strptime(s, '%m/%d/%Y at %I:%M%p')


class Command(BaseCommand):

    def handle(self, *args, **options):
        feed_url = settings.SEECLICKFIX_JSON_URL
        json_data_list = fetch_feed(feed_url)
        latest_date_seen = get_latest_date_seen()
        racks_saved = []
        for json_data in json_data_list:
            date = create_datetime_from_jsonstring(json_data['created_at'])
            if date <= latest_date_seen:
                continue
            rack = create_rack(json_data)
            rack.save()
            racks_saved.append(rack)
        latest = reduce(max, [x.date for x in racks_saved], latest_date_seen)
        set_latest_date_seen(latest)
