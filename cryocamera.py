# //////////////////////////////////////////////// //
#                                                  //
# python script to read the PT100 temperature      //
# sensor on the chip of the cryocamera.            //
# This script allows for setting a lower and an    //
# upper temperature, which will be set using a     //
# resistor chain within the camera case.           //
#                                                  //
# NOTE: NEVER USE THE CAMERA AT ROOM TEMPERATURE   //
# BUT ONLY AT CRYOGENIC TEMPERATURES.              //
#                                                  //
# Last modifications: 21.01.2019 by R.Berner       //
#                                                  //
# //////////////////////////////////////////////// //


#!/usr/bin/python
import math
import os
import time

if __name__ == "__main__":

	import max31865

	cs0Pin  = 5
	misoPin = 9
	mosiPin = 10
	clkPin  = 11
        heatPin = 26

	sens = max31865.max31865_heater(cs0Pin,misoPin,mosiPin,clkPin,heatPin,0)

        tempC = sens.readTemp()

        # Define the temperature range to operate the camera
        upper_temp = -5.
        lower_temp = -6.
        print "Lower temp: %.2f C" % lower_temp
        print "Upper temp: %.2f C" % upper_temp

        # Define temperatures at which motion is started (will introduce additional heat into the camera case)
        # and at which it must be stopped in order to prevent the camera to overheat.
        temp_motion_start = -70.
        temp_motion_stop  =  35.

        # First few temp. measurements could be incorrect
        for i in range (0,10):
            sens.readTemp()
            time.sleep(0.2)

        # Heating up case with resistors only
        tempC = sens.readTemp()
        while tempC < temp_motion_start:
            tempC = sens.readTemp()
            print "Heating up camera."
            print "Will start motion at %.2f degrees" % temp_motion_start
            print "Current temperature: %.2f" % tempC
            sens.heatOn()
            time.sleep(1)

        # Start motion and stream to port 8081 (defined in /etc/motion/motion.conf)
        tempC = sens.readTemp()
        if tempC > temp_motion_start:
            os.system("sudo motion start")
            print "Started motion"

        heating = 1

        while 1:
            time.sleep(1.)
            tempC = sens.readTemp()

            if tempC < lower_temp:
                sens.heatOn()
                print "Heating ON"
                print "Current temperature: %.2f" % tempC
                heating = 1

            elif tempC > upper_temp:
                sens.heatOff()
                print "Heating OFF"
                print "Current temperature: %.2f" % tempC
                heating = 0

            else:
                if heating == 0: print "Heating OFF"
                if heating == 1: print "Heating ON"
                print "Current temperature: %.2f" % tempC

            # To prevent overheating
            # TO DO: The command to stop motion does not yet work
            while tempC > temp_motion_stop:
                print "CAMERA IS TOO HOT!"
                print "Current temperature: %.2f" % tempC
                print "Stop motion"
                os.system("sudo service motion stop")
                #os.system("sudo motion stop")
                #os.system("sudo systemctl motion stop")
                #os.system("sudo reboot now")
                sens.heatOff()
                heating = 0
                tempC = sens.readTemp()
                print "Heating and motion OFF"
                print "Current temperature: %.2f" % tempC
                time.sleep(1.)
                if tempC < temp_motion_stop:
                    os.system("sudo motion start")
                    print "Started motion"
                    break

	GPIO.cleanup()