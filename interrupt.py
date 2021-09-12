import RPi.GPIO as GPIO  
from gpiozero import Robot
import time
import Adafruit_DHT


DHT_PIN = 17
CloseLimit = 2 
OpenLimit = 27 
Relay_3 = 23
Relay_4 = 24
Rain_pin = 25
motor1 = 5
motor2 = 6
motor3 = 19
motor4 = 26



GPIO.setmode(GPIO.BCM)

#GPIO.setup(CloseLimit,GPIO.IN)
#GPIO.setup(OpenLimit,GPIO.IN)
GPIO.setup(Rain_pin,GPIO.IN)
GPIO.setup(Relay_3,GPIO.OUT)
GPIO.setup(Relay_4,GPIO.OUT)
GPIO.setup(motor1,GPIO.OUT)
GPIO.setup(motor2,GPIO.OUT) 
GPIO.setup(CloseLimit, GPIO.IN, pull_up_down=GPIO.PUD_UP )  
GPIO.setwarnings(False)

 
motor = Robot(left=(motor1,motor2), right=(motor3,motor4))  


DHT_SENSOR = Adafruit_DHT.DHT22


def stop_motor(channel):  
    print("close motor stop")
    motor.stop()
    return
  
GPIO.add_event_detect( CloseLimit, GPIO.FALLING,  
        callback=stop_motor, bouncetime=300)  
  
while True:  
    print("motor forward 시계반대방향") #시계반대방향
    motor.forward()
    #time.sleep(1)
