
import RPi.GPIO as GPIO
from gpiozero import Robot
import time

motor = Robot(left=(5,6), right=(19,26))


GPIO.setmode(GPIO.BCM)
#GPIO.setup(20,GPIO.OUT)
#GPIO.setup(21,GPIO.OUT) 


print ("start")

try:
    while(True):
        
          
        print("forward")
        motor.forward()
        time.sleep(5)
        
        print("backward")
        motor.backward()
        time.sleep(5)
        
           

except KeyboardInterrupt:
    GPIO.cleanup()











"""

import RPi.GPIO as GPIO  
from gpiozero import Motor
import time

motor = Motor(forward=20, backward=21)
interrupt_pin = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(17,GPIO.OUT) #ena enable
GPIO.setup(interrupt_pin,GPIO.IN)
GPIO.output(17,True)  
  
def callback(channel):  
        print ("falling edge detected from pin %d"%channel  )
        print("stop")
        motor.stop()
        
  
GPIO.setmode(GPIO.BCM)  
#GPIO.setup(interrupt_pin, GPIO.IN )  
GPIO.setup(interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP )  
GPIO.add_event_detect( interrupt_pin, GPIO.BOTH, callback=callback, bouncetime=500)  
  
while True:  
    
    print("forward")
    motor.forward()
    #time.sleep(1)
    #motor.forward(speed=0.5)
    # time.sleep(5)
"""    
