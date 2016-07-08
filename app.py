#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
from Adafruit.MCP230xx.Adafruit_MCP230xx import Adafruit_MCP230XX

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
# import RPi.GPIO as GPIO
import time
import atexit
import pickle
import os
import git





# STEP MOTOR
class stepMotor:
	
	#init gpio and rotate motor to initial position (0 degrees)
	def __init__( self ):
		
		# create a default object, no changes to I2C address or frequency
		self.mh = Adafruit_MotorHAT( addr=0x60 )

		# 200 steps/rev, motor port #1
		self.stepper = self.mh.getStepper( 200, 1 )
	
		# 30 RPM
		self.stepper.setSpeed(30)

		# Start with the motor off
		self.turnOff();

		#current motor position in degrees [0,360]
		self.motorPosDeg = 0
		
		# Initalise the starting position
		self.initPos()

		# Register the turn off function
		atexit.register( self.turnOff )



	#rotate motor in clockwise direction
	def rotateR( self, noSteps, speed ):

		# Set the speed
		self.stepper.setSpeed( speed )

		# Start stepping: SINGLE, DOUBLE, INTERLEAVE, MICROSTEP
		self.stepper.step( noSteps, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP )
	
		# Turn off the motor
		self.turnOff()

		# Get the motor position
		self.motorPosDeg -= noSteps * 1.8

		# If the position is less than 0 then add the position to 360 
		# (pos is going to be a negative which is why we add the position to 360)
		if ( self.motorPosDeg < 0 ):
			self.motorPosDeg = 360 + self.motorPosDeg

		# Store the position just in case we loose power
		self.storePos()
	


	#rotate motor in counterclockwise direction
	def rotateL( self, noSteps, speed ):

		# Set the speed
		self.stepper.setSpeed( speed )

		# Start stepping: SINGLE, DOUBLE, INTERLEAVE, MICROSTEP
		self.stepper.step( noSteps, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP )
		
		# Turn off the motor
		self.turnOff()

		# Get the motor position
		self.motorPosDeg += noSteps * 1.8

		# If the position is greater than 3060 then reset the rotation
		if ( self.motorPosDeg >= 360 ):
			self.motorPosDeg = self.motorPosDeg - 360

		# Store the position just in case we loose power
		self.storePos()


	
	#rotate motor to specific position
	def rotateToAngle( self, desiredAngle, speed ):

		s = 1

		deltaAngle = abs( self.motorPosDeg - desiredAngle )

		if ( desiredAngle > self.motorPosDeg ):
			if ( deltaAngle >= 180 ):
				self.rotateR( int(( 360 - deltaAngle ) / 1.8 ), s )
			else:
				self.rotateL( int( deltaAngle / 1.8 ), s )
		else:
			if ( deltaAngle >= 180 ):
				self.rotateL( int(( 360 - deltaAngle ) / 1.8 ), s )
			else:
				self.rotateR( int( deltaAngle / 1.8 ), s )


				
	# Go to initial position defined by optical sensor
	def initPos( self ):

		if ( os.path.isfile( 'objs.pickle' )):
			with open('objs.pickle') as f:	
				self.motorPosDeg = pickle.load( f )

		print 'START POS: %s\n' %str( self.motorPosDeg )

		# Rotate the turntable to 0 so it has "reset"
		self.rotateToAngle( 0, 0 )



	def storePos( self ):

		# print 'CURRENT POS: %s\n' %str( self.motorPosDeg )

		# Saving the objects:
		with open('objs.pickle', 'w') as f:
			pickle.dump([ self.motorPosDeg ], f )


		
	#turn coils off
	# recommended for auto-disabling motors on shutdown!
	def turnOff( self ):
		# Turn off the motor
		self.mh.getMotor(1).run( Adafruit_MotorHAT.RELEASE )
		self.mh.getMotor(2).run( Adafruit_MotorHAT.RELEASE )
		self.mh.getMotor(3).run( Adafruit_MotorHAT.RELEASE )
		self.mh.getMotor(4).run( Adafruit_MotorHAT.RELEASE )


	def cleanup( self ):
		# Turn off the motors
		self.turnOff()








