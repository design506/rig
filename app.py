from flask import Flask, request, session, redirect, url_for, jsonify, render_template, Response, json
from picamera import PiCamera, Color
from camera import Camera                          #https://neosarchizo.gitbooks.io/raspberrypiforsejonguniv/content/chapter5.html 문서에 camera.py download
import queue 		# for serial command queue
import threading 	# for multiple threads
import os
import pygame		# for sound
import serial 		# for Arduino serial access
import serial.tools.list_ports
import subprocess 	# for shell commands
import RPi.GPIO as GPIO  
from gpiozero import Robot
import time
import Adafruit_DHT
import datetime
  
  
DHT_SENSOR = Adafruit_DHT.DHT22
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
motor.stop()

GPIO.output(Relay_3, True) #relay off
GPIO.output(Relay_4, True) #relay off

def rain_int(channel):  
    door_oc("close")  
    print("rainnig")
    return redirect(url_for('index'))
  
GPIO.add_event_detect( Rain_pin, GPIO.FALLING,  
        callback=rain_int, bouncetime=300)  






app = Flask(__name__)


##### VARIABLES WHICH YOU CAN MODIFY #####
loginPassword = "pi"                                  # Password for web-interface
arduinoPort = "ARDUINO"                                              # Default port which will be selected
streamScript = "/home/pi/mjpg-streamer.sh"                           # Location of script used to start/stop video stream
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)      # Secret key used for login session cookies
##########################################




# Set up runtime variables and queues
exitFlag = 0
arduinoActive = 0
streaming = 0
volume = 5
batteryLevel = -999
queueLock = threading.Lock()
workQueue = queue.Queue()
threads = []

relay_4_state = 1
global_one = 0


@app.route('/')
def index():
	if session.get('active') != True:
		return redirect(url_for('login'))

	global relay_4_state
	
	# Get list of connected USB devices
	ports = serial.tools.list_ports.comports()
	usb_ports = [
		p.description
		for p in serial.tools.list_ports.comports()
		#if 'ttyACM0' in p.description
	]
	
	# Ensure that the preferred Arduino port is selected by default
	selectedPort = 0
	for index, item in enumerate(usb_ports):
		if arduinoPort in item:
			selectedPort = index
	
	return render_template('index.html', relay_4_state=relay_4_state, portSelect=selectedPort,connected=arduinoActive)




@app.route('/Temp_Humi')
def temp_humi():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    global DHT_SENSOR
    global DHT_PIN
    global auto_temp
    
    Humi, Temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    if Temp is not None:
        _temp = '{:0.1f}'.format(float(Temp))
        Temp = float(_temp)
    else: 
        Temp = 0
                
    if Humi is not None:
        Humi = '{:0.1f}'.format(float(Humi))
    else: 
        Humi = 0 
  
    """
    if float(Temp) < (auto_temp) :   
        GPIO.output(17, True)
        relay_states[17] = 1   
        #door_state = 0  #도어 열림
        
    if float(Temp) >= auto_temp:   # 환풍기 온 문닫음       
        GPIO.output(17, False)  
        relay_states[17] = 0 
        #door_state = 1  #도어 닫음
    """ 
   
    _data = (str(Temp) + "," + str(Humi) + "," + str(timeString))
    return _data


@app.route('/on_off/<int:state>')
def _on_off(state):
    if state==1:
        GPIO.output(Relay_4, True)
        relay_4_state = 1    # 변수를 전달하기위함
        
    if state==0:
        GPIO.output(Relay_4, False)  # 환풍기켜짐 
        relay_4_state = 0    # 변수를 전달하기위함
    
    return redirect(url_for('index'))


