import logging

from time import sleep
from sys import exit as terminate
from OrtusTFT import interface, weather

# Not the best idea. I might need to convert this module with functions into a class in the future.
def init(display_q, touch_q, button_q, weather_q, d):
    global display_command, weather_queues, touch_queue, button_queue, demo, NAME

    display_command = display_q
    weather_queues = weather_q
    touch_queue = touch_q
    button_queue = button_q
    demo = d

    if demo:
        NAME = "Test User"
    else:
        NAME = weather.read_local_data("name")

def background_process(current_screen, btn_keys, **kwargs):
    sleepiness = 0

    if current_screen == "Home":
        pass

    while True:
        if not touch_queue.empty():
            touch_info = touch_queue.get()

            if touch_info[2]:
                clean_up()
                if btn_keys.get(touch_info[2]):
                    return btn_keys.get(touch_info[2])
                else:
                    logging.critical("Button '{}' is not bound to a screen.".format(touch_info[2]))
                    terminate()
        else:
            if sleepiness >= 600:
                return "Off {}".format(current_screen)
            else:
                sleepiness += 1
            
        new_data = weather.request_weather_info(weather_queues, "day_phase", wait=True)

        if new_data:
            if current_screen == "Home":
                day_phase = weather.get_day_phase(weather.request_weather_info(weather_queues, "day_phase"))
                interface.background(display_command, day_phase)
                local = home_formatting(day_phase)

                interface.update_element(display_command, "welcome_label", "text", local[0])
                interface.update_element(display_command, "weather_button", "image", "weather_icons/{}.png".format(new_data[local[1]]))
                current_temperature = new_data["temperature"]
            day_phase = weather.get_day_phase(new_data)
            interface.background(display_command, day_phase)
        
        if current_screen == "Home":
            interface.update_element(display_command, "time_temp_label", "text", "{} F°   {}".format(current_temperature, weather.current_time()))
        sleep(0.1)

def clean_up():
    interface.clear_screen(display_command, button_queue)

def home_formatting(day_phase):
    if day_phase == "night":
        return "Good Night,", "weatherCodeNight"
    elif day_phase == "day":
        return "Good Afternoon,", "weatherCodeDay"
    return "Good {},".format(day_phase.capitalize()), "weatherCodeDay"

def home():
    weather_info = weather.request_weather_info(weather_queues, "home")
    day_phase = weather.get_day_phase(weather.request_weather_info(weather_queues, "day_phase"))
    local = home_formatting(day_phase)

    welcome_label = interface.format_text("welcome_label", local[0], "midtop", (120,10), "header")
    name_label = interface.format_text("name", NAME, "midtop", (120,40), "header")
    time_temp_label = interface.format_text("time_temp_label", "", "midtop", (120,280), "subheader")

    weather_button = interface.format_label("weather_button", ((20, 90), interface.WEATHER_ICON), "topleft", image="weather_icons/{}.png".format(weather_info[local[1]]), button=True)
    calendar_button = interface.format_label("calendar_button", ((220, 90), interface.WEATHER_ICON), "topright", image="calendar.png", button=True)
    gallery_button = interface.format_label("gallery_button", ((20, 182), interface.WEATHER_ICON), "topleft", image="blank.png", button=True)
    about_button = interface.format_label("about_button", ((220, 182), interface.WEATHER_ICON), "topright", image="notepad.png", button=True)

    interface.create_element(display_command, welcome_label, name_label, time_temp_label, weather_button, calendar_button, gallery_button, about_button, button_reg=button_queue)
    interface.background(display_command, day_phase)
    current_temperature = weather_info["temperature"]

    btn_keys = {
        "weather_button": "Stats",
        "calendar_button": "Calendar",
        "gallery_button": "Photos",
        "about_button": "About"
    }
    return background_process("Home", btn_keys, {"current_temperature": current_temperature})

