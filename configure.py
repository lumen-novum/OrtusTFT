import json
import requests
import pygame
import evdev
import os
from sys import exit as terminate

import logging
logging.basicConfig(format="[%(levelname)s] [%(module)s:%(funcName)s]  %(message)s", level=logging.INFO)

# Print a question, wait for a valid answer.
def ask_question(question, valid_answers=None):
    answer = input(question).strip()
    while True:
        if valid_answers:
            for valid_answer in valid_answers:
                if answer == valid_answer:
                    return answer
        else:
            if answer != "":
                return answer
        answer = input("Sorry, your answer is invaild. Please try again: ").strip()


# Check to see if configuration data exists. If not, run whatever setup function is needed to start OrtusTFT
def verify_file():
    try:
        with open("OrtusTFT/info.json", "r") as json_file:
            data_verify = json.load(json_file)

            # Check for a name, weather api key, and display calibration.
            if not data_verify["name"]:
                logging.warn("There is no name provided. Running OrtusTFT setup...")
                save_info(name=get_name())
            if not data_verify["weather"].get("apikey"):
                logging.warn("The weather api is invalid. Running OrtusTFT setup...")
                save_info(weather=weather_setup())
            if not data_verify["display"].get("xOffset"):
                logging.warn("The display is not calibrated. Running OrtusTFT setup...")
                save_info(display=display_setup())
    except FileNotFoundError:
        logging.warn("info.json not found. Running OrtusTFT setup...")
        with open("OrtusTFT/info.json", "w") as info_json:
            newdict = {"_comment": "Please do not edit this file.",
                    "_": "If you need to change a value, run 'configure.py' again.",
                    "name": "",
                    "weather": {},
                    "display": {}
                    }
            json_object = json.dumps(newdict, indent=4)
            info_json.write(json_object)


# Save data into info.json
def save_info(name=None, weather=None, display=None):
    with open("OrtusTFT/info.json", "r") as old_data:
        json_object = json.load(old_data)

    if name:
        json_object["name"] = name
    if weather:
        json_object["weather"] = weather
    if display:
        json_object["display"] = display

    with open("OrtusTFT/info.json", "w") as weather_json:
        json_object = json.dumps(json_object, indent=4)
        weather_json.write(json_object)


# Gather information necessary to make a weather request.
def weather_setup():
    def failure(error_message):
        logging.error("\n" + error_message)
        answer = ask_question("Would you like to rerun the [w]eather setup or [e]xit the program? ", valid_answers="we")
        if answer == "w":
            return weather_setup()
        else:
            exit()
    
    coordinates = ask_question("What are the coordinates of your location? Format: (XX, XX) ").strip("()")

    unit = ask_question("Would you like to use [m]etric or [i]mperial units? ", valid_answers="im")
    if unit == "i":
        unit = "imperial"
    else:
        unit = "metric"

    timezone = ask_question("What is your timezone? Ex. America/Chicago ")
    key = ask_question("What is your Tomorrow.io secret key? ")

    login = {
            "units": unit,
            "apikey": key,
            "timezone": timezone,
            "location": coordinates,
            "timesteps": "1d",
            "fields": ["temperature"]
            }
    
    data = (requests.request("GET", "https://api.tomorrow.io/v4/timelines", params=login)).json()

    if data.get("data") is not None:
        print("\nCongratulations, you can now request weather information!")
        login.pop("timesteps")
        login.pop("fields")
        return login
    else:
        if data["code"] == 401001:
            return failure("Error: The API key you entered was invaild.")
        elif data["message"].find("location") != -1:
            return failure("Error: The location coordinates you entered were invaild.")
        elif data["message"].find("timezone") != -1:
            return failure("Error: The timezone you entered was invaild.")
        return failure("Unfortunately, there was an unknown error while sending a request. Error info: {}".format(data["message"]))


