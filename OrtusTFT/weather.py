import requests
import json
from datetime import datetime
from time import sleep
from sys import exit as terminate

# As long as the "configure" module has been imported, we don't have to worry about creating a basic config.
import logging


class Weather:
    def __init__(self, data_queues, demo):
        self.demo = demo
        
        self.url = "https://api.tomorrow.io/v4/timelines"

        self.login = {
        "fields":["temperature", "windSpeed", "visibility", "humidity", "cloudCover", "iceAccumulation", "snowAccumulation"]
        }

        weather_data = self.read_local_data("weather")

        for entry in weather_data:
            self.login[entry] = weather_data[entry]

        self.daily_fields = ["weatherCodeDay", "weatherCodeNight", "sunriseTime", "sunsetTime", "moonPhase"]

        self.recieve, self.send = data_queues

    def get_weather(self):
        logging.info("Requested weather data.")
        hourly_weather_info = {}
        daily_weather_info = {}

        self.login["timesteps"] = "1d"
        for field in self.daily_fields:
            self.login["fields"].append(field)

        data = (requests.request("GET", self.url, params=self.login)).json()

        if data.get("data") is not None:
            daily_weather_info = data["data"]["timelines"][0]["intervals"]
        else:
            logging.critical("Weather error: {}".format(data["type"]))
            terminate()

        self.login["timesteps"] = "1h"
        for field in self.daily_fields:
            self.login["fields"].remove(field)

        data = (requests.request("GET", self.url, params=self.login)).json()

        if data.get("data") is not None:
            hourly_weather_info = data["data"]["timelines"][0]["intervals"]
        else:
            logging.critical("Weather error: {}".format(data["type"]))
            terminate()

        self.save_data(hourly_weather_info, daily_weather_info)
        return [hourly_weather_info, daily_weather_info]

    def verify_time(self, time):
        # Get the current time and inputted time in seconds
        time = (datetime.strptime(time, "%Y-%m-%dT%X%z")).timestamp()
        current_time = (datetime.now()).timestamp()

        # If the difference between the current time and the last update is more than an hour, send a weather request.
        return current_time - time > 3600

    @staticmethod
    def current_time():
        return (datetime.now()).strftime("%-I:%M %p")

    def weather_handler(self):
        request_debounce = False
        json_object = None

        try:
            weather_json = open("OrtusTFT/weather.json", "r")
            json_object = json.load(weather_json)
        except FileNotFoundError:
            weather_json = open("OrtusTFT/weather.json", "a")
        finally:
            weather_json.close()

        if not json_object or self.verify_time(json_object["timeIntervals"][0]["hour"][0]["startTime"]):
            logging.info("Outdated weather file detected. Refreshing data.")
            weather_info = self.get_weather()
            request_debounce = True
        else:
            logging.info("Data is up to date.")
            weather_info = [json_object["timeIntervals"][0]["hour"], json_object["timeIntervals"][1]["day"]]

        while True:
            current_time = datetime.now()
            if current_time.minute == 0:
                if not request_debounce:
                    weather_info = self.get_weather()
                    self.send.put("refresh_current_data")
                    request_debounce = True
            else:
                request_debounce = False

            while not self.recieve.empty():
                data_pattern = self.recieve.get()
                filtered_data = {}

                if data_pattern == "day_phase":
                    filtered_data["sunrise"] = weather_info[1][0]["values"]["sunriseTime"]
                    filtered_data["sunset"] = weather_info[1][0]["values"]["sunsetTime"]
                elif data_pattern == "home":
                    filtered_data["temperature"] = int(weather_info[0][0]["values"]["temperature"]) # Int conversion isn't required, but it just rounds it down.
                    filtered_data["weatherCodeDay"] = weather_info[1][0]["values"]["weatherCodeDay"]
                    filtered_data["weatherCodeNight"] = weather_info[1][0]["values"]["weatherCodeNight"]
                elif data_pattern == "stats":
                    hour_fields = ("temperature", "windSpeed", "visibility", "humidity", "cloudCover")

                    for field in hour_fields:
                        filtered_data[field] = int(weather_info[0][0]["values"][field])

                    filtered_data["moonPhase"] = self.get_moon_phase(str(weather_info[1][0]["values"]["moonPhase"]))
                elif data_pattern == "stats 2":
                    filtered_data["day_weather"] = weather_info[1][0]["values"]["weatherCodeDay"]
                    filtered_data["night_weather"] = weather_info[1][0]["values"]["weatherCodeNight"]

                    convert = lambda time: datetime.fromtimestamp(((datetime.strptime(time, "%Y-%m-%dT%X%z")).timestamp() + 3600) % 86400)
                    sunrise, sunset = convert(weather_info[1][0]["values"]["sunriseTime"]).strftime("%-I:%M AM"), convert(weather_info[1][0]["values"]["sunsetTime"]).strftime("%-I:%M PM")
                    filtered_data["sunrise"] = sunrise
                    filtered_data["sunset"] = sunset

                    filtered_data["ice"] = weather_info[0][0]["values"]["iceAccumulation"]
                    filtered_data["snow"] = weather_info[0][0]["values"]["snowAccumulation"]

                self.send.put(filtered_data)
            sleep(0.1)

    def get_day_phase(self, times):
        # Get the current time and when sunrise and sunset starts.
        convert = lambda time: ((datetime.strptime(time, "%Y-%m-%dT%X%z")).timestamp() - 18000) % 86400
        current_time = ((datetime.now()).timestamp() - 18000) % 86400
        sunrise_time = convert(times["sunrise"])
        sunset_time = convert(times["sunset"])

        # 10 AM = Always afternoon; 4 PM = Always evening
        if current_time >= sunset_time or current_time < sunrise_time:
            return "night"
        elif current_time >= sunrise_time and current_time < 36000:
            return "morning"
        elif current_time >= 36000 and current_time < 57600:
            return "day"
        elif current_time >= 57600 and current_time < sunset_time:
            return "evening"
        else:
            logging.critical("The current time is invaild. Time: {}".format(current_time))
            terminate()

    @staticmethod
    def get_moon_phase(number):
        moon_phases = {
            "0": "New",
            "1": "Waxing Crescent",
            "2": "First Quarter",
            "3": "Waxing Gibbous",
            "4": "Full",
            "5": "Waning Gibbous",
            "6": "Third Quarter",
            "7": "Waning Crescent"
        }

        return moon_phases.get(number)

    @staticmethod
    def get_weather_code(number):
        weather_codes = {
            "1000": "Clear",
            "1100": "Mostly Clear",
            "1101": "Partly Cloudy",
            "1102": "Mostly Cloudy",
            "1001": "Cloudy",
            "1103": "Partly Cloudy and Mostly Clear",
            "2100": "Light Fog",
            "2101": "Mostly Clear and Light Fog",
            "2102": "Partly Cloudy and Light Fog",
            "2103": "Mostly Cloudy and Light Fog",
            "2106": "Mostly Clear and Fog",
            "2107": "Partly Cloudy and Fog",
            "2108": "Mostly Cloudy and Fog",
            "2000": "Fog",
            "4204": "Partly Cloudy and Drizzle",
            "4203": "Mostly Clear and Drizzle",
            "4205": "Mostly Cloudy and Drizzle",
            "4000": "Drizzle",
            "4200": "Light Rain",
            "4213": "Mostly Clear and Light Rain",
            "4214": "Partly Cloudy and Light Rain",
            "4215": "Mostly Cloudy and Light Rain",
            "4209": "Mostly Clear and Rain",
            "4208": "Partly Cloudy and Rain",
            "4210": "Mostly Cloudy and Rain",
            "4001": "Rain",
            "4211": "Mostly Clear and Heavy Rain",
            "4202": "Partly Cloudy and Heavy Rain",
            "4212": "Mostly Cloudy and Heavy Rain",
            "4201": "Heavy Rain",
            "5115": "Mostly Clear and Flurries",
            "5116": "Partly Cloudy and Flurries",
            "5117": "Mostly Cloudy and Flurries",
            "5001": "Flurries",
            "5100": "Light Snow",
            "5102": "Mostly Clear and Light Snow",
            "5103": "Partly Cloudy and Light Snow",
            "5104": "Mostly Cloudy and Light Snow",
            "5122": "Drizzle and Light Snow",
            "5105": "Mostly Clear and Snow",
            "5106": "Partly Cloudy and Snow",
            "5107": "Mostly Cloudy and Snow",
            "5000": "Snow",
            "5101": "Heavy Snow",
            "5119": "Mostly Clear and Heavy Snow",
            "5120": "Partly Cloudy and Heavy Snow",
            "5121": "Mostly Cloudy and Heavy Snow",
            "5110": "Drizzle and Snow",
            "5108": "Rain and Snow",
            "5114": "Snow and Freezing Rain",
            "5112": "Snow and Ice Pellets",
            "6000": "Freezing Drizzle",
            "6003": "Mostly Clear and Freezing drizzle",
            "6002": "Partly Cloudy and Freezing drizzle",
            "6004": "Mostly Cloudy and Freezing drizzle",
            "6204": "Drizzle and Freezing Drizzle",
            "6206": "Light Rain and Freezing Drizzle",
            "6205": "Mostly Clear and Light Freezing Rain",
            "6203": "Partly Cloudy and Light Freezing Rain",
            "6209": "Mostly Cloudy and Light Freezing Rain",
            "6200": "Light Freezing Rain",
            "6213": "Mostly Clear and Freezing Rain",
            "6214": "Partly Cloudy and Freezing Rain",
            "6215": "Mostly Cloudy and Freezing Rain",
            "6001": "Freezing Rain",
            "6212": "Drizzle and Freezing Rain",
            "6220": "Light Rain and Freezing Rain",
            "6222": "Rain and Freezing Rain",
            "6207": "Mostly Clear and Heavy Freezing Rain",
            "6202": "Partly Cloudy and Heavy Freezing Rain",
            "6208": "Mostly Cloudy and Heavy Freezing Rain",
            "6201": "Heavy Freezing Rain",
            "7110": "Mostly Clear and Light Ice Pellets",
            "7111": "Partly Cloudy and Light Ice Pellets",
            "7112": "Mostly Cloudy and Light Ice Pellets",
            "7102": "Light Ice Pellets",
            "7108": "Mostly Clear and Ice Pellets",
            "7107": "Partly Cloudy and Ice Pellets",
            "7109": "Mostly Cloudy and Ice Pellets",
            "7000": "Ice Pellets",
            "7105": "Drizzle and Ice Pellets",
            "7106": "Freezing Rain and Ice Pellets",
            "7115": "Light Rain and Ice Pellets",
            "7117": "Rain and Ice Pellets",
            "7103": "Freezing Rain and Heavy Ice Pellets",
            "7113": "Mostly Clear and Heavy Ice Pellets",
            "7114": "Partly Cloudy and Heavy Ice Pellets",
            "7116": "Mostly Cloudy and Heavy Ice Pellets",
            "7101": "Heavy Ice Pellets",
            "8001": "Mostly Clear and Thunderstorm",
            "8003": "Partly Cloudy and Thunderstorm",
            "8002": "Mostly Cloudy and Thunderstorm",
            "8000": "Thunderstorm"
        }
        
        return weather_codes.get(number)


    def save_data(self, hour, day):
        with open("OrtusTFT/weather.json", "w") as weather_json:
            newdict = {"_DEBUG": "Whenever Python creates a file, it does not allow anyone to edit it.",
                    "_ONLY": "If you need to edit this file, please run the following bash command in the same directory as 'main.py' ",
                    "_DO-NOT-EDIT": "sudo chmod a=rw OrtusTFT/weather.json",
                    "timeIntervals": [{"hour": hour}, {"day": day}]}
            json_object = json.dumps(newdict, indent=4)
            weather_json.write(json_object)

    @staticmethod
    def read_local_data(section):
        with open("OrtusTFT/info.json", "r") as data:
            data = json.load(data)

        return data[section]

    @staticmethod
    def request_weather_info(weather_queues, data_pattern, wait=False):
        def exchange(): # Request for a particular section of weather data, wait for the data, and return it.
            qinput.put(data_pattern)

            while qoutput.empty():
                pass
            
            key = qoutput.get()

            while key == "refresh_current_data":
                key = qoutput.get()
            return key

        qinput, qoutput = weather_queues

        if not wait: # If the screen has changed
            return exchange()
        elif wait and not qoutput.empty():
            return exchange()