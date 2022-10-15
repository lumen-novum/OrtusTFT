from time import sleep
from sys import exit as terminate
import datetime

# As long as the "configure" module has been imported, we don't have to worry about creating a basic config.
import logging
import weather

class HomeScreen:
    def __init__(self, necessities):
        self.tft, self.display_command, self.button_queue, self.touch_queue, self.weather_queues = necessities

        self.NAME = weather.read_local_data("name")

    def display(self):
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

        sleepiness = 0

        while True:
            if not self.touch_queue.empty():
                touch_info = self.touch_queue.get()

                if touch_info[2]:
                    self.clean_up()
                    if touch_info[2] == "weather_button":
                        return "Stats"
                    elif touch_info[2] == "calendar_button":
                        return "Calendar"
                    elif touch_info[2] == "gallery_button":
                        return "Photos"
                    elif touch_info[2] == "about_button":
                        return "About"
                    else:
                        logging.critical("Button '{}' is not bound to a screen.".format(touch_info[2]))
                        terminate()
            else:
                if sleepiness >= 600: # 1 minute
                    return "Off Home"
                else:
                    sleepiness += 1


            new_data = weather.request_weather_info(self.weather_queues, "home", wait=True)

            if new_data:
                day_phase = weather.get_day_phase(weather.request_weather_info(self.weather_queues, "day_phase"))
                self.tft.background(self.display_command, day_phase)
                local = find_current_data()

                self.tft.update_element(self.display_command, "welcome_label", "text", local[0])
                self.tft.update_element(self.display_command, "weather_button", "image", "weather_icons/{}.png".format(new_data[local[1]]))
                current_temperature = new_data["temperature"]
            
            self.tft.update_element(self.display_command, "time_temp_label", "text", "{} F°   {}".format(current_temperature, (datetime.now()).strftime("%-I:%M %p")))
            sleep(0.1)

    def clean_up(self):
        self.tft.clear_screen(self.display_command, self.button_queue)