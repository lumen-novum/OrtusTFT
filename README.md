# !!!!!!!!!!!!!!!!!!!!! DO NOT MAKE PUBLIC!!! !!!!!!!!!!!!!!!!!!!!!

# OrtusTFT
A simple, digital, forecast that uses the Adafruit 320x240 TFT hat for the Raspberry Pi.

## Features
* Home screen with temperature, time, and a preview icon of the current weather
* Statistic screen with a more in depth view of the weather such as:
  * Temperature
  * Wind Speed
  *	Cloudiness
  *	Humidity
  *	Visibility
  *	Moon Phase
  *	Sunrise/Sunset Time
  *	Day/Night Weather
  *	Chance of Ice/Snow
* About me page with some basic info

## Prerequisites
* Raspberry Pi - I'm not 100% sure if anything newer than a 3B will work. If it does/doesn't work, please leave a "documentation" issue to let me know.
* At the moment, OrtusTFT only supports Adafruit's 320x240 Resistive displays. (Size does not matter) If you try to use anything else, OrtusTFT will not function properly.
If you would like support for your screen, please create an "enhancement" issue.
* The following python packages:
  * Evdev
  * Pygame 1.9.6 ```sudo pip3 install pygame==1.9.6```
* [Tomorrow.io](https://app.tomorrow.io/signin) account - Once you have made an account and are logged in, [click here](https://app.tomorrow.io/development/keys) to get your secret key to use for later.
* Location coordinates - Go to Google Maps and right click on the place you would like to have the weather from and click on the coordinates. Write these down for later.

## Installation
1. Download and install the following [Raspberry Pi OS image.](https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/)
2. Once you have it up and running, execute the following bash commands: (Provided by Adafruit)
  ```
  cd ~
  sudo apt-get update
  sudo apt-get install -y git python3-pip
  sudo pip3 install --upgrade adafruit-python-shell click
  git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
  cd Raspberry-Pi-Installer-Scripts
  ```
3. Run the interactive TFT installation script:
  ```
  sudo python3 adafruit-pitft.py
  ```
  
When using the interactive installation script:
* Make sure the rotation for the display is either 0 or 180 degrees. (90 and 270 won't work)
* For the questions:
  > Would you like the console to appear on the PiTFT display?

  and

  > Would you like the HDMI display to mirror to the PiTFT display?

  ### Type no.
  
  If you accidentally type yes, then simply abort the installation and run the script again.
  
  [If you need any further help, please take a look at this tutorial where I learned how to setup my TFT before creating an issue.](https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/easy-install-2)
  
Reboot the Pi when finished.
  
4. Download OrtusTFT with the following commands:
```
cd ~
git clone https://github.com/lumen-novum/OrtusTFT.git
cd OrtusTFT
```

## First Time Setup
It was very difficult to get the TFT working so I had to create a few workarounds. Please run the following command to begin:
```
sudo python3 configure.py
```

For some technical reasons, root access is required in order to control the TFT. (You are always welcome to read through the source code. The script is only about 200 or so lines)

After you run the command, type 'r' to begin the setup process.

If you have a stylus, it may make the display calibration more accurate, but it's not required.

## Usage
To use OrtusTFT, simply run the following command in the root of the project:
```
sudo python3 main.py
```

Once again, root access is required in order to control the TFT. (You are always welcome to read through the source code. The project is currently about 750 or so lines)

If you would like it to automatically start up everytime the Raspberry Pi turns on, just add the following line to *~/.bashrc*:
```
sudo python3 ~/OrtusTFT/main.py
```

Whenever you exit the program, there will be errors that appear. These errors can be safely ignored and will most likely be fixed in a future update.

## Future Plans
Here are some of the improvements I'll be working on:
* Cleaning up code
* Making code more PEP8 compliant
* A proper clean up system
* A calendar that tracks weather data within a time range, events, and due dates
* A todo list
* A debugging system that can provide helpful information
  (The one I have right now only tracks basic warnings, critical messages, and python errors).
* A simulator for people to try out OrtusTFT without the need of a Raspberry Pi or the display.

## Feedback
If you would like to contribute in some way whether it be through a bug report, pull request, or something else feel free to do so. 

### Bug Types
If it is a Python error (syntax/runtime) please copy and paste the error message.

If it is a [CRITICAL] error, these are defined by me. Please copy and paste the error message.

If it is a logic error (something isn't working correctly but there isn't an error message) please just describe the problem.

### Before Sending a Bug Report
Please make sure you have followed the installation instructions **EXACTLY** the way they are.

This is to ensure that you really have an issue caused from OrtusTFT, not your system configuration.

If you need help setting up OrtusTFT, please create an issue with the "help wanted" flair instead.

Also, if you have modified the code/json at all, **please do not submit a bug report**.

If you have, you are welcome to create a "help wanted" issue with a link to your forked repository, but there is no guarantee you will recieve assistance.
(If you are uploading a json file, make sure you redact personal information such as name, api key, and location). 

### Submitting a Bug Report
When submitting a bug report, please copy, paste, and answer the following questions:
```
Which Raspberry Pi are you using?

Which TFT display are you using?

Did you follow the installation instructions step-by-step?

Did you modify any part of the code or the .json files?

What is your issue?

Is there an error message? If so, paste it here:

Is there anything else I should know about?
```

I appreciate any and all contributions. :)

## Credits
Suggestion of a simulator: [KylesDev](https://github.com/kylesdev91)

Weather code icons: [Tomorrow.io](https://github.com/Tomorrow-IO-API/tomorrow-weather-codes)

All other icons are from [Flaticon](http://www.flaticon.com/) from the following creators:
* [Good Ware](https://www.flaticon.com/authors/good-ware)
* [Pixel perfect](https://www.flaticon.com/authors/pixel-perfect)
* [Freepix](https://www.flaticon.com/authors/freepik)
* [kmg design](https://www.flaticon.com/authors/kmg-design)
* [kosonicon](https://www.flaticon.com/authors/kosonicon)
* [Sergei Kokota](https://www.flaticon.com/authors/sergei-kokota)
* [Roundicons](https://www.flaticon.com/authors/roundicons)
* [Uniconlabs](https://www.flaticon.com/authors/uniconlabs)