def weather_report(page):
    if page == 1:
        weather_info = weather.request_weather_info(weather_queues, "stats")

        back_button = interface.format_label("back_button", ((5, 5), interface.MINI_ICON), "topleft", image="previous.png", button=True)
        time_label = interface.format_text("time_label", "", "midtop", (120, 5), "subheader")
        next_page = interface.format_label("next_page", ((235, 5), interface.MINI_ICON), "topright", image="next.png", button=True)

        interface.create_element(display_command, back_button, time_label, next_page, button_reg=button_queue)

        temp_icon = interface.format_label("temp_icon", ((10, 47), interface.MINI_ICON), "topleft", image="descriptive/thermometer.png")
        temp_label = interface.format_text("temp_label", "Temperature: {} F°".format(weather_info["temperature"]), "topleft", (50, 47), "paragraph")

        wind_icon = interface.format_label("wind_icon", ((10, 89), interface.MINI_ICON), "topleft", image="descriptive/wind.png")
        wind_label = interface.format_text("wind_label", "Wind Speed: {} MPH".format(weather_info["windSpeed"]), "topleft", (50, 89), "paragraph")

        cloud_icon = interface.format_label("cloud_icon", ((10, 131), interface.MINI_ICON), "topleft", image="descriptive/cloud.png")
        cloud_label = interface.format_text("cloud_label", "Cloudiness: {}%".format(weather_info["cloudCover"]), "topleft", (50, 131), "paragraph")

        humidity_icon = interface.format_label("humidity_icon", ((10, 173), interface.MINI_ICON), "topleft", image="descriptive/humidity.png")
        humidity_label = interface.format_text("humidity_label", "Humidity: {}%".format(weather_info["humidity"]), "topleft", (50, 173), "paragraph")

        visibility_icon = interface.format_label("visibility_icon", ((10, 215), interface.MINI_ICON), "topleft", image="descriptive/visibility.png")
        visibility_label = interface.format_text("visibility_label", "Visibility: {} miles".format(weather_info["visibility"]), "topleft", (50, 215), "paragraph")

        moon_icon = interface.format_label("moon_icon", ((10, 257), interface.MINI_ICON), "topleft", image="descriptive/moon.png")
        moon_label = interface.format_text("moon_label", "Moon Phase:", "topleft", (50, 257), "paragraph")
        moon_phase = interface.format_text("moon_phase", weather_info["moonPhase"], "topleft", (50, 282), "paragraph")

        interface.create_element(display_command,
                                    temp_icon, temp_label, wind_icon, wind_label, humidity_icon, 
                                    humidity_label, visibility_icon, visibility_label,
                                    cloud_icon, cloud_label, moon_icon, moon_label,
                                    moon_phase)

        day_phase = weather.get_day_phase(weather.request_weather_info(weather_queues, "day_phase"))
        interface.background(display_command, day_phase)

    elif page == 2:
        weather_info = weather.request_weather_info(weather_queues, "stats 2")

        back_button = interface.format_label("back_button", ((5, 5), interface.MINI_ICON), "topleft", image="previous.png", button=True)
        time_label = interface.format_text("time_label", "", "midtop", (120, 5), "subheader")

        interface.create_element(display_command, back_button, time_label, button_reg=button_queue)

        sunrise_icon = interface.format_label("sunrise_icon", ((10, 47), interface.MINI_ICON), "topleft", image="descriptive/sunrise.png")
        sunrise_label = interface.format_text("sunrise_label", "Sunrise: {}".format(weather_info["sunrise"]), "topleft", (50, 47), "paragraph")

        sunset_icon = interface.format_label("sunset_icon", ((10, 89), interface.MINI_ICON), "topleft", image="descriptive/sunset.png")
        sunset_label = interface.format_text("sunset_label", "Sunset: {}".format(weather_info["sunset"]), "topleft", (50, 89), "paragraph")

        weather_day_icon = interface.format_label("day_icon", ((10, 131), interface.MINI_ICON), "topleft", image="weather_icons/{}.png".format(weather_info["day_weather"]))
        weather_day_label = interface.format_text("day_label", "Daytime Weather:", "topleft", (50, 131), "paragraph")
        weather_day_desc = interface.format_text("day_desc", weather.get_weather_code(str(weather_info["day_weather"] // 10)), "topleft", (50, 156), "paragraph")

        weather_night_icon = interface.format_label("night_icon", ((10, 198), interface.MINI_ICON), "topleft", image="weather_icons/{}.png".format(weather_info["night_weather"]))
        weather_night_label = interface.format_text("night_label", "Nighttime Weather: ", "topleft", (50, 198), "paragraph")
        weather_night_desc = interface.format_text("night_desc", weather.get_weather_code(str(weather_info["night_weather"] // 10)), "topleft", (50, 223), "paragraph")

        ice_snow_icon = interface.format_label("ice_snow_icon", ((10, 265), interface.MINI_ICON), "topleft", image="descriptive/snowflake.png")
        ice_label = interface.format_text("ice_label", "Ice: {}%".format(weather_info["ice"]), "topleft", (50, 265), "paragraph")
        snow_label = interface.format_text("snow_label", "Snow: {}%".format(weather_info["snow"]), "topleft", (50, 290), "paragraph")

        interface.create_element(display_command, 
                                    sunrise_icon, sunrise_label, sunset_icon, sunset_label,
                                    weather_day_icon, weather_day_label, weather_night_icon,
                                    weather_day_desc, weather_night_label, weather_night_desc,
                                    ice_snow_icon, ice_label, snow_label)
    else:
        logging.critical("An unknown page number was requested.")
        terminate()

def about():
    back_button = interface.format_label("back_button", ((5, 5), interface.MINI_ICON), "topleft", image="previous.png", button=True)
    interface.create_element(display_command, back_button, button_reg=button_queue)

    title = interface.format_text("title", "OrtusTFT", "midtop", (120,40), "header")
    author = interface.format_text("author", "Developed by:", "midtop", (120,80), "subheader")
    name = interface.format_text("name", "lumen-novum", "midtop", (120,105), "subheader")

    qr_code = interface.format_label("qr_code", ((120, 140), (100, 100)), "midtop", image="qr.png")
    side_note = interface.format_text("side_note", "(Github page)", "midtop", (120,240), "paragraph")

    version = interface.format_text("version", "V0.1.0", "midtop", (120,290), "paragraph")
    
    interface.create_element(display_command, title, author, name, qr_code, side_note, version)

    day_phase = weather.get_day_phase(weather.request_weather_info(weather_queues, "day_phase"))
    interface.background(display_command, day_phase)

def sleep_screen():
    interface.create_element(display_command, interface.format_label("power", ((0, 0), (240, 320)), "topleft", fill=interface.BLACK, button=True), button_reg=button_queue)
    if not demo:
        with open("/sys/class/backlight/soc:backlight/brightness", "w") as backlight:
            backlight.write("0")

def wip():
    def cone_row(height):
        for cone_num in range(7):
            cone_pos = (cone_num * 32) + 8
            interface.create_element(display_command, interface.format_label(str(cone_num) + str(height), ((cone_pos, height), interface.MINI_ICON), "topleft", image="cone.png"))

    back_button = interface.format_label("back_button", ((5, 5), interface.MINI_ICON), "topleft", image="previous.png", button=True)
    interface.create_element(display_command, back_button, button_reg=button_queue)

    day_phase = weather.get_day_phase(weather.request_weather_info(weather_queues, "day_phase"))
    interface.background(display_command, day_phase)

    # TODO: Eliminate the need to specifiy "\n" to go to the next line.
    title = interface.format_text("title", "WIP", "midtop", (120,90), "header")
    desc1 = interface.format_text("desc1", "This feature hasn't\nbeen implemented\nyet.", "midtop", (120,130), "subheader")

    interface.create_element(display_command, title, desc1)

    cone_row(48)        
    cone_row(222)