# STEP MOTOR
class relaySwitch:

	def __init__( self ):

		# Set the sleep time
		self.sleepTime = 0.1

		# Setup the three MCP23017 chips
		self.mcp1 = Adafruit_MCP230XX( address=0x20, num_gpios=16 )
		self.mcp2 = Adafruit_MCP230XX( busnum=1, address=0x21, num_gpios=16 )
		self.mcp3 = Adafruit_MCP230XX( busnum=1, address=0x22, num_gpios=16 )
		
		# Set the pins to be outputs
		self.setupController( self.mcp1 )
		self.setupController( self.mcp2 )
		self.setupController( self.mcp3 )

		self.initSwitches()



	def initSwitches( self ):

		i=0;

		for x in range( 0, 45 ):
			
			# if i is 0 then trigger the switch
			if i == 0:
				self.switch( x )
			
				# Wait for the sleep time
				time.sleep( self.sleepTime );

				# Increase I so that we miss the open relay
				i++

			# if i is not 0 then reset it to 0
			else
				i=0

		

	def switch( self, id ):

		# Get the first relay controller
		if id <= 15 :
			controller = self.mcp1
			pin = id

		# Get the second relay controller
		elif id <= 30 :
			controller = self.mcp2
			pin = id - 15

		# Get the thrid relay controller
		elif id < 45 :
			controller = self.mcp3
			pin = id - 30

		# TURN ON THE PIN
		controller.output( pin, 1 )
		
		# Wait for the sleep time
		time.sleep( self.sleepTime );

		# TURN OFF THE PIN
		controller.output( pin, 0 )



	def cleanup( self ):
		# Turn off all of the switches
		self.cleanController( self.mcp1 )
		self.cleanController( self.mcp2 )
		self.cleanController( self.mcp3 )



	def setupController( self, controller ):
		# Setup pins on the I2C Controller chip
		for x in range( 0, 15 ):
			controller.config( x, OUTPUT )
		


	def cleanController( self, controller ):
		# Turn off the output pins
		for x in range( 0, 15 ):
			controller.output( x, 0 )
		








class WSHandler( tornado.websocket.WebSocketHandler ):

	def open(self):
		print 'CONNECTED.\n'

		# Create the stepper motor controller
		self.stepper = stepMotor()

		# Create the relay switch controller
		self.switcher = relaySwitch()



	def on_message( self, message ):
		# print 'RECIEVED MESSAGE: %s\n' %message

		# Split the message so that we can access the data elements
		data = message.split(";")

		# If the first code is "turntable" then we want to control the turntable stepper motor
		if ( str(data[0]) == "turntable" ):
			self.stepper.rotateToAngle( float( data[1]), float( data[2]))

		# If the first code is "switch" then we want to switch a point
		elif ( str(data[0]) == "switch" ):
			self.switcher.switch( int( data[1]), int( data[2]))

		# If the first code is "shutdown" to shutdown the Raspberry PI
		elif ( str(data[0]) == "shutdown" ):
			self.switcher.cleanup();
			self.stepper.cleanup();
			os.system('shutdown -h now')

		# If the first code is "update" then update the code from git
		elif ( str(data[0]) == "update" ):
			g = git.cmd.Git("https://github.com/c-andrews/RPI_track_control.git")
			g.pull()



	def on_close( self ):
		print 'CONNECTION CLOSED\n'



	def check_origin( self, origin ):
		return True



	def write_message( self, message ):
		print ( "IN WRITE MESSAGE " + message )
		self.write_message( message )





application = tornado.web.Application([( r'/ws', WSHandler ),])

if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	main_loop = tornado.ioloop.IOLoop.instance()
	main_loop.start()