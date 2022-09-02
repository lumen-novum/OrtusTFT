from time import sleep

class TempSleep:
    def __init__(self, necessities):
        self.tft, self.display_command, self.button_queue, self.touch_queue, self.weather_queues, self.weather = necessities
        
    def display(self, last_screen):      
        self.tft.create_element(self.display_command, self.tft.format_label("power", ((0, 0), (240, 320)), "topleft", fill=self.tft.BLACK, button=True), button_reg=self.button_queue)
        with open("/sys/class/backlight/soc:backlight/brightness", "w") as backlight:
            backlight.write("0")

        deep_sleep = 0
        reset_screen = False
        while True:
            if not self.touch_queue.empty():
                touch_info = self.touch_queue.get()

                if touch_info[2]:
                    self.clean_up()
                    if reset_screen:
                        return "Home"
                    else:
                        return last_screen

            if deep_sleep == 3000: # 5 minutes
                reset_screen = True
                deep_sleep = 3001
            elif deep_sleep < 3000:
                deep_sleep += 1
            sleep(0.1)

    def clean_up(self):
        self.tft.clear_screen(self.display_command, self.button_queue)
        with open("/sys/class/backlight/soc:backlight/brightness", "w") as backlight:
            backlight.write("1")