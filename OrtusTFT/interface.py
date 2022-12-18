import pygame
import os

from sys import exit as terminate
from OrtusTFT import weather
from time import sleep

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

def touch_handler(newbutton, send_press, demo):
    buttons = {}

    def button_collsion(x,y):
        detected_button = None
        for button in buttons:
            hitbox = buttons[button]
            if hitbox.collidepoint(x, y):
                detected_button = button
                return detected_button

    if not demo:
        # Not very pythonic, but it allows people who are running the demo to skip installing an unnecessary package
        import evdev

        # Declare display and touchscreen input paths
        touchscreen = evdev.InputDevice("/dev/input/touchscreen")

        display_data = weather.read_local_data("display")
        X_CALIBRATION = display_data["xCalibration"]
        X_OFFSET = display_data["xOffset"]
        Y_CALIBRATION = display_data["yCalibration"]
        Y_OFFSET = display_data["yOffset"]

    x_value = 0
    y_value = 0
    is_pressed = False

    while True:
        while not newbutton.empty():
            new = newbutton.get()

            if new == "clear":
                buttons.clear()
                break
            elif new[2] == "topright":
                specs = new[1]
                rect = pygame.Rect((specs[0][0]-specs[1][0], specs[0][1]), specs[1])
            elif new[0] == "pygame_click":
                x_value = new[1]
                y_value = new[2]
                is_pressed = True
            else:
                rect = pygame.Rect(new[1]) 

            buttons[new[0]] = rect

        if not demo:
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
        
        if is_pressed:
            button_found = button_collsion(x_value, y_value)

            send_press.put([x_value, y_value, button_found])
        
            # If using real hardware, clean up touch events
            if not demo:
                # Give time for the Raspberry Pi to respond to the press
                sleep(1)

                # Clear unnecessary "pressure" events
                for _ in touchscreen.read():
                    pass
            is_pressed = False

            
                
        sleep(0.1) # Check about 240 times a second for screen events

def display_background(day_phase):
    if day_phase == "day":
        DAY = pygame.image.load("{}/assets/images/gradients/day.png".format(RELATIVE_PATH)).convert_alpha()
        background = pygame.transform.scale(DAY, (240, 320))
    elif day_phase == "night":
        NIGHT = pygame.image.load("{}/assets/images/gradients/night.png".format(RELATIVE_PATH)).convert_alpha()
        background = pygame.transform.scale(NIGHT, (240, 320))
    elif day_phase == "morning":
        SUNRISE = pygame.image.load("{}/assets/images/gradients/sunrise.png".format(RELATIVE_PATH)).convert_alpha()
        background = pygame.transform.scale(SUNRISE, (240, 320))
    elif day_phase == "evening":
        SUNSET = pygame.image.load("{}/assets/images/gradients/sunset.png".format(RELATIVE_PATH)).convert_alpha()
        background = pygame.transform.scale(SUNSET, (240, 320))

    return background

