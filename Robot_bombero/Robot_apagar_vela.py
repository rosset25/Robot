#NOTA: este código es un poco chapucero a falta de tiempo

from Robot import *
import numpy

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2


import sys 


from candle import candle

S = [230, 248, 266, 297, 350, 445, 680, 760]
D = [28, 24, 20, 16, 12, 8, 4, 3]

robot = Robot(TOUCH_CONFIG)

time.sleep(1)
robot.fan(1)
time.sleep(5)

camera = PiCamera()
rawCapture = PiRGBArray(camera)
time.sleep(1.0)

contador = 0
habitacion = 0


def deteccion_vela():	
	
	i = 0
	converged = False
	rawCapture.truncate(0)
	camera.capture(rawCapture, format='bgr')
	image = rawCapture.array
	c = candle(image)
	#time.sleep(3)
	
	print("vuelta a empezar")
	while (converged == False or i < 9) and contador < 1:
		print("buscando vela")
		rawCapture.truncate(0)
		camera.capture(rawCapture, format='bgr')
		image = rawCapture.array
		c = candle(image)
		
		if i == 0:
			robot.motors(0,0)
			time.sleep(1)
		
		if c is None:
			print("candle not found")
			robot.motors(60,0)
			time.sleep(0.3)
			robot.motors(0,0)
			time.sleep(0.5)
			i = i +1
			print(i)
			if i == 10:
				break
		else:
			print("ENCONTRADA!!!")
			enchufar_ventilador()
			#print(x, dx, motor)
			converged = True
			break

			
def enchufar_ventilador():

	print("apagando vela....")
	converged = False
	while not converged:
		rawCapture.truncate(0)
		camera.capture(rawCapture, format='bgr')
		image = rawCapture.array
		c = candle(image)
		if c is None:
			print("candle not found")
		else:
			print("apagando vela...1")
			x, y, w, h = c
			dx = x - 360
			motor = dx * 500 / 360
			if motor > 50:
				motor = 50
			if motor < -50:
				motor = -50
			print(x, dx, motor)
			robot.motors(motor, -motor)
			time.sleep(0.1)
			robot.motors(0,0)
			robot.fan(200)
			converged = abs(motor) < 50
	
	
	while robot.touch() != 1:
		robot.fan(200)
		robot.motors(40,40)
		time.sleep(0.1)
	
	robot.motors(-43,-40)
	time.sleep(0.3)
	robot.motors(0,0)
	time.sleep(0.4)
	print("encendiendo ventilador...")
	robot.fan(200)
	time.sleep(3)
	robot.fan(0)
	#robot.terminate()


	
try:
	
	
	empezar_habitacion = False
	
	comienzo = int(sys.argv[1])
	if sys.argv[1] == "1":
			empezar_habitacion = True
	
	
	print(empezar_habitacion)
	
	dentro_habitacion = False #dependiendo de si empieza dentro de una habitación o no, 
							  #esta variable significará lo contrario o no
	palante = True
	
	contador_vela = 0
	contador_hab = 1
	
	if empezar_habitacion == True:
		contador_vela = 1

	
	while True:
		
		(lV, rV) = robot.distance()
		
		if robot.light() < 520:
			if dentro_habitacion == True:
				dentro_habitacion = False
				palante = True
				if habitacion >= 4:
					habitacion = 0
			else:
				dentro_habitacion = True

			#Se comprueban diferentes condiciones dependiendo o no de si empezó en una habitación o no
			
			if (habitacion == 0 and dentro_habitacion == True and empezar_habitacion == False) or (habitacion == 0 and dentro_habitacion == False and empezar_habitacion == True):
				robot.motors(70,0)
				time.sleep(0.2)
				
			robot.motors(70,60)
			time.sleep(0.8)
			

			if dentro_habitacion == True and empezar_habitacion == True and (habitacion >= 4 or contador_hab == 0):
				if rV < 250:
					robot.motors(50,70)
					time.sleep(0.2)
					robot.motors(60,0)
					time.sleep(0.8)
					robot.motors(60,50)
					time.sleep(3)
				
			
			if dentro_habitacion == True:
				habitacion = habitacion +1
				contador_hab = contador_hab +1
				if contador_hab > 1:
					contador_hab = 0
					
		
			
		if (habitacion == 1 and palante == True and dentro_habitacion == False and empezar_habitacion = False) or ((habitacion == 1 or contador_hab == 1) and palante == True and dentro_habitacion == True and empezar_habitacion == True):
			robot.motors(38,70)
			time.sleep(1)
			
			if robot.touch() == 1:
				robot.motors(-70,-40)
				time.sleep(1)
			
			palante = False
		
		
		if not robot.error: #si no ha habido ningún error
		
			
			if (dentro_habitacion == True and empezar_habitacion == False) or (dentro_habitacion == False and empezar_habitacion == True):
				
				converged = False
				if contador == 0:
					deteccion_vela()
					
					contador_vela = contador_vela +1
					print("acabee")
					time.sleep(2)

			
			if (dentro_habitacion == False and empezar_habitacion == False) or (dentro_habitacion == True and empezar_habitacion == True):
				contador_vela = 0
			
		
			if robot.touch() == 1:
					if (habitacion >= 4 and empezar_habitacion == True and dentro_habitacion == True) or (habitacion == 0 and empezar_habitacion == False and dentro_habitacion == False):
						robot.motors(-70,-50)
						time.sleep(0.8)
						robot.motors(20,70)
						time.sleep(0.3)
					
					elif habitacion != 1 or (habitacion == 1 and empezar_habitacion == True):
						print("habitacion: ", habitacion)
						robot.motors(-40,-70)
						time.sleep(0.8)
					else:
						robot.motors(-70,-50)
						time.sleep(0.8)
				
			
			d = numpy.interp(rV,S,D)
			print(rV,d)
			
			#Para que siga siempre a la pared de su derecha
			
			if d>=16 and d<19:
				robot.motors(72, 72)
			elif d<16:
				robot.motors(3, 65)
			else:
				robot.motors(70, 42)
		else:
			print('Error!')             
		time.sleep(0.01)
except KeyboardInterrupt:
	pass
robot.terminate()