@app.route('/door_op_cl/<state>')
def door_oc(state):
    if state == "close" :  #close
        print("door_op_cl"+str(state))
        while GPIO.input(CloseLimit) == 0 :
            print("motor 시계반대방향") #시계반대방향
            print(GPIO.input(CloseLimit))
            motor.forward(speed=speed)
 
        print("close motor stop")
        print(GPIO.input(CloseLimit))
        motor.stop()
        motor.backward(speed=speed) #살짝 뒤로옴
        motor.stop()    
   
    if state == "open" :   #open
        while GPIO.input(OpenLimit) == 0 :
            print("motor backward 열림") 
            print(GPIO.input(OpenLimit))
            motor.backward(speed=speed)
        
        print("open motor stop")
        print(GPIO.input(OpenLimit))
        motor.stop()
        motor.forward(speed=speed) #살짝 뒤로옴
        motor.stop()
   
    return redirect(url_for('index'))

@app.route('/door_menu_oc/<int:distence>')
def door_moc(distence): # 수동 문 여닫이
    global global_one
    i=1
    
    while i <= distence:
        motor.forward()    
        i+=1
        global_one = i
        
    motor.stop()
    #print(global_one)
    return redirect(url_for('index')) 
            


def gen(camera):
   while True:
       frame = camera.get_frame()
       yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
   return Response(gen(Camera()),
                   mimetype='multipart/x-mixed-replace; boundary=frame')




@app.route('/login')
def login():
	if session.get('active') == True:
		return redirect(url_for('index'))
	else:
		return render_template('login.html')

##
# Check if the login password is correct
#
@app.route('/login_request', methods = ['POST'])
def login_request():
	password = request.form.get('password')
	if password == loginPassword:

		session['active'] = True
		return redirect(url_for('index'))
	return redirect(url_for('login'))


##
# Update Settings
#
@app.route('/settings', methods=['POST'])
def settings():
	if session.get('active') != True:
		return redirect(url_for('login'))

	thing = request.form.get('type');
	value = request.form.get('value');

	if thing is not None and value is not None:
		# Motor deadzone threshold
		if thing == "motorOff":
			print("Motor Offset:", value)
			if test_arduino() == 1:
				queueLock.acquire()
				workQueue.put("O" + value)
				queueLock.release()
			else:
				return jsonify({'status': 'Error','msg':'Arduino not connected'})

		# Motor steering offset/trim
		elif thing == "steerOff":
			print("Steering Offset:", value)
			if test_arduino() == 1:
				queueLock.acquire()
				workQueue.put("S" + value)
				queueLock.release()
			else:
				return jsonify({'status': 'Error','msg':'Arduino not connected'})

		# Automatic/manual animation mode
		elif thing == "animeMode":
			print("Animation Mode:", value)
			if test_arduino() == 1:
				queueLock.acquire()
				workQueue.put("M" + value)
				queueLock.release()
			else:
				return jsonify({'status': 'Error','msg':'Arduino not connected'})

		# Sound mode currently doesn't do anything
		elif thing == "soundMode":
			print("Sound Mode:", value)

		# Change the sound effects volume
		elif thing == "volume":
			global volume
			volume = int(value)
			print("Change Volume:", value)

		# Turn on/off the webcam
		elif thing == "streamer":
			print("Turning on/off MJPG Streamer:", value)
			if onoff_streamer() == 1:
				return jsonify({'status': 'Error', 'msg': 'Unable to start the stream'})

			if streaming == 1:
				return jsonify({'status': 'OK','streamer': 'Active'})
			else:
				return jsonify({'status': 'OK','streamer': 'Offline'})

		# Shut down the Raspberry Pi
		elif thing == "shutdown":
			print("Shutting down Raspberry Pi!", value)
			result = subprocess.run(['sudo','nohup','shutdown','-h','now'], stdout=subprocess.PIPE).stdout.decode('utf-8')
			return jsonify({'status': 'OK','msg': 'Raspberry Pi is shutting down'})

		# Unknown command
		else:
			return jsonify({'status': 'Error','msg': 'Unable to read POST data'})

		return jsonify({'status': 'OK' })
	else:
		return jsonify({'status': 'Error','msg': 'Unable to read POST data'})






if __name__ == '__main__':
	#app.run()
	app.run(host='0.0.0.0', debug=True, threaded=True)
