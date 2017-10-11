"""
This template is for future tests within the Cognition and Action in Real and Virtual Environments (CARVE) Lab.
Designed by: Dr. Kristen Macuga, Erik Watterson
Programmed by: Erik Watterson
Development Platform: Vizard Virtual Reality Toolkit

Summmary:
This script is designed to be a template file for future VR spacial relation tests.
When ran, it starts by prompting the user for measurements of their height.
Once the user is measured, it generates 3 boxes for each hand, and a box for each foot.
Each hand box is located at the max length from the users shoulder to each respective axis X, Y, and Z,
The feet boxes are located slightly off the ground and forward from the users starting foot possition.
the premise of the future tests are to time the user from when they leave one box and enter a differing, or the same, box.
The ques to let the user know when to leave a starting position could be auditory, visual or tactile.
The pattern of boxes for the user to enter could be static or random deppending on the test.
One example of a test could be Simon Says using a virtual environment.
"""

#~ To do~
# 1.) Get info to post into text file.
# 2.) verify changes work for arm side sensors
# 3.) Start on Feet logic.

"""
The boxes are numerically assigned:
	right hand front = 0
	left hand front  = 1
	right hand side  = 2
	left hand side   = 3
	right foot front = 4
	left foot front  = 5
	start box right hand = start box left hand = 6
	end box = 7
"""


# general viz module
import viz
# vizinfo is used along w/ vizinput to gather input throughout the program 
import vizinfo
# vizshape is used for the creation and manipulation of the box sensors and tiles. 
import vizshape
# vizmath is used for various mathematical operations used in the program. 
import math
#import vizact # Kept in case it might be needed.
import viztask
# vizproximity is used for the creation and function of all proximity sensors.
import vizproximity
# viztime is used primarily for the viz.tick() function, which captures the value of the internal clock 
# that goes on in during vizard's runtime. 
import time
# vizinput is used along w/ vizinfo to gather input throughout the program 
import vizinput
# Vizconnect is used for tracking the position and orientation of the head and hand. 
import vizconnect
import Vizconnect_config_4limbs_avatar_copy
import hand # (From fitz test) Kept in case it was needed.
import random # Used to cycle test list.
import time	# Used for it's CPU clock time function

# main_data is the text file where all the data is written and saved to. The format currently is accurate with notepad. May
# be off in other text editors.
name=vizinput.input('Input name of file: ') 
main_data= open(name, 'a')

# The scale of the square boxes. Changing this will dynamically change the size of all of them.
bSize = 0.2 

# General variables
enterSensorCount = [0]*8 # Used to count the number of times a tracker enters a sensor.
appendages = ["temp", "rhf", "lhf"] # used to verify correct limb. Temp is used as a buffer.
requiredAppendage = appendages[0] # The appendage to look for
appendagesItterator = 0 # current location in the appendages array

# Start Sensor variables
startReadyCounter = 0 # As each appendage enters a start box, it readies the trial to start.
start = False # used to determine if the sensors are ready to be used. Procs after ready start counter = max.
startBoxSum = 2	# used to determine how many start boxes there are. Used for comparison with startBoxCounter.


# Time Variables
timeA = 0.0			# Start time
timeB = 0.0			# Stores the time frame when you enter a sensor
timeEnd = 0.0		# Stores the entire time frame of the trial
trialTimeList = []  # Used to make the text to file printing easier and also stores all of trial times.
leftEarly = "No"	# If the user left early, this will change to "Yes"

viz.mouse.setVisible(viz.OFF) # remove mouse cursor when program starts

# General screen setup. 
viz.setMultiSample(4)
viz.fov(60)
	

#Tracking data from vizconnect_config__________________________________________

'''
#### HEADSET
vizconnect.go('./Vizconnect_config_4limbs.py')
headTracker = vizconnect.getRawTracker('optical_heading')
handTracker = vizconnect.getRawTracker('ppt_hand')
viewpoint = vizconnect.getDisplay().getNode3d()
main_sphere=vizshape.addSphere(radius=.005,slices=20,stacks=20) #Adding a sphere to represent user's fingertip
viz.link(handTracker, main_sphere) #Linking sphere to vizconnect tracking of the hand


### For mouse and keyboard walking to test outside lab
'''

