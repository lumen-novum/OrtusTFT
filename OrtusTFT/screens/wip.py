from time import sleep
from sys import exit as terminate

# As long as the "configure" module has been imported, we don't have to worry about creating a basic config.
import logging

class WorkInProgress:
    def __init__(self, necessities):
        self.tft, self.display_command, self.button_queue, self.touch_queue, self.weather_queues, self.weather = necessities

    def display(self):
        def cone_row(height):
            for cone_num in range(7):
                cone_pos = (cone_num * 32) + 8
                self.tft.create_element(self.display_command, self.tft.format_label(str(cone_num) + str(height), ((cone_pos, height), self.tft.MINI_ICON), "topleft", image="cone.png"))

        back_button = self.tft.format_label("back_button", ((5, 5), self.tft.MINI_ICON), "topleft", image="previous.png", button=True)
        self.tft.create_element(self.display_command, back_button, button_reg=self.button_queue)

        day_phase = self.weather.get_day_phase(self.weather.request_weather_info(self.weather_queues, "day_phase"))
        self.tft.background(self.display_command, day_phase)

        # TODO: Make '\n' a useable character :/
        title = self.tft.format_text("title", "WIP", "midtop", (120,90), "header")
        desc1 = self.tft.format_text("desc1", "This feature hasn't\nbeen implemented\nyet.", "midtop", (120,130), "subheader")
        #desc2 = self.tft.format_text("desc2", "been implemented", "midtop", (120,155), "subheader")
        #desc3 = self.tft.format_text("desc3", "yet.", "midtop", (120,180), "subheader")

        self.tft.create_element(self.display_command, title, desc1)

        cone_row(48)        
        cone_row(222)

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
                    return "Off WIP"
                else:
                    sleepiness += 1
            
            new_data = self.weather.request_weather_info(self.weather_queues, "day_phase", wait=True)

            if new_data:
                day_phase = self.weather.get_day_phase(new_data)
                self.tft.background(self.display_command, day_phase)
            sleep(0.1)

    def clean_up(self):
        self.tft.clear_screen(self.display_command, self.button_queue)