"""
Todd Page
10/8/2011

Cool Test

requires pywapi : python-weather-api : http://code.google.com/p/python-weather-api/

"""

## standard libraries

## custom libraries
from base import PybotPlugin
import pywapi ## http://code.google.com/p/python-weather-api/

def pybot_start(pybot):
    weather = Weather(pybot)
    return weather

class Weather(PybotPlugin):
    def main(self, arguments_lst):
        cmd = arguments_lst[0]
        args = arguments_lst[1:]
        
        if cmd == "current":
            requestor = args[0]
            zipcode = args[1]
            self.getWeather(requestor, zipcode)
            
    def getWeather(self, dbref, zipcode):
        google_result = pywapi.get_weather_from_google(zipcode)
        condition = str(google_result["current_conditions"]["condition"])
        temp_f = str(google_result["current_conditions"]["temp_f"])
        temp_c = str(google_result["current_conditions"]["temp_c"])
        city = str(google_result["forecast_information"]["city"])
        
        msg = "It is %(condition)s and %(temp_f)sF (%(temp_c)sC) in %(city)s" % locals()
        self.mushPemit(dbref, msg)
