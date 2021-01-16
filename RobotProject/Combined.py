#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
from AlphaBot2 import AlphaBot2
#from rpi_ws281x import Adafruit_NeoPixel, Color
from TRSensors import TRSensor
import time
import cv2
import numpy as np
from look_up import Link,LookUp
from sklearn.cluster import DBSCAN
#from AlphaMessenger import send_msg, send_json
import ast
import socket
Button = 7
NODES = ['a','b','c','d','e','f','g','h']
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Button,GPIO.IN,GPIO.PUD_UP)

# Server 

listensocket = socket.socket() #Creates an instance of socket
Port = 8001 #Port to host server on
maxConnections = 999
IP = socket.gethostname() #IP address of local machine

listensocket.bind(('',Port))

#Starts server
listensocket.listen(maxConnections)
print("Server started at " + IP + " on port " + str(Port))



maximum = 30;
j = 0
integral = 0;
last_proportional = 0




TR = TRSensor()
Ab = AlphaBot2()
Ab.stop()
print("Line follow Example")
time.sleep(0.5)
for i in range(0,100):
	if(i<25 or i>= 75):
		Ab.right()
		Ab.setPWMA(30)
		Ab.setPWMB(30)
	else:
		Ab.left()
		Ab.setPWMA(30)
		Ab.setPWMB(30)
	TR.calibrate()
Ab.stop()

def calc_slope(line_segments,mask):
    pos = 0
    neg = 0
    equal = 0
    #print(line_segments)
    # try:
    for i in line_segments:
        coords = i[0] * 1.0
        if coords[2] - coords[0]== 0: #if line is vertical -> ignore
            equal+=1
            continue 
        slope = (coords[1] -coords[3])/(coords[2] - coords[0]) 
        if slope > 0:
            pos += 1
        else:
            neg += 1
    #print(f'left_vote: {neg},right vote: {pos},equal: {equal}')
        
    if neg>pos:
        return 'left' # return the most probable
    return 'right'

def slope_infer(mask):
    line_segments=  None

    edges = cv2.Canny(mask, 250, 500)
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(edges, rho, angle, min_threshold, 
                                    np.array([]), minLineLength=10, maxLineGap=2)

    return calc_slope(line_segments,mask)

def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)
def navigate(Ab,src,dst,direction=None):
    global HEAD
    camera = cv2.VideoCapture(-1)
    camera.set(3, 640)
    camera.set(4, 480)
    lookup=LookUp()
    link=lookup.get_rotation_link(src,dst) #get a link needed to stop rotation
    rotate=True
    HEAD = link.color
    stop_count=0
    while (True):
        #print("rotating ... ")
        if(rotate):
            camera.read()
            time.sleep(0.05)
            Ab.stop()

        

        _, image = camera.read()

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = link(hsv) #get a mask from hsv image
        
        cropped=np.copy(mask[-40:,:])
        dbin=np.array(cropped.nonzero()).T
        if(dbin.shape[0]!=0):
            rotate=True
            #Ab.stop()
            print("here ")
            db = DBSCAN(eps=5, min_samples=80, metric="euclidean", algorithm="auto")
            db_out = db.fit(dbin)
            for i,label in zip(dbin,db_out.labels_):
                    cropped[i[0],i[1]] = (label + 1) * 100
            if(len(np.where((np.unique(db_out.labels_) >= 0) == True)[0]) == 1): stop_count += 1
            if(stop_count>=3 and len(np.where((np.unique(db_out.labels_) >= 0) == True)[0]) == 1 and len(np.where((cropped != 0) == True)[0])/(cropped.shape[0]*cropped.shape[1])>=0.1): #if cluster is >= 10% of the frame then turn right/left until there are 2 clusters
                command = slope_infer(mask)
                if(command == 'left'):
                    direction=Ab.left

                elif(command == 'right'):
                    direction=Ab.right

            if(len(np.where((np.unique(db_out.labels_) >= 0) == True)[0]) >= 2 and len(np.where((cropped != 0) == True)[0])/(cropped.shape[0]*cropped.shape[1])>=0.4): #if clusters are >= 40% of the frame
                print("detected")
                Ab.setPWMA(0)
                Ab.setPWMB(0)
                Ab.stop()
                #cv2.imwrite('detected.jpg',image)
                return image
        rotate=True
        if(rotate):
            time.sleep(0.2)
            direction(speed=25)

