from time import sleep
from sys import exit as terminate

# As long as the "configure" module has been imported, we don't have to worry about creating a basic config.
import logging

class StatScreen:
    def __init__(self, necessities):
        self.tft, self.display_command, self.button_queue, self.touch_queue, self.weather_queues, self.weather, self.demo = necessities

    def display(self):
        weather_info = self.weather.request_weather_info(self.weather_queues, "stats")

        back_button = self.tft.format_label("back_button", ((5, 5), self.tft.MINI_ICON), "topleft", image="previous.png", button=True)
        time_label = self.tft.format_text("time_label", "", "midtop", (120, 5), "subheader")
        next_page = self.tft.format_label("next_page", ((235, 5), self.tft.MINI_ICON), "topright", image="next.png", button=True)

        self.tft.create_element(self.display_command, back_button, time_label, next_page, button_reg=self.button_queue)

        temp_icon = self.tft.format_label("temp_icon", ((10, 47), self.tft.MINI_ICON), "topleft", image="descriptive/thermometer.png")
        temp_label = self.tft.format_text("temp_label", "Temperature: {} F°".format(weather_info["temperature"]), "topleft", (50, 47), "paragraph")

        wind_icon = self.tft.format_label("wind_icon", ((10, 89), self.tft.MINI_ICON), "topleft", image="descriptive/wind.png")
        wind_label = self.tft.format_text("wind_label", "Wind Speed: {} MPH".format(weather_info["windSpeed"]), "topleft", (50, 89), "paragraph")

        cloud_icon = self.tft.format_label("cloud_icon", ((10, 131), self.tft.MINI_ICON), "topleft", image="descriptive/cloud.png")
        cloud_label = self.tft.format_text("cloud_label", "Cloudiness: {}%".format(weather_info["cloudCover"]), "topleft", (50, 131), "paragraph")

        humidity_icon = self.tft.format_label("humidity_icon", ((10, 173), self.tft.MINI_ICON), "topleft", image="descriptive/humidity.png")
        humidity_label = self.tft.format_text("humidity_label", "Humidity: {}%".format(weather_info["humidity"]), "topleft", (50, 173), "paragraph")

        visibility_icon = self.tft.format_label("visibility_icon", ((10, 215), self.tft.MINI_ICON), "topleft", image="descriptive/visibility.png")
        visibility_label = self.tft.format_text("visibility_label", "Visibility: {} miles".format(weather_info["visibility"]), "topleft", (50, 215), "paragraph")

        moon_icon = self.tft.format_label("moon_icon", ((10, 257), self.tft.MINI_ICON), "topleft", image="descriptive/moon.png")
        moon_label = self.tft.format_text("moon_label", "Moon Phase:", "topleft", (50, 257), "paragraph")
        moon_phase = self.tft.format_text("moon_phase", weather_info["moonPhase"], "topleft", (50, 282), "paragraph")

        self.tft.create_element(self.display_command,
                                    temp_icon, temp_label, wind_icon, wind_label, humidity_icon, 
                                    humidity_label, visibility_icon, visibility_label,
                                    cloud_icon, cloud_label, moon_icon, moon_label,
                                    moon_phase)

        day_phase = self.weather.get_day_phase(self.weather.request_weather_info(self.weather_queues, "day_phase"))
        self.tft.background(self.display_command, day_phase)

        sleepiness = 0

        while True:
            if not self.touch_queue.empty():
                touch_info = self.touch_queue.get()

                if touch_info[2]:
                    self.clean_up()
                    if touch_info[2] == "back_button":
                        return "Home"
                    elif touch_info[2] == "next_page":
                        return "Stats 2"
                    else:
                        logging.critical("Button '{}' is not bound to a screen.".format(touch_info[2]))
                        terminate()
            else:
                if sleepiness >= 600:
                    return "Off Stats"
                else:
                    sleepiness += 1
            
            self.tft.update_element(self.display_command, "time_label", "text", self.weather.current_time())

            new_data = self.weather.request_weather_info(self.weather_queues, "stats", wait=True)
            if new_data:
                self.tft.update_element(self.display_command, "temp_label", "text", "Temperature: {} F°".format(new_data["temperature"]))
                self.tft.update_element(self.display_command, "wind_label", "text", "Wind Speed: {} MPH".format(new_data["windSpeed"]))
                self.tft.update_element(self.display_command, "cloud_label", "text", "Cloudiness: {}%".format(new_data["cloudCover"]))
                self.tft.update_element(self.display_command, "humidity_label", "text", "Humidity: {}%".format(new_data["humidity"]))
                self.tft.update_element(self.display_command, "visibility_label", "text", "Visibility: {} miles".format(new_data["visibility"]))
                self.tft.update_element(self.display_command, "moon_phase", "text", new_data["moonPhase"])
            sleep(0.1)

    def display_second_page(self):
        weather_info = self.weather.request_weather_info(self.weather_queues, "stats 2")

        back_button = self.tft.format_label("back_button", ((5, 5), self.tft.MINI_ICON), "topleft", image="previous.png", button=True)
        time_label = self.tft.format_text("time_label", "", "midtop", (120, 5), "subheader")

        self.tft.create_element(self.display_command, back_button, time_label, button_reg=self.button_queue)

        sunrise_icon = self.tft.format_label("sunrise_icon", ((10, 47), self.tft.MINI_ICON), "topleft", image="descriptive/sunrise.png")
        sunrise_label = self.tft.format_text("sunrise_label", "Sunrise: {}".format(weather_info["sunrise"]), "topleft", (50, 47), "paragraph")

        sunset_icon = self.tft.format_label("sunset_icon", ((10, 89), self.tft.MINI_ICON), "topleft", image="descriptive/sunset.png")
        sunset_label = self.tft.format_text("sunset_label", "Sunset: {}".format(weather_info["sunset"]), "topleft", (50, 89), "paragraph")

        weather_day_icon = self.tft.format_label("day_icon", ((10, 131), self.tft.MINI_ICON), "topleft", image="weather_icons/{}.png".format(weather_info["day_weather"]))
        weather_day_label = self.tft.format_text("day_label", "Daytime Weather:", "topleft", (50, 131), "paragraph")
        weather_day_desc = self.tft.format_text("day_desc", self.weather.get_weather_code(str(weather_info["day_weather"] // 10)), "topleft", (50, 156), "paragraph")

        weather_night_icon = self.tft.format_label("night_icon", ((10, 198), self.tft.MINI_ICON), "topleft", image="weather_icons/{}.png".format(weather_info["night_weather"]))
        weather_night_label = self.tft.format_text("night_label", "Nighttime Weather: ", "topleft", (50, 198), "paragraph")
        weather_night_desc = self.tft.format_text("night_desc", self.weather.get_weather_code(str(weather_info["night_weather"] // 10)), "topleft", (50, 223), "paragraph")

        ice_snow_icon = self.tft.format_label("ice_snow_icon", ((10, 265), self.tft.MINI_ICON), "topleft", image="descriptive/snowflake.png")
        ice_label = self.tft.format_text("ice_label", "Ice: {}%".format(weather_info["ice"]), "topleft", (50, 265), "paragraph")
        snow_label = self.tft.format_text("snow_label", "Snow: {}%".format(weather_info["snow"]), "topleft", (50, 290), "paragraph")

        self.tft.create_element(self.display_command, 
                                    sunrise_icon, sunrise_label, sunset_icon, sunset_label,
                                    weather_day_icon, weather_day_label, weather_night_icon,
                                    weather_day_desc, weather_night_label, weather_night_desc,
                                    ice_snow_icon, ice_label, snow_label)

        sleepiness = 0

        while True:
            if not self.touch_queue.empty():
                touch_info = self.touch_queue.get()

                if touch_info[2]:
                    self.clean_up()
                    if touch_info[2] == "back_button":
                        return "Stats"
                    else:
                        logging.critical("Button '{}' is not bound to a screen.".format(touch_info[2]))
                        terminate()
            else:
                if sleepiness >= 300: # Oddly enough, still a minute. I have no clue why.
                    return "Off Stats 2"
                else:
                    sleepiness += 1
            
            new_data = self.weather.request_weather_info(self.weather_queues, "stats", wait=True)
            if new_data:
                self.tft.update_element("sunrise_label", "text", "Sunrise: {}".format(new_data["sunrise"]))
                self.tft.update_element("sunset_label", "text", "Sunset: {}".format(new_data["sunset"]))

                self.tft.update_element("day_icon", "image", "weather_icons/{}.png".format(new_data["day_weather"]))
                self.tft.update_element("day_desc", "text", self.weather.get_weather_code(str(new_data["day_weather"] // 10)))

                self.tft.update_element("night_icon", "image", "weather_icons/{}.png".format(new_data["night_weather"]))
                self.tft.update_element("night_desc", "text", self.weather.get_weather_code(str(new_data["night_weather"] // 10)))

                self.tft.update_element("ice_label", "text", "Ice: {}%".format(new_data["ice"]))
                self.tft.update_element("snow_label", "text", "Snow: {}%".format(new_data["snow"]))
            
            day_phase = self.weather.get_day_phase(self.weather.request_weather_info(self.weather_queues, "day_phase"))
            self.tft.background(self.display_command, day_phase)

            self.tft.update_element(self.display_command, "time_label", "text", self.weather.current_time())
            sleep(0.1)

    def clean_up(self):
        self.tft.clear_screen(self.display_command, self.button_queue)