vizconnect.go('./Vizconnect_config_4limbs_avatar_copy.py')
### Substitute mouse and keyboard tracking
leftHand = vizconnect.getRawTracker('lefthand')
headTracker = vizconnect.getRawTracker('mouse_and_keyboard_walking')
handTracker = vizconnect.getRawTracker('keyboard')
main_sphere=vizshape.addSphere(radius=.005,slices=20,stacks=20) #Adding a sphere to represent user's fingertip
#left_main_sphere=vizshape.addSphere(radius=.01,slices=20,stacks=20) #Adding a sphere to represent user's fingertip
#viz.link(handTracker, main_sphere) #Linking sphere to vizconnect tracking of the hand
viz.link(leftHand, main_sphere)
viz.MainView.setPosition([0,15,-15])#~Made it slightly lower for mouse and keyboard

#Create proximity manager to manage sensors____________________________________

manager = vizproximity.Manager()
manager.setDebug(viz.OFF) #Turn on to add wireframe, done below with keypress 'l'
vizact.onkeydown('l',manager.setDebug,viz.TOGGLE)
   
# Setting hand tracked position as target 
right_hand = vizproximity.Target(handTracker)
left_hand = vizproximity.Target(leftHand)
manager.addTarget(left_hand)
manager.addTarget(right_hand)

# Visual grid that appears on floor
grid = vizshape.addGrid(color=[0.2]*3)
viz.clearcolor(viz.GRAY)
#~ can be removed, kept for reference of spacial dimensions
#table= vizshape.addBox([1.05,.000000001,.495],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.PURPLE)
#table.setPosition(0,.76-.001,.23) 


#Timer Functions___________________________________________________________________________________

"""
Used to check if participant left the start sensor early.

Currently not in use!
"""

def scheduleTimer(sensor):
	
	yield viztask.waitTime(3) #~ wait 3 seconds before it go's
	
	##~ Taken from Tutorial: "Measuring reaction time"

	"""~ Can't quite get it to work correctly but wanted to keep for referance.
	
	#Wait for next frame to be drawn to screen.
	d = yield viztask.waitDraw()
	#Save display time
	displayTime = d.time
	#Wait for movement outside of the sensor
	d = yield viztask.waitSensorUp(sensor)
	#save display time
	reactionTime = d.time - displayTime
	
	#print reaction time
	print("Reaction time: " + str(reactionTime))
	"""

#boxes_____________________________________________________________________________________________

"""
 Set temporary box positions.
 
 #~ This function isn't necissary but I wanted to keep it in case of back tracking
"""
def massSetBoxPos(boxList):
	print("massSetBoxPos is a go!")
	
	#~ Hands, front
	boxList[0].setPosition(0.2,1.2192,0.57912) 
	boxList[1].setPosition(-0.2,1.2192,0.57912)
	
	#~ Hands, Side
	boxList[2].setPosition(1.2192,1.2192,0)
	boxList[3].setPosition(-1.2192,1.2192,0)
	
	#~ Feet, front
	#boxList[4].setPosition(0.4572,0.254,0.1524)
	#boxList[5].setPosition(-0.4572,0.254,0.1524)

	#~ Start sensor, hands
	boxList[6].setPosition(0,0,0)
	boxList[7].setPosition(0,0,0)
	boxList[8].setPosition(0,0,0)
	
	return boxList


"""		
 This function makes a series of boxes then calls a function to set the size and position of the boxes.
"""