def follow(Ab,TR,src,dst):
    global HEAD
    maximum = 25;
    j = 0
    integral = 0;
    last_proportional = 0
    lookup=LookUp()
    link, HEAD = lookup.get_stopping_link(src,dst) #get a link used to stop movement
    #print('stop color: ',link.color)
    Ab.setPWMA(20)
    Ab.setPWMB(20)
    
    Ab.forward()
    Ab.setPWMA(10)
    Ab.setPWMB(10)
    camera = cv2.VideoCapture(-1)
    camera.set(3, 640)
    camera.set(4, 480)
    stop_count=0
    acc=0
    direction = None
    prev = 0
    while True:
        
        position,Sensors = TR.readLine()
        _, image = camera.read()

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = link(hsv)
        if(position == prev and position != 2000):
            acc+=1
            #print('repeated pos ', position)
            if(acc == 5): #accelerate if the robot is stuck
                Ab.stop()
                Ab.setPWMA(30)
                Ab.setPWMB(30)
                Ab.forward()
                Ab.setPWMA(10)
                Ab.setPWMB(10)
                acc=0
                
                
                
        cropped=np.copy(mask[-40:,:])
        dbin=np.array(cropped.nonzero()).T
        if(dbin.shape[0]!=0):
            acc = 0
            Ab.stop()
            db = DBSCAN(eps=5, min_samples=80, metric="euclidean", algorithm="auto")
            db_out = db.fit(dbin)
            for i,label in zip(dbin,db_out.labels_):
                    cropped[i[0] , i[1]] = (label + 1) * 100
            if(len(np.where((np.unique(db_out.labels_) >= 0) == True)[0]) == 1): stop_count += 1
            if(stop_count >= 3 and len(np.where((np.unique(db_out.labels_) >= 0) == True)[0]) == 1 and len(np.where((cropped != 0) == True)[0])/(cropped.shape[0]*cropped.shape[1])>=0.2):
                command = slope_infer(mask)
                if command == None and direction != None:
                    direction(speed = 20)
                    continue
                if(command == 'left'):  
                    direction = Ab.left
                    direction(speed = 15)

                    continue
                else:
                    direction =Ab.right
                    direction(speed = 15)

                    continue
            if(len(np.where((np.unique(db_out.labels_) >= 0) == True)[0]) == 2 and len(np.where((cropped != 0) == True)[0])/(cropped.shape[0]*cropped.shape[1])>=0.4):
                print("detected")
                Ab.setPWMA(10)
                Ab.setPWMB(10)
                Ab.stop()
                return image
                #break
            Ab.forward()

        if(Sensors[0] >900 and Sensors[1] >900 and Sensors[2] >900 and Sensors[3] >900 and Sensors[4] >900):
            Ab.setPWMA(0)
            Ab.setPWMB(0);
        else:
    		# The "proportional" term should be 0 when we are on the line.
            proportional = position - 2000
    		
    		# Compute the derivative (change) and integral (sum) of the position.
            derivative = proportional - last_proportional
            integral += proportional
    		
    		# Remember the last position.
            last_proportional = proportional
    
    
            power_difference = proportional/20 + integral/10000 + derivative*3/2#proportional/30  + integral/10000 + derivative*2  
    
            if (power_difference > maximum):
                power_difference = maximum
            if (power_difference < - maximum):
                power_difference = - maximum
           # print(position,power_difference)
            if (power_difference < 0):
                Ab.setPWMA(maximum + power_difference)
                Ab.setPWMB(maximum);
            else:
                Ab.setPWMA(maximum);
                Ab.setPWMB(maximum - power_difference)
        prev = position



#while True:
        #Accepts the incomming connection
(clientsocket, address) = listensocket.accept()
message = "New connection made!"
clientsocket.send(message.encode())
init_HEAD = {0:'blue',1:'red',2:'yellow',3:'yellow',4:'yellow',5:'blue',6:'blue',7:'yellow'}
HEAD = None
#Sets up the GPIOs --Can only be used on Raspberry Pi

i = 0
message = clientsocket.recv(1024).decode() #Gets the incomming message
    
if len(message):
    print(message)
    time.sleep(0.5)
    message_list = ast.literal_eval(message)

    # alphabet number
    converted_message = []
    for element in message_list:
        number = ord(element) - 97
        converted_message.append(number)
path = converted_message
HEAD = init_HEAD[path[0]]
while True:
    if(i == len(path)-1):
        msg = "Finished!"
        clientsocket.send(msg.encode())
        clientsocket.close()
        break
    print(path)
    src = path[i]
    dst = path[(i+1)%len(path)]
    lookup = LookUp()
    command = lookup.get_command(src,dst,HEAD)
    position,Sensors = TR.readLine()
    print(command, src,dst, HEAD)
    msg = "I am going "+command+" :). My current node is " + NODES[src] + " and my current destination node is " + NODES[dst]
    clientsocket.send(msg.encode())
    if(command == "forward"):
        follow(Ab,TR,src,dst)
        i+=1
        msg = f'Done !:) {i+1} nodes out of {len(path)} are visited! \n ###################{i+1}/{len(path)}#######################'
    if(command == "left"):
        navigate(Ab,src,dst,direction=Ab.left)
        msg = f'I turned left! Now I have to move forward!\n ###################{i+1}/{len(path)}#######################'
    if(command == "right"):
        navigate(Ab,src,dst,direction=Ab.right)
        msg = f'I turned right`1! Now I have to move forward!\n ###################{i+1}/{len(path)}#######################'
   
    clientsocket.send(msg.encode())

    
