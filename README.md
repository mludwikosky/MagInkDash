
Forked from: https://github.com/speedyg0nz/MagInkDash
Also combined with: https://github.com/speedyg0nz/MagInkCal

# MagInkDash
This repo contains the code needed to drive an E-Ink Magic Dashboard that uses a Raspberry Pi to automatically retrieve updated content from Google Calendar, and OpenWeatherMap, format them into the desired layout, before displaying it to an E-Ink display (Waveshare 12.48). Note that the code has only been tested on the specific hardware mentioned, but can be easily modified to work with other hardware.

## Background

This project is a mashup of speedyg0nz's two E-Ink displays. I initally copied his approach and made the MagInkCal. I made some modifications to that to make it more readable. Mainly removing the month digit at the top, and rotating the content landscape. His original design was following the original [Android Magic Calendar concept](https://www.youtube.com/watch?v=2KDkFgOHZ5I), but that didn't work as well with English. Changing it to landscape allowed longer text per day, but there was still a lot left out. I saw that he had moved to the MagInkDash concept and I wanted to combine the two. My version works using the original Waveshare 12.48" Tri-color E-Ink Display (although I'm only using black and white at the moment). It also runs locally on a PiSugar 3 powered Raspberry Pi W. I removed the OpenAI integration because the random facts and information didn't appeal to me. I would rather use that space on the screen for more calendar events.

There definitely is some more work to be done on this project. There are some compromises with the current setup that make it less than ideal. For starters, using the Raspberry Pi W and the PiSugar, it can only update once a day when the PiSugar boots the Pi up. The main drawback for this is the current weather is only accurate at 6am, which I have it set to boot up. After that, it's stale information and actually distracts from the usefulness of the display. I'm planning on rebuilding the weather side of it to be more useful with a once-a-day refresh cycle.