def massMakeBoxes(boxList):
	print("massMakeBozes is a go!")
	
	# Make all of the boxes needed in the trail.
	for x in range(9):
		print("making box " + str(x))
		temp = vizshape.addBox([bSize,bSize,bSize],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
		boxList.append(temp)
		
	massSetBoxPos(boxList)	
	return boxList



#Sensors_____________________________________________________________________________

def sensorOnEnterRightFront(sensor):
	global requiredAppendage
	global start
	global timeA
	global timeB
	global trialTimeList
	global enterSensorCount
	
	enterSensorCount[0] = enterSensorCount[0] + 1
	
	print("Entered box num: 0")
	
	if(start == True):
		if(requiredAppendage == "rhf"):
			print("Entered rhf")
			timeB = time.clock() - timeA
			trialTimeList.append(timeB)
			
			

def sensorOnExitRightFront(sensor):
	print("exited box num: 0")
	
	if(requiredAppendage == "rhf"):
		print("Exited rhf")
			
			
def sensorOnEnterLeftFront(sensor):
	global requiredAppendage
	global start
	global timeA
	global timeB
	global trialTimeList
	global enterSensorCount
	
	enterSensorCount[1] = enterSensorCount[1] + 1
	
	print("Entered box num: 1")
	
	if(start == True):
		if(requiredAppendage == "lhf"):
			print("Entered lhf")
			timeB = time.clock() - timeA
			trialTimeList.append(timeB)

def sensorOnExitLeftFront(sensor):
	print("exited box num: 1")
	
	if(requiredAppendage == "rhf"):
		print("Exited rhf")
		

def sensorOnEnterRightSide(sensor):
	global required
	global start
	global timeA
	global timeB
	global trialTimeList
	global enterSensorCount
	
	enterSensorCount[2] = enterSensorCount[2] + 1
	print("Entered box num: 2")
	
	if(start == True):
		if(requiredAppendage == "rhs"):
			print("Entered rhs")
			timeB = time.clock() - timeA
			trialTimeList.append(timeB)

def sensorOnExitRightSide(sensor):
	print("exited box num: 2")
	
	if(requiredAppendage == "rhs"):
		print("Exited rhs")

def sensorOnEnterLeftSide(sensor):
	global requiredAppendage
	global start
	global timeA
	global timeB
	global trialTimeList
	global enterSensorCount
	
	enterSensorCount[3] = enterSensorCount[3] + 1	
	print("Entered box num: 3")

	if(start == True):
		if(requiredAppendage == "lhs"):
			print("Entered lhs")
			timeB = time.clock() - timeA
			trialTimeList.append(timeB)

def sensorOnExitLeftSide(sensor):
	print("exited box num: 3")

	
	if(requiredAppendage == "lhs"):
		print("Exited lhs")

"""
def sensorOnEnterRightFoot(sensor):
	print("Entered box num: 4")
	global enterSensorCount
	
	enterSensorCount[4] = enterSensorCount[4] + 1

def sensorOnExitRightFoot(sensor):
	print("exited box num: 4")

def sensorOnEnterLeftFoot(sensor):
	print("Entered box num: 5")
	global enterSensorCount
	
	enterSensorCount[5] = enterSensorCount[5] + 1
	
def sensorOnExitLeftFoot(sensor):
	print("exited box num: 5")
"""

# Functions for start sensors

def sensorExitStart(sensor):
	global timeA
	global leftEarly
	
	print("Exit Start Sensor")
	global startReadyCounter
	# Check if they left before the desired time.
	if(time.clock() - timeA < 3):  # Change the number 3 to any number of desired seconds
		leftEarly = "yes"
		print(leftEarly)
	else:
		leftEarly = "no"
		print(leftEarly)
		
	startReadyCounter = startReadyCounter - 1

	
def sensorEnterStart(sensor):
	print("Enter Start Sensor")
	global startReadyCounter
	global start
	global requiredAppendage
	global appendages
	global timeA
	global enterSensorCount
	
	enterSensorCount[6] = enterSensorCount[6] + 1
	startReadyCounter = startReadyCounter + 1
	print("Appendages inside start boxes: " + str(startReadyCounter))
	
	# Please keep all hands inside of the ride, if appendages are not in the startboxes the trial won't start
	if(startReadyCounter == startBoxSum):
		print("ready")
		
		# make sure to not double count anything
		# If this is True then it tells us we have already done this part and have re-entered the start box
		if(start == False):
			
			appendages.pop(0) # removes the first trial so as to reset the test.
			random.shuffle(appendages)
			requiredAppendage = appendages[0]
			print(str(appendages[0]))
			
			timeA = time.clock()
			
			start = True
		
		# Start timers
		
def sensorEnterEnd(sensor):
	print("Enter end sensor")
	global appendagesItterator
	global start
	global timeEnd
	global timeA
	global trialTimeList
	global leftEarly
	global enterSensorCount
	
	enterSensorCount[7] = enterSensorCount[7] + 1

	if(manager.getActiveTargets() == manager.getActiveTargets(sensor=endSensor)): # Used to provent potential issues when trying to record data. If a tracker is inside of another sensor then there could be time or count issues.
		if(start == True): # used to protect from doubling the effects of the sensor
			print("End sensor only active")
			print(len(appendages))
		
			# End timers
			timeEnd = time.clock() - timeA
			print(timeEnd)
			
			# Add to the list
			trialTimeList.append(timeEnd)
			trialTimeList.append(leftEarly)
			
			print(trialTimeList)
			
			#~ we can either print to a text file here, or we can store the variables for later.
			#print to text = trialTimeList
			#print to text = enterSensorCount
			
			del trialTimeList[:] # Restart list for use in next trial
			

		
			if(len(appendages) > 1):
				start = False
			
			else:
				viz.quit()
	
	else:
		print("Please check appendages")


#Main Program_____________________________________________________________________________________________


""" We need the following measurements:

1) the measurement from foot to shoulde r.
2) the measurement from fingertip to shoulder.
3) the measurement from shoulder to shoulder.

This has been changed bellow. 
"""

boxList = [] #~ stores boxes
massMakeBoxes(boxList)

width = float(vizinput.input('Input the length from soulder to shoulder: \n '))
hieght = float(vizinput.input('Input the length from shoulder to foot: \n '))
length = float(vizinput.input('Input the length from soulder to arm: \n '))

# coordinates for right hand front

	# Adjust for centering the boxs
x = width / 2 - 0.05
y = hieght - 0.05
z = length - 0.05

boxList[0].setPosition(x, y, z) 
rightFrontSensor = vizproximity.Sensor(vizproximity.Box([bSize,bSize,bSize]),boxList[0])
manager.addSensor(rightFrontSensor)
boxList[0].visible(viz.OFF)

# coordinates for left hand front
boxList[1].setPosition(-x, y, z)
leftFrontSensor = vizproximity.Sensor(vizproximity.Box([bSize,bSize,bSize]),boxList[1])
manager.addSensor(leftFrontSensor)
boxList[1].visible(viz.OFF)

# coordinates for start sensor right hand

boxList[6].setPosition(x, hieght - length, 0)
rightHandStart = vizproximity.Sensor(vizproximity.Box([bSize,bSize,bSize]),boxList[6])
manager.addSensor(rightHandStart)
boxList[6].visible(viz.OFF)

# coordinates for start sensor left hand
boxList[7].setPosition(-x, hieght - length, 0)
leftHandStart = vizproximity.Sensor(vizproximity.Box([bSize,bSize,bSize]),boxList[7])
manager.addSensor(leftHandStart)
boxList[7].visible(viz.OFF)

# coordinates for the end sensor
boxList[8].setPosition(0, hieght, 0.1)
endSensor = vizproximity.Sensor(vizproximity.Box([bSize,bSize,bSize]),boxList[8])
manager.addSensor(endSensor)
boxList[8].visible(viz.OFF)


# coordinates for right hand side

	# Adjust for centering the boxes
x = length - 0.05
y = hieght - 0.05
z = 0

boxList[2].setPosition(x, y, z) 
rightSideSensor = vizproximity.Sensor(vizproximity.Box([bSize,bSize,bSize]),boxList[2])
manager.addSensor(rightSideSensor)
boxList[2].visible(viz.OFF)

# coordinates for left hand side
boxList[3].setPosition(-x, y, z) 
leftSideSensor = vizproximity.Sensor(vizproximity.Box([bSize,bSize,bSize]),boxList[3])
manager.addSensor(leftSideSensor)
boxList[3].visible(viz.OFF)

"""
# coordinates for right foot front

	# Adjust for centering boxes
x = width / 2 - 0.05
y = 0.254
z = 0.1524

boxList[4].setPosition(x, y, z) 
rightFootSensor = vizproximity.Sensor(vizproximity.Box([bSize,bSize,bSize]),boxList[4])
manager.addSensor(rightFootSensor)
"""
boxList[4].visible(viz.OFF)

"""
# coordinates for left foot front
boxList[5].setPosition(-x, y, z) 
leftFootSensor = vizproximity.Sensor(vizproximity.Box([bSize,bSize,bSize]),boxList[5])
manager.addSensor(leftFootSensor)
"""
boxList[5].visible(viz.OFF)




manager.onEnter(rightFrontSensor, sensorOnEnterRightFront)
manager.onExit(rightFrontSensor, sensorOnExitRightFront)
manager.onEnter(leftFrontSensor, sensorOnEnterLeftFront)
manager.onExit(leftFrontSensor, sensorOnExitLeftFront)

manager.onEnter(rightHandStart, sensorEnterStart)
manager.onExit(leftHandStart, sensorExitStart)
manager.onEnter(leftHandStart, sensorEnterStart)
manager.onExit(rightHandStart, sensorExitStart)
manager.onEnter(endSensor, sensorEnterEnd)
#manager.onExit(endSensor, sensorExitEnd) #~ Currently no logic is associated with exiting the end sensor so the function does not exist.


#Run___________________________________________________________________________
viz.go()

