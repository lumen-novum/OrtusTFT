import multiprocessing
import logging
from sys import argv

from OrtusTFT import configure, interface, weather, screens

# Set default values
demo = False
logging_level = logging.INFO

if argv.count("--debug") == 1:
    logging_level = logging.DEBUG
logging.basicConfig(format="[%(levelname)s] [%(module)s:%(funcName)s]  %(message)s", level=logging_level)

if (argv.count("--demo") == 1 or
        argv.count("-d") == 1):
    logging.debug("Demo argument found. Running OrtusTFT demo...")
    demo = True
elif (argv.count("--setup") == 1 or
        argv.count("-s") == 1):    
    logging.debug("Setup argument found. Running OrtusTFT setup...")
    configure.main()
else:
    logging.debug("No extra arguments were found. Verifying config file and running OrtusTFT...")
    configure.verify_integrity()

if __name__ == "__main__":
    adafruit_tft = interface.setup(weather)
    
    weather_input = multiprocessing.Queue()
    weather_output = multiprocessing.Queue()

    touch_queue = multiprocessing.Queue() # Manages touch coordinates
    button_queue = multiprocessing.Queue() # Allows buttons to be created within the touch handler system
    display_command = multiprocessing.Queue() # Manages pygame and TFT

    touch_process = multiprocessing.Process(target=interface.touch_handler, args=(button_queue, touch_queue, demo))
    screen_process = multiprocessing.Process(target=interface.screen_handler, args=(display_command, button_queue, demo))
    weather_process = multiprocessing.Process(target=weather.weather_handler, args=(weather_input, weather_output))

    screens.init(display_command, touch_queue, button_queue, (weather_input, weather_output), demo)

    screen_process.start()
    touch_process.start()
    weather_process.start()

    current_screen = "Home"

    while True:
        if current_screen == "Home":
            current_screen = screens.home()
        elif current_screen == "Stats":
            current_screen = screens.weather_report(1)
        elif current_screen == "Stats 2":
            current_screen = screens.weather_report(2)
        elif current_screen == "About":
            current_screen = screens.about()
        elif current_screen[0:3] == "Off":
            current_screen = screens.sleep_screen(current_screen[4:len(current_screen)])
        else:
            current_screen = screens.wip()