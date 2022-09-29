import logging
import weather

from time import sleep
from sys import exit as terminate

NAME = weather.read_local_data("name")

def background_process(btn_and_screen):
    sleepiness = 0

    while True:
        if not self.touch_queue.empty():
            touch_info = self.touch_queue.get()

            if touch_info[2]:
                self.clean_up()
                if touch_info[2] == "back_button":
                    return "Home"
                else:
                    logging.critical("Button '{}' is not bound to a screen.".format(touch_info[2]))
                    terminate()
        else:
            if sleepiness >= 600:
                return "Off About"
            else:
                sleepiness += 1
            
        new_data = self.weather.request_weather_info(self.weather_queues, "day_phase", wait=True)

        if new_data:
            day_phase = self.weather.get_day_phase(new_data)
            self.tft.background(self.display_command, day_phase)
        sleep(0.1)

def clean():
    self.tft.clear_screen(self.display_command, self.button_queue)

def home():
    def find_current_data():
        if day_phase == "night":
            return "Good Night,", "weatherCodeNight"
        elif day_phase == "day":
            return "Good Afternoon,", "weatherCodeDay"
        return "Good {},".format(day_phase.capitalize()), "weatherCodeDay"

    weather_info = weather.request_weather_info(self.weather_queues, "home")
    day_phase = weather.get_day_phase(weather.request_weather_info(self.weather_queues, "day_phase"))
    local = find_current_data()

    welcome_label = self.tft.format_text("welcome_label", local[0], "midtop", (120,10), "header")
    name_label = self.tft.format_text("name", self.NAME, "midtop", (120,40), "header")
    time_temp_label = self.tft.format_text("time_temp_label", "", "midtop", (120,280), "subheader")

    weather_button = self.tft.format_label("weather_button", ((20, 90), self.tft.WEATHER_ICON), "topleft", image="weather_icons/{}.png".format(weather_info[local[1]]), button=True)
    calendar_button = self.tft.format_label("calendar_button", ((220, 90), self.tft.WEATHER_ICON), "topright", image="calendar.png", button=True)
    gallery_button = self.tft.format_label("gallery_button", ((20, 182), self.tft.WEATHER_ICON), "topleft", image="blank.png", button=True)
    about_button = self.tft.format_label("about_button", ((220, 182), self.tft.WEATHER_ICON), "topright", image="notepad.png", button=True)

    self.tft.create_element(self.display_command, welcome_label, name_label, time_temp_label, weather_button, calendar_button, gallery_button, about_button, button_reg=self.button_queue)
    self.tft.background(self.display_command, day_phase)
    current_temperature = weather_info["temperature"]

def weather_report(page):
    pass

def about():
    pass

def sleep_screen():
    pass

def wip():
    pass