## Hardware Required
- [Raspberry Pi Zero WH](https://www.raspberrypi.com/news/zero-wh/) - Header pins are needed to connect to the E-Ink display
- [Waveshare 12.48" Tri-color E-Ink Display](https://www.waveshare.com/product/12.48inch-e-paper-module-b.htm)) - Used to display the generated dashboard.
- [Pisugar3](https://www.tindie.com/products/pisugar/pisugar3-battery-for-raspberry-pi-zero/)[Amazon](https://www.amazon.com/dp/B09MJ8SCGD) - Provides the RTC and battery. 


## How It Works
Through PiSugar3's web interface, the onboard RTC can be set to wake and trigger the RPi to boot up daily at a time of your preference. Upon boot, a cronjob on the RPi is triggered to run a Python script that fetches the current weather from OpenWeatherMap and calendar events from Google Calendar for the next 7 days. Then it formats them into the desired layout before displaying it on the E-Ink display. The RPi then shuts down to conserve battery. The calendar remains displayed on the E-Ink screen, because well, E-Ink...

Some features of the dashboard: 
- **Battery Life**: As with similar battery powered devices, the biggest question is the battery life. I'm currently using a 1500mAh battery on the Inkplate 10 and based on current usage, it should last me around 3-4 months. With the 3000mAh that comes with the manufacturer assembled Inkplate 10, we could potentially be looking at 6-8 month battery life. With this crazy battery life, there are much more options available. Perhaps solar power for unlimited battery life? Or reducing the refresh interval to 15 or 30min to increase the information timeliness?
- **Calendar and Weather**: I'm currently displaying calendar events and weather forecast for current day and the upcoming two days. No real reason other than the desire to know what my weekend looks like on a Friday, and therefore helping me to better plan my weekend. Unfortunately, if you have a busy calendar with numerous events on a single day, the space on the dashboard will be consumed very quickly. If so, you might wish to modify the code to reduce/limit the number of days/events to be displayed.

![MagInkDash Features](https://user-images.githubusercontent.com/5581989/231484018-6ff6a883-3226-42c7-a387-fcef7ee9d49c.png)

## Setting Up 

1. Start by flashing [Raspberrypi OS Lite](https://www.raspberrypi.org/software/operating-systems/) to a SD/MicroSD Card. If you're using a Raspberry Pi with 32bit CPU, there are [known issues](https://forums.raspberrypi.com/viewtopic.php?t=323478) between the latest RPiOS "bullseye" release and chromium-browser, which is required to run this code. As such, I would recommend that you keep to the legacy "buster" OS if you're still running this on older RPi hardware.

2. After setting up the OS, run the following commmand in the RPi Terminal, and use the [raspi-config](https://www.raspberrypi.org/documentation/computers/configuration.html) interface to setup Wifi connection, and set the timezone to your location. You can skip this if the image is already preconfigured using the Raspberry Pi Imager.

```bash
sudo raspi-config
```
3. Run the following commands in the RPi Terminal to setup the environment to run the Python scripts and function as a web server. It'll take some time so be patient here.

```bash
sudo apt update
sudo apt-get install python3-pip
sudo apt-get install chromium-chromedriver
sudo apt-get install libopenjp2-7-dev
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip3 install pytz
pip3 install selenium
pip3 install Pillow
```
4. Download the over the files in this repo to a folder in your PC first. 

5. In order for you to access your Google Calendar events, it's necessary to first grant the access. Follow the [instructions here](https://developers.google.com/calendar/api/quickstart/python) on your PC to get the credentials.json file from your Google API. Don't worry, take your time. I'll be waiting here.

6. Once done, copy the credentials.json file to the "gcal" folder in this project. Navigate to the "gcal" folder and run the following command on your PC. A web browser should appear, asking you to grant access to your calendar. Once done, you should see a "token.pickle" file in your "gcal" folder.

```bash
python3 quickstart.py
```

7. Copy all the files (other than the "inkplate" folder) over to your RPi using your preferred means. 

8. Run the following command in the RPi Terminal to open crontab.
```bash
crontab -e
```
9. Specifically, add the following command to crontab so that the MagInkDash Python script runs on the hour, every hour.
```bash
0 * * * * cd /location/to/your/MagInkDash && python3 main.py
```
10. As for the Inkplate, I'm not going to devote too much space here since there are [official resources that describe how to set it up](https://inkplate.readthedocs.io/en/latest/get-started.html). It may take some trial and error for those new to microcontroller programming but it's all worth it! Only the Arduino portion of the guide is relevant, and you'll need to be able to run *.ino scripts via Arduino IDE before proceeding. From there, run the "inkplate.ino" file from the "inkplate" folder from the Arduino IDE when connected to the Inkplate.

12. That's all! Your Magic Dashboard should now be refreshed every hour! 

![20230412_214652](https://user-images.githubusercontent.com/5581989/231485348-35d7e0df-034e-49aa-8500-223b2b3bdcc0.JPG)
![20230412_215020](https://user-images.githubusercontent.com/5581989/231484068-aa6ce877-1e0a-49fe-b47e-7c024752f42c.JPG)
Selfie and family portrait together with the MagInkCal

## Acknowledgements
- [Lexend Font](https://fonts.google.com/specimen/Lexend) and [Tilt Warp Font](https://fonts.google.com/specimen/Tilt+Warp): Fonts used for the dashboard display
- [Bootstrap](https://getbootstrap.com/): Styling toolkit to customise the look of the dashboard
- [Weather Icons](https://erikflowers.github.io/weather-icons/): Icons used for displaying of weather forecast information
- [Freepik](https://www.freepik.com/): For the background image used in this dashboard
  
## Contributing
I won't be updating this code much, since it serves my needs well. Nevertheless, feel free to fork the repo and modify it for your own purpose. At the same time, check out other similar projects, such as [InkyCal](https://github.com/aceisace/Inkycal) by [/u/aceisace](https://www.reddit.com/user/aceisace/). It's much more polished and also actively developed.

## Buy Me A Coffee
If this project has helped you in any way, do buy me a coffee so I can continue to build more of such projects in the future and share them with the community!

<a href="https://www.buymeacoffee.com/speedygonz" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>


## What's Next
Since building the Magic Calendar two years back, I've been looking at E-Ink tablets that emulate the experience of writing on paper, and allow the users to take notes on the go. Those familiar with this range of products would be aware of the Kindle Scribe, reMarkable tablet, Ratta Supernote, Kobo Elipsa and many others. I've had some limited success with getting a Kindle Paperwhite to display a calendar while sleeping but it felt too "hacky" and prone to breaking when Amazon updates the OS. I'm still looking for the right device (possibly a PineNote?), so if you're aware of any suitable candidates, do let me know!
