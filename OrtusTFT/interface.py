import pygame
import os
import weather
from time import sleep
import json
from sys import exit as terminate

# As long as the "configure" module has been imported, we don't have to worry about creating a basic config.
import logging

SCREEN_SIZE = (240, 320)
RELATIVE_PATH = os.path.dirname(__file__)
logging.debug("Current Pygame path is: {}".format(RELATIVE_PATH))

SCROLL_PAUSE = 120
SCROLL_SPEED = 5

WHITE = (255,255,255)
BLACK = (0,0,0)    
WEATHER_ICON = (72, 72)
MINI_ICON = (32, 32)

time = "day"

def setup(demo):
    if not demo:
        if os.geteuid() != 0:
            logging.critical("Display cannot initalize without root access.")
            terminate()

        os.putenv("SDL_FBDEV", "/dev/fb1")

        with open("/sys/class/backlight/soc:backlight/brightness", "w") as backlight:
            backlight.write("1")       

    pygame.init()
    pygame.mouse.set_visible(demo)
    tft = pygame.display.set_mode(SCREEN_SIZE)
    tft.fill(WHITE)
    pygame.display.flip()

    HEADER_FONT = pygame.font.Font("{}/assets/fonts/bold.ttf".format(RELATIVE_PATH), 30)
    SUBHEADER_FONT = pygame.font.Font("{}/assets/fonts/main.ttf".format(RELATIVE_PATH), 25)
    PARAGRAPH_FONT = pygame.font.Font("{}/assets/fonts/light.ttf".format(RELATIVE_PATH), 20)

# Declare variables
activated = False
notify = notify
command = command
newbutton = button_reg

def touch_handler():
    def button_collsion(x,y):
        detected_button = None
        for button in buttons:
            hitbox = buttons[button]
            if hitbox.collidepoint(x, y):
                detected_button = button
                return detected_button

    # Not very pythonic, but it allows people who are running the demo to skip installing an unnecessary package
    import evdev

    # Declare display and touchscreen input paths
    touchscreen = evdev.InputDevice("/dev/input/touchscreen")

    display_data = weather.read_local_data("display")
    X_CALIBRATION = display_data["xCalibration"]
    X_OFFSET = display_data["xOffset"]
    Y_CALIBRATION = display_data["yCalibration"]
    Y_OFFSET = display_data["yOffset"]

    while True:
        while not newbutton.empty():
            new = newbutton.get()

            if new == "clear":
                buttons.clear()
                break
            elif new[2] == "topright":
                specs = new[1]
                rect = pygame.Rect((specs[0][0]-specs[1][0], specs[0][1]), specs[1])
            else:
                rect = pygame.Rect(new[1])

            buttons[new[0]] = rect

            event = touchscreen.read_one()
            if event != None:
                # Calculate where the screen is being pressed
                raw_x = touchscreen.absinfo(0).value
                raw_y = touchscreen.absinfo(1).value
                pos_calc = lambda raw_xy, offset, cali: int((raw_xy - offset) / cali)

                x_value = pos_calc(raw_x, X_OFFSET, X_CALIBRATION)
                y_value = pos_calc(raw_y, Y_OFFSET, Y_CALIBRATION)
                
                # If x or y values overflow, set the value to the max.
                # If x or y values underflow, set the value to the min.
                if x_value < 0:
                    x_value = 0
                elif x_value > 240:
                    x_value = 240

                if y_value < 0:
                    y_value = 0
                elif y_value > 320:
                    y_value = 320
            
                # Loop through all buttons to see if one of them 
                # collides with where the screen was pressed
                
                button_found = button_collsion(x_value, y_value)

                notify.put([x_value, y_value, button_found])
                
                # Give time for the Raspberry Pi to respond to the press
                sleep(1)

                # Clear unnecessary "pressure" events
                for _ in touchscreen.read():
                    pass

            
                
        sleep(0.1) # Check about 240 times a second for screen events

def display_background(self):
    if time == "day":
        DAY = pygame.image.load("{}/assets/images/gradients/day.png".format(RELATIVE_PATH)).convert_alpha()
        background = pygame.transform.scale(DAY, (240, 320))
    elif time == "night":
        NIGHT = pygame.image.load("{}/assets/images/gradients/night.png".format(RELATIVE_PATH)).convert_alpha()
        background = pygame.transform.scale(NIGHT, (240, 320))
    elif time == "morning":
        SUNRISE = pygame.image.load("{}/assets/images/gradients/sunrise.png".format(RELATIVE_PATH)).convert_alpha()
        background = pygame.transform.scale(SUNRISE, (240, 320))
    elif time == "evening":
        SUNSET = pygame.image.load("{}/assets/images/gradients/sunset.png".format(RELATIVE_PATH)).convert_alpha()
        background = pygame.transform.scale(SUNSET, (240, 320))

    tft.blit(background, (0, 0))