class TextLabel:
    def __init__(self, day_phase, text_properties):
        self.type = "text_label"
        self.text = text_properties["text"]
        self.alignment = text_properties["alignment"]
        self.position = text_properties["position"]
        self.og_position = text_properties["position"]
        self.font = text_properties["size"]
        self.day_phase = day_phase

        self.scrolling_index = -1
        self.scrolling_waiting = 0

        self.text_boxes = {}

        for line in self.text.splitlines():
            if len(line) > 20 and self.font == "paragraph":
                self.scrolling_index = 20
                line = line[0:20]

            if self.day_phase == "night":
                color = WHITE
            else:
                color = BLACK

            if self.font == "header":
                pyg_font = HEADER_FONT
                text_box = HEADER_FONT.render(line, True, color)
            elif self.font == "subheader":
                pyg_font = SUBHEADER_FONT
                text_box = SUBHEADER_FONT.render(line, True, color)
            elif self.font == "paragraph":
                pyg_font = PARAGRAPH_FONT
                text_box = PARAGRAPH_FONT.render(line, True, color)
            else:
                logging.critical("Invaild font type: {}".format(self.font))
                terminate()

            if self.alignment == "topleft":
                text_position = text_box.get_rect(topleft= self.position)
            elif self.alignment == "midtop":
                text_position = text_box.get_rect(midtop= self.position)
            #tft.blit(text_box, text_position)
            self.text_boxes[text_box] = text_position
            self.position = list(self.position)
            self.position[1] += pygame.font.Font.size(pyg_font, line)[1]
    
    def redraw(self):
        self.position = self.og_position
        self.text_boxes.clear()
        for line in self.text.splitlines():
            if len(line) > 20 and self.font == "paragraph":
                self.scrolling_index = 20
                line = line[0:20]

            if self.day_phase == "night":
                color = WHITE
            else:
                color = BLACK

            if self.font == "header":
                pyg_font = HEADER_FONT
                text_box = HEADER_FONT.render(line, True, color)
            elif self.font == "subheader":
                pyg_font = SUBHEADER_FONT
                text_box = SUBHEADER_FONT.render(line, True, color)
            elif self.font == "paragraph":
                pyg_font = PARAGRAPH_FONT
                text_box = PARAGRAPH_FONT.render(line, True, color)
            else:
                logging.critical("Invaild font type: {}".format(self.font))
                terminate()

            if self.alignment == "topleft":
                text_position = text_box.get_rect(topleft= self.position)
            elif self.alignment == "midtop":
                text_position = text_box.get_rect(midtop= self.position)
            #tft.blit(text_box, text_position)
            self.text_boxes[text_box] = text_position
            self.position = list(self.position)
            self.position[1] += pygame.font.Font.size(pyg_font, line)[1]

    def wait(self, time):
        if self.scrolling_waiting < time:
            self.scrolling_waiting += 1
            return True

        self.scrolling_waiting = 0
        return False
    
    def start(self, text):
        self.scrolling_index = 20
        return text[0:20]

    def current(self, text):
        index = self.scrolling_index
        return text[index-20:index]
    
    def scroll_text(self):
        if self.scrolling_index == 20:
            if self.wait(SCROLL_PAUSE):
                line = self.start(line)
            else:
                self.scrolling_index += 1
                line = self.current(line)
        elif self.scrolling_index < len(line):
            if self.wait(SCROLL_SPEED):
                line = self.current(line)
            else:
                self.scrolling_index += 1
                line = self.current(line)
        else:
            if self.wait(SCROLL_PAUSE):
                line = self.current(line)
            else:
                line = self.start(line)

class Label:
    def __init__(self, image, other_properties):
        self.image = image
        self.type = "label"
        self.rect = other_properties["rect"]
        self.alignment = other_properties["alignment"]
        self.fill = other_properties["fill"]
        self.outline = other_properties["outline"]

        if image:
            self.image = pygame.transform.scale(image, self.rect[1])
            if self.alignment == "topleft":
                self.rectangle = self.image.get_rect(topleft= self.rect[0])
            elif self.alignment == "midtop":
                self.rectangle = self.image.get_rect(midtop= self.rect[0])
            elif self.alignment == "topright":
                self.rectangle = self.image.get_rect(topright= self.rect[0])
            else:
                logging.critical("Expected valid rect alignment, got: {}".format(self.alignment))
                terminate()

    #if outline:
    #    pygame.draw.rect(tft, outline, pygame.Rect(rect))

