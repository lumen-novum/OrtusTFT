import pygame
import os
from time import sleep
import json
from sys import exit as terminate

# As long as the "configure" module has been imported, we don't have to worry about creating a basic config.
import logging


class Main:
    def __init__(self, notify, command, button_reg, demo):
        self.demo = demo

        self.SCREEN_SIZE = (240, 320)

        if not demo:
            import evdev
            
            if os.geteuid() != 0:
                logging.critical("Display cannot initalize without root access.")
                terminate()

            with open("OrtusTFT/info.json", "r") as data:
                display_data = json.load(data)

            self.X_CALIBRATION = display_data["display"]["xCalibration"]
            self.X_OFFSET = display_data["display"]["xOffset"]
            self.Y_CALIBRATION = display_data["display"]["yCalibration"]
            self.Y_OFFSET = display_data["display"]["yOffset"]

            os.putenv("SDL_FBDEV", "/dev/fb1")

            with open("/sys/class/backlight/soc:backlight/brightness", "w") as backlight:
                backlight.write("1")

            # Declare display and touchscreen input paths
            self.touchscreen = evdev.InputDevice("/dev/input/touchscreen")

        self.SCROLL_PAUSE = 120
        self.SCROLL_SPEED = 5

        self.WHITE = (255,255,255)
        self.BLACK = (0,0,0)           

        pygame.init()
        pygame.mouse.set_visible(demo)
        self.tft = pygame.display.set_mode(self.SCREEN_SIZE)
        self.tft.fill(self.WHITE)
        pygame.display.flip()
        self.clock = pygame.time.Clock()	

        self.image_list = {}
        self.DAY = pygame.image.load("/home/pi/OrtusTFT/OrtusTFT/assets/images/gradients/day.png").convert_alpha()
        self.NIGHT = pygame.image.load("/home/pi/OrtusTFT/OrtusTFT/assets/images/gradients/night.png").convert_alpha()
        self.SUNRISE = pygame.image.load("/home/pi/OrtusTFT/OrtusTFT/assets/images/gradients/sunrise.png").convert_alpha()
        self.SUNSET = pygame.image.load("/home/pi/OrtusTFT/OrtusTFT/assets/images/gradients/sunset.png").convert_alpha()
        self.time = "day"

        self.HEADER_FONT = pygame.font.Font("/home/pi/OrtusTFT/OrtusTFT/assets/fonts/bold.ttf", 30)
        self.SUBHEADER_FONT = pygame.font.Font("/home/pi/OrtusTFT/OrtusTFT/assets/fonts/main.ttf", 25)
        self.PARAGRAPH_FONT = pygame.font.Font("/home/pi/OrtusTFT/OrtusTFT/assets/fonts/light.ttf", 20)
        self.WEATHER_ICON = (72, 72)
        self.MINI_ICON = (32, 32)

        # Declare variables
        self.activated = False
        self.notify = notify
        self.command = command
        self.newbutton = button_reg

        self.buttons = {}
        self.scrolling_text = {}


    def touch_handler(self):
        def button_collsion(x,y):
            detected_button = None
            for button in self.buttons:
                hitbox = self.buttons[button]
                if hitbox.collidepoint(x, y):
                    detected_button = button
                    return detected_button

        while True:
            while not self.newbutton.empty():
                new = self.newbutton.get()

                if new == "clear":
                    self.buttons.clear()
                    break
                elif new[2] == "topright":
                    specs = new[1]
                    rect = pygame.Rect((specs[0][0]-specs[1][0], specs[0][1]), specs[1])
                else:
                    rect = pygame.Rect(new[1])

                self.buttons[new[0]] = rect

            if not self.demo:
                event = self.touchscreen.read_one()
                if event != None:
                    # Calculate where the screen is being pressed
                    raw_x = self.touchscreen.absinfo(0).value
                    raw_y = self.touchscreen.absinfo(1).value
                    pos_calc = lambda raw_xy, offset, cali: int((raw_xy - offset) / cali)

                    x_value = pos_calc(raw_x, self.X_OFFSET, self.X_CALIBRATION)
                    y_value = pos_calc(raw_y, self.Y_OFFSET, self.Y_CALIBRATION)
                    
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

                    self.notify.put([x_value, y_value, button_found])
                    
                    # Give time for the Raspberry Pi to respond to the press
                    sleep(1)

                    # Clear unnecessary "pressure" events
                    for _ in self.touchscreen.read():
                        pass
            elif self.demo:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x_value, y_value = pygame.mouse.get_pos()

                        button_found = button_collsion(x_value, y_value)

                        self.notify.put([x_value, y_value, button_found])
                    
                        # Give time for the Raspberry Pi to respond to the press
                        sleep(1)
                    
            sleep(0.1) # Check about 240 times a second for screen events

    def display_background(self):
        if self.time == "day":
            background = pygame.transform.scale(self.DAY, (240, 320))
        elif self.time == "night":
            background = pygame.transform.scale(self.NIGHT, (240, 320))
        elif self.time == "morning":
            background = pygame.transform.scale(self.SUNRISE, (240, 320))
        elif self.time == "evening":
            background = pygame.transform.scale(self.SUNSET, (240, 320))

        self.tft.blit(background, (0, 0))

    def text_label(self, text, alignment, position, font):
        def wait(time):
            if self.scrolling_text[text]["time_waiting"] < time:
                self.scrolling_text[text]["time_waiting"] += 1
                return True

            self.scrolling_text[text]["time_waiting"] = 0
            return False
        
        def start(text):
            self.scrolling_text[text]["index"] = 20
            return text[0:20]

        def current(text):
            index = self.scrolling_text[text]["index"]
            return text[index-20:index]
        
        for line in text.splitlines():
            if self.scrolling_text.get(line):
                if self.scrolling_text[text]["index"] == 20:
                    if wait(self.SCROLL_PAUSE):
                        line = start(line)
                    else:
                        self.scrolling_text[line]["index"] += 1
                        line = current(line)
                elif self.scrolling_text[line]["index"] < len(line):
                    if wait(self.SCROLL_SPEED):
                        line = current(line)
                    else:
                        self.scrolling_text[line]["index"] += 1
                        line = current(line)
                else:
                    if wait(self.SCROLL_PAUSE):
                        line = current(line)
                    else:
                        line = start(line)
            elif len(line) > 20 and font == "paragraph":
                self.scrolling_text[line] = {"index": 20, "time_waiting": 0}
                line = line[0:20]

            if self.time == "night":
                color = self.WHITE
            else:
                color = self.BLACK

            if font == "header":
                pyg_font = self.HEADER_FONT
                text_box = self.HEADER_FONT.render(line, True, color)
            elif font == "subheader":
                pyg_font = self.SUBHEADER_FONT
                text_box = self.SUBHEADER_FONT.render(line, True, color)
            elif font == "paragraph":
                pyg_font = self.PARAGRAPH_FONT
                text_box = self.PARAGRAPH_FONT.render(line, True, color)
            else:
                logging.critical("Invaild font type: {}".format(font))
                terminate()

            if alignment == "topleft":
                text_position = text_box.get_rect(topleft= position)
            elif alignment == "midtop":
                text_position = text_box.get_rect(midtop= position)
            self.tft.blit(text_box, text_position)
            position = list(position)
            position[1] += pygame.font.Font.size(pyg_font, line)[1]

    def label(self, image, rect, alignment, fill, outline):
        #if outline:
        #    pygame.draw.rect(self.tft, outline, pygame.Rect(rect))

        if fill:
            self.tft.fill(fill, pygame.Rect(rect))

        if image:
            image = pygame.transform.scale(self.image_list[image], rect[1])

            if alignment == "topleft":
                rectangle = image.get_rect(topleft= rect[0])
            elif alignment == "midtop":
                rectangle = image.get_rect(midtop= rect[0])
            elif alignment == "topright":
                rectangle = image.get_rect(topright= rect[0])
            else:
                logging.critical("Expected valid rect alignment, got: {}".format(alignment))
                terminate()

            self.tft.blit(image, rectangle)

    def screen_handler(self):
        screen_objects = []
        object_indexes = []

        while True:
            self.display_background()

            while not self.command.empty():
                command_info = self.command.get()
                if command_info["request"] == "create":
                    if object_indexes.count(command_info["element"]["id"]) == 0:
                        properties = command_info["element"]["properties"]
                        if properties.get("image") != self.image_list.get(properties.get("image")):
                            self.image_list[properties["image"]] = (pygame.image.load("/home/pi/OrtusTFT/OrtusTFT/assets/images/" + properties["image"]).convert_alpha())

                        screen_objects.append(command_info["element"])
                        object_indexes.append(command_info["element"]["id"])
                    else:
                        logging.critical("An object with a duplicate id was made. ID: {}".format(command_info["element"]["id"]))
                        terminate()
                elif command_info["request"] == "update":
                    if command_info["aspect"] == "image" and command_info["data"] != self.image_list.get(command_info["data"]):
                        self.image_list[command_info["data"]] = (pygame.image.load("/home/pi/OrtusTFT/OrtusTFT/assets/images/" + command_info["data"]).convert_alpha())

                    element_index = object_indexes.index(command_info["id"])
                    screen_objects[element_index]["properties"][command_info["aspect"]] = command_info["data"]
                elif command_info["request"] == "remove":
                    element_index = object_indexes.index(command_info["id"])
                    screen_objects.pop(element_index)
                    object_indexes.pop(element_index)
                elif command_info["request"] == "clear":
                    screen_objects.clear()
                    object_indexes.clear()
                    self.scrolling_text.clear()
                elif command_info["request"] == "background":
                    self.time = command_info["time_of_day"]

            for item in screen_objects:
                if item["type"] == "text_label":
                    property = item["properties"]
                    self.text_label(property["text"], property["alignment"], property["position"], property["size"])
                elif item["type"] == "button" or item["type"] == "label":
                    property = item["properties"]
                    self.label(property["image"], property["rect"], property["alignment"], property["fill"], property["outline"])  

            self.clock.tick(24)
            pygame.display.flip()
            self.tft.fill(self.WHITE)

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

    def close(self):
        pass
        #self.signal_term.value = True
