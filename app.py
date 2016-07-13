#!/usr/bin/python
#from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
#from Adafruit.MCP230xx.Adafruit_MCP230xx import Adafruit_MCP230XX

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import RPi.GPIO as GPIO
import time
import atexit
import pickle
import os
import git



 
from tornado.options import define, options

define("port", default=8080, help="run on the given port", type=int)
 
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('app.html')





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

		# print 'DESIRED ANGLE: %s\n' %str( desiredAngle )
		# print 'CURRENT POS: %s\n' %str( self.motorPosDeg )

		if desiredAngle == self.motorPosDeg:
			return

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

		data = None

		if ( os.path.isfile( 'objs.pickle' )):
			with open('objs.pickle') as f:	
				data = pickle.load( f )
		
		if data :
			self.motorPosDeg = data[0]
		else :
			self.motorPosDeg = 0

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

		self.mcp1 = None
		self.mcp2 = None
		self.mcp3 = None

		# Setup the three MCP23017 chips
		self.mcp1 = Adafruit_MCP230XX( address=0x20, num_gpios=16 )
		# self.mcp2 = Adafruit_MCP230XX( address=0x21, num_gpios=16 )
		# self.mcp3 = Adafruit_MCP230XX( address=0x22, num_gpios=16 )
		
		# Set the pins to be outputs
		self.setupController( self.mcp1 )
		self.setupController( self.mcp2 )
		self.setupController( self.mcp3 )

		self.initSwitches()



	def initSwitches( self ):

		i=0;

		for x in range( 0, 45 ):
			
			# if i is 0 then trigger the switch
			if i == 1 :
				self.switch( x )
			
				# Wait for the sleep time
				time.sleep( self.sleepTime );

				# Increase I so that we miss the open relay
				i=0

			# if i is not 0 then reset it to 0
			else :
				i+=1

		

	def switch( self, id ):

		controller = None

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

		# If there is no controller then return
		if controller == None : return

		# TURN ON THE PIN
		controller.output( pin, 0 )
		
		# Wait for the sleep time
		time.sleep( self.sleepTime );

		# TURN OFF THE PIN
		controller.output( pin, 1 )



	def cleanup( self ):
		# Turn off all of the switches
		self.cleanController( self.mcp1 )
		self.cleanController( self.mcp2 )
		self.cleanController( self.mcp3 )



	def setupController( self, controller ):
		# If there is no controller then return
		if controller == None : return

		# Setup pins on the I2C Controller chip
		for x in range( 0, 16 ):
			controller.config( x, GPIO.OUT )
			controller.output( x, 1 )
		


	def cleanController( self, controller ):
		# If there is no controller then return
		if controller == None : return

		# Turn off the output pins
		for x in range( 0, 16 ):
			controller.output( x, 1 )
		








class WebSocketHandler( tornado.websocket.WebSocketHandler ):

	def open(self):
		print 'CONNECTED.\n'

		# Create the stepper motor controller
		#self.stepper = stepMotor()

		# Create the relay switch controller
		#self.switcher = relaySwitch()



	def on_message( self, message ):
		print 'RECIEVED MESSAGE: %s\n' %message

		# Split the message so that we can access the data elements
		#data = message.split(";")

		# If the first code is "turntable" then we want to control the turntable stepper motor
		#if ( str(data[0]) == "turntable" ):
		#	self.stepper.rotateToAngle( float( data[1]), float( data[2]))

		# If the first code is "switch" then we want to switch a point
		#elif ( str(data[0]) == "switch" ):
		#	self.switcher.switch( int( data[1]))

		# If the first code is "shutdown" to shutdown the Raspberry PI
		#elif ( str(data[0]) == "shutdown" ):
		#	self.switcher.cleanup();
		#	self.stepper.cleanup();
		#	os.system('shutdown -h now')

		# If the first code is "update" then update the code from git
		#elif ( str(data[0]) == "update" ):
		#	g = git.cmd.Git("https://github.com/c-andrews/RPI_track_control.git")
		#	g.pull()



	def on_close( self ):
		print 'CONNECTION CLOSED\n'



	def check_origin( self, origin ):
		return True



	def write_message( self, message ):
		print ( "IN WRITE MESSAGE " + message )
		self.write_message( message )





if __name__ == "__main__":

	tornado.options.parse_command_line()

	settings = {
		"assets_path": os.path.join(os.path.dirname(__file__), "assets" )
	}

	print "ASSET PATH:", settings['assets_path']
	
	app = tornado.web.Application(
	    handlers=[
	        (r"/", IndexHandler),
	        (r"/ws", WebSocketHandler),
	        (r"/(apple-touch-icon\.png)", tornado.web.StaticFileHandler, dict( path=settings['assets_path'])),
	    ],
	    **settings
	)

	httpServer = tornado.httpserver.HTTPServer( app )
	httpServer.listen( options.port )

	print "Listening on port:", options.port

	tornado.ioloop.IOLoop.instance().start()


# application = tornado.web.Application([( r'/ws', WSHandler ),])

# if __name__ == "__main__":
# 	http_server = tornado.httpserver.HTTPServer(application)
# 	http_server.listen(8888)
# 	main_loop = tornado.ioloop.IOLoop.instance()
# 	main_loop.start()
