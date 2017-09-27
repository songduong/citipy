#dependencies
from citipy import citipy as cp
import random
import pyowm
import numpy as np
from  urllib import request as urllib_request
import datetime
import json 
import matplotlib.pyplot as plt
from math import ceil as ceiling
import csv
import os
import pandas as pd
import requests as req
from scipy.stats.stats import pearsonr
import time
API="INSERT API KEY"
owm = pyowm.OWM(API)
url="http://api.openweathermap.org/data/2.5/weather?q="
units="&units=imperial"

#get cities from coordinates
cities = []
 
while len(cities) <= 1500:
    latitude = random.randint(-90.00,90.00)
    longitude = random.randint(-180.00, 180.00)
    city = cp.nearest_city(latitude, longitude)
    if city not in cities:
        cities.append({
            'city code' : city,
            'city': city.city_name,
            'country': city.country_code,
            'latitude': latitude,
            'longitude': longitude,
        })
    else:
        continue

#get weather info for each city
weatherInfo={}
for x in cities:
    city = x['city']
    country = x['country']
    citycode = x['city code']
    latitude = x['latitude']
    longitude = x['longitude']
    cityCountryUnitsAPI=url+city+","+country+units+"&APPID="+API
    call=req.get(cityCountryUnitsAPI).json()
    time.sleep(1)
    for y in call:
        try:
            weatherInfo[city] = {
                'City': city,
                'Country':country,
                'Citycode':citycode,
                'Latitude':latitude,
                'Longitude':longitude,
                'Temperature (F)':call['main']['temp'],
                'Wind (mph)':call['wind']['speed'],
                'Humidity (%)':call['main']['humidity'],
                'Cloudiness (%)':call['clouds']['all'],
            }
        except KeyError:
            continue

"""
Instead of doing an API call from OWM, you can always install their package PYOWM and then do this:

for x in cities:

    city = x['city']
    country = x['country']
    citycode = x['city code']
    latitude = x['latitude']
    longitude = x['longitude']
    observation = owm.weather_at_place(city + ',' + country)
    w=observation.get_weather()
    temp = w.get_temperature()
    wind = w.get_wind()
    humid = w.get_humidity()
    cloud = w.get_clouds()
    weatherInfo[city] = {
        'city': city,
        'country':country,
        'citycode':citycode,
        'latitude':latitude,
        'longitude':longitude,
        'temperature':temp['temp'],
        'wind':wind['speed'],
        'humidity':humid,
        'cloudiness':cloud,
    }
"""

#get dataframe ready
weatherDF=pd.DataFrame.from_records(weatherInfo).T
weatherDF.to_csv("weatherDF.csv")
#remove columns that we don't need
weatherDF2=weatherDF.drop('Citycode', axis=1).drop('City', axis=1).drop('Country', axis=1).drop('Longitude', axis=1)

#loop to print out charts and analysis
for x in weatherDF2:
    if weatherDF2[x] is not weatherDF2['Latitude']:
        fig=plt.figure()
        plt.scatter(weatherDF2.Latitude, weatherDF2[x], s=50, edgecolor='steelblue', c='lightblue')
        plt.title(f'%s vs. Latitude' % (x.title()))
        plt.ylabel("Latitude")
        plt.xlabel(x.title())
        PR=pearsonr(weatherDF.Latitude, weatherDF2[x])
        plt.savefig(x + "vs. Latitude.png")
        plt.show()
 
        def printanalysis(z,w):
            if z >= 0.5:
                description = "a strong and positive"
                direction = "higher"
            elif 0 < z < 0.5:
                description = "a weak and positive"
                direction = "higher"
            elif -0.5 < z < 0:
                description = "a weak and negative"
                direction = "lower"
            elif z <= 0.5:
                description = "a strong and negative"
                direction = "lower"
            else:
                description = "zero"
            if w > 0.05:
                result="an insignificant"
                null="We are unable to reject the null hypotheses."
            elif w < 0.05:
                result ="a significant"
                null=f"We are able to reject the null hypotheses, and conclude that the higher the latitude, the %s the %s." % (direction, x)
            print(f'There is %s correlation between %s and latitude, r=%s, n=%s, p=%s. Overall, there is %s correlation between the two variables.' % (result, x, round(PR[0],3), len(weatherDF), round(PR[1],3), description))
            print("")
            print(null)
        printanalysis(PR[0],PR[1])

