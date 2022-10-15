from time import sleep
from sys import exit as terminate

# As long as the "configure" module has been imported, we don't have to worry about creating a basic config.
import logging



class AboutScreen:
    def __init__(self, necessities):
        self.tft, self.display_command, self.button_queue, self.touch_queue, self.weather_queues, self.weather, self.demo = necessities
    
    def display(self):
        back_button = self.tft.format_label("back_button", ((5, 5), self.tft.MINI_ICON), "topleft", image="previous.png", button=True)
        self.tft.create_element(self.display_command, back_button, button_reg=self.button_queue)

        title = self.tft.format_text("title", "OrtusTFT", "midtop", (120,40), "header")
        author = self.tft.format_text("author", "Developed by:", "midtop", (120,80), "subheader")
        name = self.tft.format_text("name", "lumen-novum", "midtop", (120,105), "subheader")

        qr_code = self.tft.format_label("qr_code", ((120, 140), (100, 100)), "midtop", image="qr.png")
        side_note = self.tft.format_text("side_note", "(Github page)", "midtop", (120,240), "paragraph")

        version = self.tft.format_text("version", "V0.1.0", "midtop", (120,290), "paragraph")
        
        self.tft.create_element(self.display_command, title, author, name, qr_code, side_note, version)

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

    def clean_up(self):
        self.tft.clear_screen(self.display_command, self.button_queue)