"""
Copyright (c) 2023  Persons on behalf of Joseph0M
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""



import requests
import json
import time
import string

import googlemaps
from datetime import datetime
import plotly.express as px
import pandas as pd

# Map Plotting
class Maps():
    def __init__(self,key:str) -> None:
        self.client = googlemaps.Client(key=key)
        self.calls = 0

    def _process(self,data):
        lat = data['results'][0]['geometry']['location']['lat']
        lng = data['results'][0]['geometry']['location']['lng']
        formatted_address = data['results'][0]['formatted_address']
        return lat, lng, formatted_address

    def _get_place(self,name:str) -> dict:
        self.calls += 1
        data = self.client.places(name)
        data = data[name]
        return data

    def _plot(self,lat, long,names):
        df = pd.DataFrame({
            "latitude": lat,
            "longitude": long,
            "names": names
        })
        fig = px.scatter_mapbox(df, lat="latitude", lon="longitude",text="names", zoom=3)
        fig.update_layout(mapbox_style="open-street-map")
        return fig

    def plot(self,schools:dict) -> None:
        latitude = []
        longitude = []
        names = []
        for i in schools:
            try:
                if schools[i]['lat'] != None:
                    names.append(i)
                latitude.append(schools[i]['lat'])
                longitude.append(schools[i]['lng'])
            except:
                pass
        return self._plot(latitude, longitude,names)

    def find(self,school:dict,name:str) -> dict:
        data = self._get_place(name)
        if data:
            if data['status'] == "OK":
                lat, lng, formatted_address = self._process(data)
                school['lat'] = lat
                school['lng'] = lng
                school['formatted_address'] = formatted_address
                return school
        else:
            return None
        
#Main Algorithm

schools = {}

def get_cities():
    url = "https://www.cambridgeinternational.org"
    ext = "/ciefacsearch/getcities/"
    payload = {"awardingOrganisationId":4,"regionId":"United Kingdom"}
    req = requests.post(url+ext, data=payload)
    if req.status_code == 200:
        cities = []
        data = json.loads(req.text)
        for item in data:
            if "Text" in item and item["Text"] != "Select a city":
                cities.append(item["Text"])
        return cities
    else:
        print("Error: Request failed with status code", req.status_code)

def process(lines,city):
    global schools
    sequence = "<td><a"
    found_sequence = "<td>Yes</td>"
    for key,line in enumerate(lines):
        if sequence in line:
            if found_sequence in lines[key+2]:
                line = line.replace('<td><a href="',"")
                line = line.replace('" title="website" target="_blank">',"")
                line = line.replace("</a></td>","")
                line = line.strip()
                url, name = line.split(" ", 1)
                addr = name+ ", "+city
                schools[name] = {"primative_address": addr, "url": url,"city":city}

url = "https://www.cambridgeinternational.org"
ext = "/ciefacsearch/updatesearchcriteria/"
city = ""

def get_schools(city):
    global schools
    payload = {"AwardingOrganisationId":4,"SelectedRegionId":"United Kingdom","SelectedCity":city}
    req = requests.post(url+ext, data=payload)
    lines = req.text.splitlines()
    process(lines,city)

print("""
    Welcome to the CIE Centre Finder! 
    Find the nearest Cambridge International Exam centre that offers exams to private candidates.
    This program will find all the schools in a given city or country and plot them on a map.
    The main website is https://www.cambridgeinternational.org/find-a-centre/ but its horrible to use!
    """)
input("""
LEGAL DISCLAMER:
By using this program you agree to the following:
      Cambridge International Terms of service (https://www.cambridgeinternational.org/privacy-and-legal/terms-and-conditions/)
        - This software is not affiliated with Cambridge International
        - This software is not designed to reverse engineer, decomplile, copy or adapt any software or other code or scripts forming part of the Cambridge International Site
        - This software is not designed to change, modify, delete, interfere with or misuse data contained on the Cambridge International Site entered by or relating to any third party user of the Site
        Google Maps Platform Terms of Service (https://cloud.google.com/maps-platform/terms/)
        - This software is not affiliated with Google or any subsidiaries
You agree to use this software at your own risk. The author is not responsible for any damages or actions caused by the use of this software.
You releive the author of any legal responsibility for any damages or actions caused by the use of this software.
This software is not intended to be used for any illegal purposes.  
MIT License: 
      THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
      FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
      IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
      WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
      OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Press enter to continue.
      """)

print("""Please enter your Google Maps API key. You can get one for free at https://developers.google.com/maps/gmp-get-started
      Enable the Google Maps Place API and the Google Maps Geocoding API.
      For calls of more than 1000 per day, you will need to enter your billing information.
      """)

Key = input("Please enter your Google Maps API key: ")
print("Thank you!")
for city in get_cities():
    print(city)
    get_schools(city)

maps = Maps(Key)
for name in schools:
    schools[name] = maps.find(schools[name],name)
maps.plot(schools).show()



