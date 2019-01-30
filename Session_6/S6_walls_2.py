from BrickPi import *
import threading
import random


TOUCH_CONFIG = 1
ULTRASONIC_CONFIG = 2
BRAITENBERG_CONFIG = 3

class Robot:
	def __init__(self,config=ULTRASONIC_CONFIG):
		BrickPiSetup()
		BrickPi.MotorEnable[PORT_A] = 1
		BrickPi.MotorEnable[PORT_C] = 1
		BrickPi.MotorEnable[PORT_D] = 1
		BrickPi.SensorType[PORT_1] = TYPE_SENSOR_RAW   
		BrickPi.SensorType[PORT_4] = TYPE_SENSOR_RAW   
		if config==ULTRASONIC_CONFIG:
			BrickPi.SensorType[PORT_2] = TYPE_SENSOR_LIGHT_ON
			BrickPi.SensorType[PORT_3] = TYPE_SENSOR_ULTRASONIC_CONT
			print('Robot configuration: ultrasonic sensor')
		elif config==BRAITENBERG_CONFIG:
			BrickPi.SensorType[PORT_2] = TYPE_SENSOR_LIGHT_OFF
			BrickPi.SensorType[PORT_3] = TYPE_SENSOR_LIGHT_OFF
			print('Robot configuration: dual light sensor (Braitenberg)')
		else:
			BrickPi.SensorType[PORT_2] = TYPE_SENSOR_LIGHT_ON
			BrickPi.SensorType[PORT_3] = TYPE_SENSOR_TOUCH
			print('Robot configuration: touch sensor')

		BrickPiSetupSensors()
		self.running = True
		self.error = False
		self.config = config
		self.thread = threading.Thread(None,self.update)
		self.thread.start()
		time.sleep(0.1)

	def update(self):
		while self.running:
			if self.error:
				value = BrickPiSetupSensors()
				if value==0:
					self.error = False
			else:
				value = BrickPiUpdateValues()
				if value==0:
					if self.config==ULTRASONIC_CONFIG:
						if self.ultrasound() == -1:
							self.error = True
						if self.light() < 255:
							self.error = True
						(d1, d2) = self.distance()
						if d1 > 800 or d1 < 100 or d2 > 800 or d2 < 100:
							self.error = True
					elif self.config==TOUCH_CONFIG:
						if self.light() < 255:
							self.error = True
						(d1, d2) = self.distance()
						if d1 > 800 or d1 < 100 or d2 > 800 or d2 < 100:
							self.error = True
					elif self.config==BRAITENBERG_CONFIG:
						pass
				else:
					self.error = True
			time.sleep(0.01)

	def terminate(self):
		self.running = False
		while self.thread.is_alive():
			pass
		
	def motors(self,power_A,power_D):
		BrickPi.MotorSpeed[PORT_A] = power_A
		BrickPi.MotorSpeed[PORT_D] = power_D

	def fan(self,power):
		BrickPi.MotorSpeed[PORT_C] = power

	def light(self):
		return BrickPi.Sensor[PORT_2]     
		
	def touch(self):
		return BrickPi.Sensor[PORT_3]     

	def ultrasound(self):
		return BrickPi.Sensor[PORT_3]

	def distance(self):
		return (BrickPi.Sensor[PORT_1],BrickPi.Sensor[PORT_4])
		
	def light_passive(self):
		sensor_2 = 870 - BrickPi.Sensor[PORT_2]
		sensor_3 = 870 - BrickPi.Sensor[PORT_3]
		return (sensor_2, sensor_3)

if __name__=="__main__":
	try:
		#robot = Robot(TOUCH_CONFIG)
		robot = Robot(ULTRASONIC_CONFIG)
		#robot = Robot(BRAITENBERG_CONFIG)

		#NOTA: robot con una diferencia de 5 entre una rueda y otra
		
		robot.motors(0,0)
		print('Ultrasound: %d' % robot.ultrasound())
		
		
		while True:
			if robot.error:
				print('\033[91m' + "ERROR!!!" + '\033[0m')
	
			#mientras no encuentre la línea blanca sigue hacia delante
			while robot.light() > 370:
				robot.motors(75,70)
				time.sleep(0.1)		
				
			#si la encuentra, gira a la izquierda marcha atrás
			robot.motors(-30,-50)
			time.sleep(1.5)
			#gira a la derecha hacia delante
			robot.motors(60,0)
			time.sleep(1.5)
	
			
	except KeyboardInterrupt:
		robot.terminate()
