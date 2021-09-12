import RPi.GPIO as GPIO  
from gpiozero import Robot
import time
import Adafruit_DHT


DHT_PIN = 4
CloseLimit = 22 
OpenLimit = 27 
Relay_3 = 23
Relay_4 = 24
Rain_pin = 25
motor1 = 5
motor2 = 6
motor3 = 19
motor4 = 26
speed = 0.7
open_stete = ''
close_stete = ''

GPIO.setmode(GPIO.BCM)

GPIO.setup(CloseLimit,GPIO.IN)
GPIO.setup(OpenLimit,GPIO.IN)
GPIO.setup(Rain_pin,GPIO.IN)
GPIO.setup(Relay_3,GPIO.OUT)
GPIO.setup(Relay_4,GPIO.OUT)
GPIO.setup(motor1,GPIO.OUT)
GPIO.setup(motor2,GPIO.OUT) 
GPIO.setup(Rain_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP )  
GPIO.setwarnings(False)

 
motor = Robot(left=(motor1,motor2), right=(motor3,motor4))  


DHT_SENSOR = Adafruit_DHT.DHT22

def rain_int(channel):  
    #door_oc("close")  
    print("rainnig")
    return
  
GPIO.add_event_detect( Rain_pin, GPIO.FALLING,  
        callback=rain_int, bouncetime=300)  
  


def door_oc(state):
    
    if state == "close" :
        
        while GPIO.input(CloseLimit) == 0 :
            print("motor 시계반대방향") #시계반대방향
            print(GPIO.input(CloseLimit))
            motor.forward(speed=speed)
        
        print("close motor stop")
        print(GPIO.input(CloseLimit))
        motor.stop()
        motor.backward(speed=speed) #살짝 뒤로옴
        motor.stop()    
    
    
    if state == "open" :

        while GPIO.input(OpenLimit) == 0 :
            print("motor backward 열림") 
            print(GPIO.input(OpenLimit))
            motor.backward(speed=speed)
        
        print("open motor stop")
        print(GPIO.input(OpenLimit))
        motor.stop()
        motor.forward(speed=speed) #살짝 뒤로옴
        motor.stop()
            

def door_moc(state, distence): # 수동 문 여닫이
    global global_one
    i=1
    print(state, distence)
    if state == "open" :
        while i <= distence:
            motor.backward()    
            i+=1
            global_one = i
        print(global_one)
        return global_one    
            
            
    if state == "close" :
        while i <= distence:
            #motor.forward()    
            i+=1
            
            
    
    
    

auto_temp = 33.6

global_one = 0

while True:
    
    Humi, Temp = Adafruit_DHT.read_retry(DHT_SENSOR,DHT_PIN)
    
    if Temp is not None:
        _temp = '{:0.1f}'.format(float(Temp))
        Temp = float(_temp)
    else: 
        Temp = 0
                
    if Humi is not None:
        Humi = '{:0.1f}'.format(float(Humi))
    else: 
        Humi = 0 

    print(Temp, Humi)

    """
    if Temp < (auto_temp - 0.2) :  # 
        
        GPIO.output(Relay_4, True)
        door_oc("open")
     
    if Temp >= auto_temp  :           # 문닫히고 환풍기 켜짐
        
        door_oc("close")
        GPIO.output(Relay_4, False)
    """    
    
    if global_one == 0:
        door_moc("open", 100) 
        print(global_one)
    
    
    
    