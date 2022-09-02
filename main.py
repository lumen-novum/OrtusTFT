import configure # Verifies that the necessary info is there to start OrtusTFT

import OrtusTFT.interface
import OrtusTFT.weather
from OrtusTFT.screens import home, statistics, about, wip, sleep_screen

import multiprocessing

if __name__ == "__main__":
    try:
        weather_queues = (multiprocessing.Queue(), multiprocessing.Queue())
        weather = OrtusTFT.weather.Weather(weather_queues)

        touch_queue = multiprocessing.Queue() # Manages touch coordinates
        button_queue = multiprocessing.Queue() # Allows buttons to be created within the touch handler system
        display_command = multiprocessing.Queue() # Manages pygame and TFT
        tft = OrtusTFT.interface.Main(touch_queue, display_command, button_queue)
    
        touch_process = multiprocessing.Process(target=tft.touch_handler, args=())
        screen_process = multiprocessing.Process(target=tft.screen_handler, args=())
        weather_process = multiprocessing.Process(target=weather.weather_handler, args=())

        touch_process.start()
        screen_process.start()
        weather_process.start()

        current_screen = "Home"

        necessities = (tft, display_command, button_queue, touch_queue, weather_queues, weather)
        hs = home.HomeScreen(necessities)
        weather_stats = statistics.StatScreen(necessities)
        about_page = about.AboutScreen(necessities)
        wip_page = wip.WorkInProgress(necessities)
        power_off = sleep_screen.TempSleep(necessities)

        while True:
            if current_screen == "Home":
                current_screen = hs.display()
            elif current_screen == "Stats":
                current_screen = weather_stats.display()
            elif current_screen == "Stats 2":
                current_screen = weather_stats.display_second_page()
            elif current_screen == "About":
                current_screen = about_page.display()
            elif current_screen[0:3] == "Off":
                current_screen = power_off.display(current_screen[4:len(current_screen)])
            else:
                current_screen = wip_page.display()


    finally:
        # TODO: Introduce proper cleanup
        pass