def screen_handler(display_queue, notify_touch_sys, demo):
    clock = pygame.time.Clock()	
    screen_objects, object_indexes = list(), list()
    image_list, scrolling_text = dict(), dict()

    day_phase = "day"

    if not demo:
        if os.geteuid() != 0:
            logging.critical("Display cannot initalize without root access.")
            terminate()

        os.putenv("SDL_FBDEV", "/dev/fb1")

        with open("/sys/class/backlight/soc:backlight/brightness", "w") as backlight:
            backlight.write("1")       

    global HEADER_FONT, SUBHEADER_FONT, PARAGRAPH_FONT

    pygame.init()
    pygame.mouse.set_visible(demo)

    if demo:
        pygame.display.set_caption("OrtusTFT")

    tft = pygame.display.set_mode(SCREEN_SIZE)
    
    tft.fill(WHITE)
    pygame.display.flip()

    HEADER_FONT = pygame.font.Font("{}/assets/fonts/bold.ttf".format(RELATIVE_PATH), 30)
    SUBHEADER_FONT = pygame.font.Font("{}/assets/fonts/main.ttf".format(RELATIVE_PATH), 25)
    PARAGRAPH_FONT = pygame.font.Font("{}/assets/fonts/light.ttf".format(RELATIVE_PATH), 20)

    while True:
        tft.blit(display_background(day_phase), (0, 0))

        while not display_queue.empty():
            command_info = display_queue.get()
            if command_info["request"] == "create":
                if object_indexes.count(command_info["element"]["id"]) == 0:
                    properties = command_info["element"]["properties"]
                    if properties.get("image") != image_list.get(properties.get("image")):
                        image_list[properties["image"]] = (pygame.image.load("{}/assets/images/".format(RELATIVE_PATH) + properties["image"]).convert_alpha())

                    if command_info["element"]["type"] == "text_label":
                        screen_objects.append(TextLabel(day_phase, command_info["element"]["properties"]))
                    elif command_info["element"]["type"] == "label" or command_info["element"]["type"] == "button":
                        new_image = None
                        if properties["image"] != None:
                            new_image = image_list[properties["image"]]
                        screen_objects.append(Label(new_image, properties))
                    else:
                        logging.warning("Recieved element type of {}. Skipping element.".format(command_info["element"]["type"]))

                    object_indexes.append(command_info["element"]["id"])
                else:
                    logging.critical("An object with a duplicate id was made. ID: {}".format(command_info["element"]["id"]))
                    terminate()
            elif command_info["request"] == "update":
                if command_info["aspect"] == "image" and command_info["data"] != image_list.get(command_info["data"]):
                    image_list[command_info["data"]] = (pygame.image.load("{}/assets/images/".format(RELATIVE_PATH) + command_info["data"]).convert_alpha())

                element_index = object_indexes.index(command_info["id"])
                if command_info["aspect"] == "text":
                    screen_objects[element_index].text = command_info["data"]
                    screen_objects[element_index].redraw()
            elif command_info["request"] == "remove":
                element_index = object_indexes.index(command_info["id"])
                screen_objects.pop(element_index)
                object_indexes.pop(element_index)
            elif command_info["request"] == "clear":
                screen_objects.clear()
                object_indexes.clear()
                scrolling_text.clear()
            elif command_info["request"] == "background":
                day_phase = command_info["time_of_day"]

        for item in screen_objects:
            if item.type == "text_label":
                if item.scrolling_index != -1:
                    item.scroll_text()
                
                for text_box in item.text_boxes:
                    tft.blit(text_box, item.text_boxes[text_box])
                #text_label(property["text"], property["alignment"], property["position"], property["size"], day_phase)
            elif item.type == "label":
                if item.fill:
                    tft.fill(item.fill, pygame.Rect(item.rect))
                if item.image:
                    tft.blit(item.image, item.rectangle)
                #label(property["image"], property["rect"], property["alignment"], property["fill"], property["outline"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                x_value, y_value = pygame.mouse.get_pos()
                notify_touch_sys.put(["pygame_click", x_value, y_value])

        clock.tick(24)
        pygame.display.flip()
        tft.fill(WHITE)

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

def create_element(queue, *elements, button_reg=None):
    for element in elements:
        queue.put({"request": "create", "element": element})
        if element["type"] == "button":
            if not button_reg:
                logging.critical("Unable to create button: '{}' due to the lack of a queue.".format(element["id"]))
                terminate()

            button_reg.put((element["id"], element["properties"]["rect"], element["properties"]["alignment"]))

def update_element(queue, id, aspect, data):
    queue.put({"request": "update", "id": id, "aspect": aspect, "data": data})

def remove_element(queue, id):
    queue.put({"request": "remove", "id": id})

def clear_screen(screen, button):
    screen.put({"request": "clear"})
    button.put("clear")

def background(queue, time_of_day):
    queue.put({"request": "background", "time_of_day": time_of_day})