def text_label(self, text, alignment, position, font):
    def wait(time):
        if scrolling_text[text]["time_waiting"] < time:
            scrolling_text[text]["time_waiting"] += 1
            return True

        scrolling_text[text]["time_waiting"] = 0
        return False
    
    def start(text):
        scrolling_text[text]["index"] = 20
        return text[0:20]

    def current(text):
        index = scrolling_text[text]["index"]
        return text[index-20:index]
    
    for line in text.splitlines():
        if scrolling_text.get(line):
            if scrolling_text[text]["index"] == 20:
                if wait(SCROLL_PAUSE):
                    line = start(line)
                else:
                    scrolling_text[line]["index"] += 1
                    line = current(line)
            elif scrolling_text[line]["index"] < len(line):
                if wait(SCROLL_SPEED):
                    line = current(line)
                else:
                    scrolling_text[line]["index"] += 1
                    line = current(line)
            else:
                if wait(SCROLL_PAUSE):
                    line = current(line)
                else:
                    line = start(line)
        elif len(line) > 20 and font == "paragraph":
            scrolling_text[line] = {"index": 20, "time_waiting": 0}
            line = line[0:20]

        if time == "night":
            color = WHITE
        else:
            color = BLACK

        if font == "header":
            pyg_font = HEADER_FONT
            text_box = HEADER_FONT.render(line, True, color)
        elif font == "subheader":
            pyg_font = SUBHEADER_FONT
            text_box = SUBHEADER_FONT.render(line, True, color)
        elif font == "paragraph":
            pyg_font = PARAGRAPH_FONT
            text_box = PARAGRAPH_FONT.render(line, True, color)
        else:
            logging.critical("Invaild font type: {}".format(font))
            terminate()

        if alignment == "topleft":
            text_position = text_box.get_rect(topleft= position)
        elif alignment == "midtop":
            text_position = text_box.get_rect(midtop= position)
        tft.blit(text_box, text_position)
        position = list(position)
        position[1] += pygame.font.Font.size(pyg_font, line)[1]

def label(self, image, rect, alignment, fill, outline):
    #if outline:
    #    pygame.draw.rect(tft, outline, pygame.Rect(rect))

    if fill:
        tft.fill(fill, pygame.Rect(rect))

    if image:
        image = pygame.transform.scale(image_list[image], rect[1])

        if alignment == "topleft":
            rectangle = image.get_rect(topleft= rect[0])
        elif alignment == "midtop":
            rectangle = image.get_rect(midtop= rect[0])
        elif alignment == "topright":
            rectangle = image.get_rect(topright= rect[0])
        else:
            logging.critical("Expected valid rect alignment, got: {}".format(alignment))
            terminate()

        tft.blit(image, rectangle)

def screen_handler():
    clock = pygame.time.Clock()	
    screen_objects = list()
    object_indexes = list()
    image_list = dict()

    while True:
        display_background()

        while not command.empty():
            command_info = command.get()
            if command_info["request"] == "create":
                if object_indexes.count(command_info["element"]["id"]) == 0:
                    properties = command_info["element"]["properties"]
                    if properties.get("image") != image_list.get(properties.get("image")):
                        image_list[properties["image"]] = (pygame.image.load("{}/assets/images/".format(RELATIVE_PATH) + properties["image"]).convert_alpha())

                    screen_objects.append(command_info["element"])
                    object_indexes.append(command_info["element"]["id"])
                else:
                    logging.critical("An object with a duplicate id was made. ID: {}".format(command_info["element"]["id"]))
                    terminate()
            elif command_info["request"] == "update":
                if command_info["aspect"] == "image" and command_info["data"] != image_list.get(command_info["data"]):
                    image_list[command_info["data"]] = (pygame.image.load("{}/assets/images/".format(RELATIVE_PATH) + command_info["data"]).convert_alpha())

                element_index = object_indexes.index(command_info["id"])
                screen_objects[element_index]["properties"][command_info["aspect"]] = command_info["data"]
            elif command_info["request"] == "remove":
                element_index = object_indexes.index(command_info["id"])
                screen_objects.pop(element_index)
                object_indexes.pop(element_index)
            elif command_info["request"] == "clear":
                screen_objects.clear()
                object_indexes.clear()
                scrolling_text.clear()
            elif command_info["request"] == "background":
                time = command_info["time_of_day"]

        for item in screen_objects:
            if item["type"] == "text_label":
                property = item["properties"]
                text_label(property["text"], property["alignment"], property["position"], property["size"])
            elif item["type"] == "button" or item["type"] == "label":
                property = item["properties"]
                label(property["image"], property["rect"], property["alignment"], property["fill"], property["outline"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x_value, y_value = pygame.mouse.get_pos()

                button_found = button_collsion(x_value, y_value)

                notify.put([x_value, y_value, button_found])
                
                # Give time for the Raspberry Pi to respond to the press
                sleep(1)

        clock.tick(24)
        pygame.display.flip()
        tft.fill(WHITE)

@staticmethod
def format_text(id, text, alignment, position, size):
    return {
        "id": id,
        "type": "text_label",
        "properties": {
            "text": text,
            "alignment": alignment,
            "position": position,
            "size": size
        }
    }

@staticmethod
def format_label(id, rect, alignment, image=None, fill=None, outline=None, button=False):
    inital_element = {
        "id": id,
        "type": "label",
        "properties": {
            "image": image,
            "alignment": alignment,
            "rect": rect,
            "fill": fill,
            "outline": outline
        }
    }

    if button:
        inital_element["type"] = "button"

    return inital_element

@staticmethod
def create_element(queue, *elements, button_reg=None):
    for element in elements:
        queue.put({"request": "create", "element": element})
        if element["type"] == "button":
            if not button_reg:
                logging.critical("Unable to create button: '{}' due to the lack of a queue.".format(element["id"]))
                terminate()

            button_reg.put((element["id"], element["properties"]["rect"], element["properties"]["alignment"]))

@staticmethod
def update_element(queue, id, aspect, data):
    queue.put({"request": "update", "id": id, "aspect": aspect, "data": data})

@staticmethod
def remove_element(queue, id):
    queue.put({"request": "remove", "id": id})

@staticmethod
def clear_screen(screen, button):
    screen.put({"request": "clear"})
    button.put("clear")
        
@staticmethod
def background(queue, time_of_day):
    queue.put({"request": "background", "time_of_day": time_of_day})