# Calibrate display so it can properly recieve screen presses.
def display_setup():
    if os.geteuid() != 0:
        logging.critical("Display cannot initalize without root access.")
        terminate()

    with open("/sys/class/backlight/soc:backlight/brightness", "w") as backlight:
        backlight.write("1")
    
    SCREEN_SIZE = (240, 320)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)
    MINI_ICON = (32, 32)
    SECOND_ICON_POS = (208, 288)

    # Prepare pygame
    os.putenv("SDL_FBDEV", "/dev/fb1")
    pygame.init()
    pygame.mouse.set_visible(False)
    tft = pygame.display.set_mode(SCREEN_SIZE)
    tft.fill(WHITE)
    pygame.display.flip()
    clock = pygame.time.Clock()

     # Declare display and touchscreen input paths
    touchscreen = evdev.InputDevice("/dev/input/touchscreen")

    print("Please touch all of the black squares that appear on screen.")
    active = False
    button_held = 0
    stage = 0
    x_value = 500
    y_value = 500

    exit_button = pygame.Rect(0, 0, 32, 32)

    while True:
        event = touchscreen.read_one()
        if event != None:
            raw_x = touchscreen.absinfo(0).value
            raw_y = touchscreen.absinfo(1).value

            active = True
            if button_held < 100:
                button_held += 1
            elif button_held == 100:
                stage = 0
                active = False
        elif event == None and active:
            button_held = 0

            if stage == 0:
                x_offset = raw_x
                y_offset = raw_y
            elif stage == 1:
                x_calibration = int((raw_x - x_offset) / 240)
                y_calibration = int((raw_y - y_offset) / 320)

                # This should fix rare occurrences of the screen registering two presses instead of one.
                if x_calibration == 0 or y_calibration == 0:
                    logging.error("There was a problem while calibrating the screen. Reseting calibration...")
                    stage = 0

                print("\nThe touch system has been calibrated. Feel free to touch around to make sure your system is working properly.")
                print("If you need to try again, hold the screen down until the black squares reappear.")
                print("To exit, touch the green square's bottom right corner.\n")
            else:
                pos_calc = lambda raw_xy, offset, cali: int((raw_xy - offset) / cali)

                x_value = pos_calc(raw_x, x_offset, x_calibration)
                y_value = pos_calc(raw_y, y_offset, y_calibration)

                if exit_button.collidepoint(x_value, y_value):
                    return {
                        "xCalibration": x_calibration,
                        "xOffset": x_offset,
                        "yCalibration": y_calibration,
                        "yOffset": y_offset
                    }
            active = False
            stage += 1
        else:
            button_held = 0
        
        if stage == 0:
            tft.fill(BLACK, pygame.Rect((0, 0), MINI_ICON))
        elif stage == 1:
            tft.fill(BLACK, pygame.Rect(SECOND_ICON_POS, MINI_ICON))
        else:
            tft.fill(RED, pygame.Rect((x_value - 16, y_value - 16), MINI_ICON))
            tft.fill(GREEN, exit_button)
        
        pygame.display.flip()
        tft.fill(WHITE)
        clock.tick(240)

def get_name():
    return ask_question("What is your name? ")


# Run all setup functions
def setup():
    name = get_name()
    weather_login = weather_setup()
    display_calibration = display_setup()
    save_info(name=name, weather=weather_login, display=display_calibration)

if __name__ == "__main__":
    begin = ask_question("\nHi, welcome to the OrtusTFT setup. Would you like to [r]eset everything, reset the [d]isplay calibration, reset the [w]eather login, or change your [n]ame? ", valid_answers="rdwn")
    
    if begin == "r":
        setup()
    elif begin == "n":
        save_info(name=get_name())
    elif begin == "w":
        weather_login = weather_setup()
        save_info(weather=weather_login)
    elif begin == "d":
        display_calibration = display_setup()
        save_info(display=display_calibration)
    
    print("\nThe setup has completed. You may now run OrtusTFT.")
else:
    # Checks to see if necessary data is available before starting OrtusTFT
    verify_file()
