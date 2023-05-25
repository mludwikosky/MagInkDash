"""
This project is designed for the Inkplate 10 display. However, since the server code is only generating an image, it can
be easily adapted to other display sizes and resolution by adjusting the config settings, HTML template and
CSS stylesheet. This code is heavily adapted from my other project (MagInkCal) so do take a look at it if you're keen.
As a dashboard, there are many other things that could be displayed, and it can be done as long as you are able to
retrieve the information. So feel free to change up the code and amend it to your needs.
"""

import datetime
import logging
import sys
import json
from datetime import datetime as dt
from pytz import timezone
from gcal.gcal import GcalModule
from owm.owm import OWMModule
from power.power import PowerHelper
from render.render import RenderHelper


if __name__ == '__main__':
    logger = logging.getLogger('maginkdash')

    # Basic configuration settings (user replaceable)
    configFile = open('config.json')
    config = json.load(configFile)

    calendars = config['calendars'] # Google Calendar IDs
    displayTZ = timezone(config['displayTZ']) # list of timezones - print(pytz.all_timezones)
    numCalDaysToShow = config['numCalDaysToShow'] # Number of days to retrieve from gcal, keep to 3 unless other parts of the code are changed too
    isDisplayToScreen = config['isDisplayToScreen']  # set to true when debugging rendering without displaying to screen
    isShutdownOnComplete = config['isShutdownOnComplete']  # set to true to conserve power, false if in debugging mode
    screenWidth = config['screenWidth']  # Width of E-Ink display. Default is landscape. Need to rotate image to fit.
    screenHeight = config['screenHeight']  # Height of E-Ink display. Default is landscape. Need to rotate image to fit.
    imageWidth = config['imageWidth']  # Width of image to be generated for display.
    imageHeight = config['imageHeight']  # Height of image to be generated for display.
    rotateAngle = config['rotateAngle']  # If image is rendered in portrait orientation, angle to rotate to fit screen
    lat = config["lat"] # Latitude in decimal of the location to retrieve weather forecast for
    lon = config["lon"] # Longitude in decimal of the location to retrieve weather forecast for
    owm_api_key = config["owm_api_key"]  # OpenWeatherMap API key. Required to retrieve weather forecast.
    batteryDisplayMode = config['batteryDisplayMode'] # 0: do not show / 1: always show / 2: show when battery is low

    # Create and configure logger
    logging.basicConfig(filename="logfile.log", format='%(asctime)s %(levelname)s - %(message)s', filemode='a')
    logger = logging.getLogger('maginkdash')
    logger.addHandler(logging.StreamHandler(sys.stdout))  # print logger to stdout
    logger.setLevel(logging.INFO)
    logger.info("Starting dashboard update")

    # Get Battery Level
    powerService = PowerHelper()
    powerService.sync_time()
    currBatteryLevel = powerService.get_battery()
    logger.info('Battery level at start: {:.3f}'.format(currBatteryLevel))

    # Retrieve Weather Data
    owmModule = OWMModule()
    current_weather, hourly_forecast, daily_forecast = owmModule.get_weather(lat, lon, owm_api_key)

    # Retrieve Calendar Data
    currDate = dt.now(displayTZ).date()
    currDatetime = dt.now(displayTZ).hour
    calStartDatetime = displayTZ.localize(dt.combine(currDate, dt.min.time()))
    calEndDatetime = displayTZ.localize(dt.combine(currDate + datetime.timedelta(days=numCalDaysToShow-1), dt.max.time()))
    calModule = GcalModule()
    eventList = calModule.get_events(
        currDate, calendars, calStartDatetime, calEndDatetime, displayTZ, numCalDaysToShow)

    # Render Dashboard Image
    renderService = RenderHelper(imageWidth, imageHeight, rotateAngle)
    # renderService.process_inputs(currDate, current_weather, hourly_forecast, daily_forecast, eventList, numCalDaysToShow, topic, path_to_server_image)
    calBlackImage, calRedImage = renderService.process_inputs(currDate, current_weather, hourly_forecast, daily_forecast, eventList, numCalDaysToShow, currBatteryLevel, batteryDisplayMode)

    if isDisplayToScreen:
        from display.display import DisplayHelper
        displayService = DisplayHelper(screenWidth, screenHeight)
        if currDate.weekday() == 6: # If date is Sunday, calibrate display
            # calibrate display once a week to prevent ghosting
            displayService.calibrate(cycles=0)  # to calibrate in production
        displayService.update(calBlackImage, calRedImage)
        displayService.sleep()

    logger.info("Completed dashboard update")

    currBatteryLevel = powerService.get_battery()
    logger.info('Battery level at end: {:.3f}'.format(currBatteryLevel))

    logger.info("Checking if configured to shutdown safely - Current hour: {}".format(currDatetime))
    if isShutdownOnComplete:
        # implementing a failsafe so that we don't shutdown when debugging
        # checking if it's 6am in the morning, which is the time I've set PiSugar to wake and refresh the calendar
        # if it is 6am, shutdown the RPi. if not 6am, assume I'm debugging the code, so do not shutdown
        if currDatetime == 6:
            logger.info("Shutting down safely.")
            import os
            os.system("sudo shutdown -h now")