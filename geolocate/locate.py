from django.http import HttpResponse, HttpRequest
import json, requests
import os


geocode_url = 'https://geocoder.cit.api.here.com/6.2/geocode.json'
google_url = 'https://maps.googleapis.com/maps/api/geocode/json'

def get_geocode_position(data):
    #the coordintes are deeply nested so can't avoid this ugliness
    response = data['Response']
    one_view = response['View'][0]
    #could be more than one result but we have no way of knowing which result is best
    one_result = one_view['Result'][0]
    location = one_result['Location']
    geocode_position = location['DisplayPosition']
    return geocode_position

def make_geocode_request(address):
    params = {
        'app_id': os.environ['GEOCODE_APP_ID'], 
        'app_code': os.environ['GEOCODE_APP_CODE'],
        'searchtext': address
    }
    resp = requests.get(url=geocode_url, params=params)
    data = resp.json()
    # data = json.loads(resp.text)
    geocode_position = get_geocode_position(data)
    #convert naming to Google style
    lat = geocode_position['Latitude']
    lng = geocode_position['Longitude']
    return {'lat': lat, 'lng': lng}


def get_google_position(data):
    one_result = data['results'][0]
    google_location = one_result['geometry']['location']
    print('google_location', google_location)
    return google_location


def make_google_request(address):
    params = {
        'key': os.environ['GOOGLE_API_KEY'],
        'address': address
    }
    resp = requests.get(url=google_url, params=params)
    data = resp.json()
    google_position = get_google_position(data)
    return google_position



#returns the latitude and longitude of an address
def locate(request):
    address = request.GET['address']

    #try geocode first
    try:
        geocode_position = make_geocode_request(address)
        return HttpResponse(json.dumps(geocode_position))
    except Exception as err:
        print('Unexpected error %s occurred with geocode API'%(err))

    #try google second
    try:
        google_position = make_google_request(address)
        return HttpResponse(json.dumps(google_position))
    except Exception as err:
        print('Unexpected error %s occurred with google API'%(err))
    
    #now give up
    return HttpResponse('Your request could not be completed at this moment')