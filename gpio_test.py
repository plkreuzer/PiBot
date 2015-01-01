import time
import RPi.GPIO as GPIO
from RPIO import PWM
import pygame
import signal
import sys

# Passive Infrared Receiver
# GPIO 4, pin 7
PIR_CHAN = 7

# Motor Control Ports
#   MOTOR_* is the right side
#   MOTOL_* is the left side
#GPIO 17, pin 11
MOTOR_EN = 17
#GPIO 22, pin 15
MOTOR_P1 = 15
#GPIO 27, pin 13
MOTOR_P2 = 13

#GPIO 23, pin 16
MOTOL_EN = 23
#GPIO 25, pin 22
MOTOL_P1 = 22
#GPIO 24, pin 18
MOTOL_P2 = 18

# SPeeds below are in microseconds, 20ms max.
MOTOR_SPEED_OFF = 0
MOTOR_SPEED_FULL = 1900
MOTOR_SPEED_HALF = 1000
MOTOR_SPEED_75 = 1500
MOTOR_SPEED_25 = 500

# Servo Control Ports
# NOTE: RPIO module uses GPIO X enumeration and not pinout enumeration.
# GPIO 5, pin 29
SERVO_PIN = 5
SERVO_FREQ = 50 # 50 Hz, 20ms
SERVO_RIGHT = 115
SERVO_FORWARD = 155
SERVO_LEFT = 199

# Echo 'Trigger' and 'Echo' Pins
# GPIO 6, pin 31
ECHO_TP = 31
# GPIO 13, pin 33
ECHO_EP = 33

PWM_DMA_CHAN = 14

def setupPWM():
  # 'servo' interface was the simple interface that used the same DMA as the audio card.
  # servo = PWM.Servo(dma_channel = PWM_DMA_CHAN)
  # #Set servo on SERVO_PIN to 1500us (1.5ms, straight forward)
  # servo.set_servo(SERVO_PIN, SERVO_FORWARD)
  # return servo
  PWM.setup()
  PWM.init_channel(PWM_DMA_CHAN)
  PWM.add_channel_pulse(PWM_DMA_CHAN, SERVO_PIN, 0, SERVO_FORWARD)
  PWM.add_channel_pulse(PWM_DMA_CHAN, MOTOR_EN, 0, MOTOR_SPEED_OFF)
  PWM.add_channel_pulse(PWM_DMA_CHAN, MOTOL_EN, 0, MOTOR_SPEED_OFF)

def changePWM(chan, pin, start, width):
  PWM.clear_channel_gpio(chan, pin)
  PWM.add_channel_pulse(chan, pin, start, width)
  
def setupGPIO():
  pygame.mixer.init()
  pygame.mixer.music.load('/home/pi/nas/PiBot/sounds/bark.wav')
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(PIR_CHAN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(MOTOR_P1, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(MOTOR_P2, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(MOTOL_P1, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(MOTOL_P2, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)


def motor_go_straight(speed):
  changePWM(PWM_DMA_CHAN, MOTOR_EN, 0, speed)
  changePWM(PWM_DMA_CHAN, MOTOL_EN, 0, speed)
  GPIO.output(MOTOR_P1, GPIO.HIGH)
  GPIO.output(MOTOR_P2, GPIO.LOW)
  GPIO.output(MOTOL_P1, GPIO.HIGH)
  GPIO.output(MOTOL_P2, GPIO.LOW)
  
def motor_turn_left(speed):
  changePWM(PWM_DMA_CHAN, MOTOR_EN, 0, speed)
  changePWM(PWM_DMA_CHAN, MOTOL_EN, 0, speed)
  GPIO.output(MOTOR_P1, GPIO.HIGH)
  GPIO.output(MOTOR_P2, GPIO.LOW)
  GPIO.output(MOTOL_P1, GPIO.LOW)
  GPIO.output(MOTOL_P2, GPIO.LOW)

def motor_spin_left(speed):
  changePWM(PWM_DMA_CHAN, MOTOR_EN, 0, speed)
  changePWM(PWM_DMA_CHAN, MOTOL_EN, 0, speed)
  GPIO.output(MOTOR_P1, GPIO.HIGH)
  GPIO.output(MOTOR_P2, GPIO.LOW)
  GPIO.output(MOTOL_P1, GPIO.LOW)
  GPIO.output(MOTOL_P2, GPIO.HIGH)

def motor_turn_right(speed):
  changePWM(PWM_DMA_CHAN, MOTOR_EN, 0, speed)
  changePWM(PWM_DMA_CHAN, MOTOL_EN, 0, speed)
  GPIO.output(MOTOR_P1, GPIO.LOW)
  GPIO.output(MOTOR_P2, GPIO.LOW)
  GPIO.output(MOTOL_P1, GPIO.HIGH)
  GPIO.output(MOTOL_P2, GPIO.LOW)
  
def motor_spin_right(speed):
  changePWM(PWM_DMA_CHAN, MOTOR_EN, 0, speed)
  changePWM(PWM_DMA_CHAN, MOTOL_EN, 0, speed)
  GPIO.output(MOTOR_P1, GPIO.LOW)
  GPIO.output(MOTOR_P2, GPIO.HIGH)
  GPIO.output(MOTOL_P1, GPIO.HIGH)
  GPIO.output(MOTOL_P2, GPIO.LOW)

def motor_stop():
  changePWM(PWM_DMA_CHAN, MOTOR_EN, 0, MOTOR_SPEED_OFF)
  changePWM(PWM_DMA_CHAN, MOTOL_EN, 0, MOTOR_SPEED_OFF)
  GPIO.output(MOTOR_P1, GPIO.LOW)
  GPIO.output(MOTOR_P2, GPIO.LOW)
  GPIO.output(MOTOL_P1, GPIO.LOW)
  GPIO.output(MOTOL_P2, GPIO.LOW)

def motor_coast():
  changePWM(PWM_DMA_CHAN, MOTOR_EN, 0, MOTOR_SPEED_OFF)
  changePWM(PWM_DMA_CHAN, MOTOL_EN, 0, MOTOR_SPEED_OFF)
  GPIO.output(MOTOR_P1, GPIO.LOW)
  GPIO.output(MOTOR_P2, GPIO.LOW)
  GPIO.output(MOTOL_P1, GPIO.LOW)
  GPIO.output(MOTOL_P2, GPIO.LOW)

def motion_detected(channel):
  print('Motion Detected!')
  if pygame.mixer.music.get_busy() != True:
    pygame.mixer.music.play()

def cleanup():
  print('Cleaning up IO\'s')
  pygame.mixer.music.stop()
  pygame.mixer.quit()
  GPIO.remove_event_detect(PIR_CHAN)
  PWM.cleanup()
	
def sigintHandler(signum, frame):
  print('Exitting application')
  cleanup()
  sys.exit()
  
setupGPIO()
servo = setupPWM()

GPIO.add_event_detect(PIR_CHAN, GPIO.RISING)
GPIO.add_event_callback(PIR_CHAN, motion_detected)
signal.signal(signal.SIGINT, sigintHandler)

print('Waiting...')
while 1:
  # servo.set_servo(SERVO_PIN, SERVO_FORWARD)
  changePWM(PWM_DMA_CHAN, SERVO_PIN, 0, SERVO_FORWARD)
  motor_go_straight(MOTOR_SPEED_HALF)
  time.sleep(2)
  motor_go_straight(MOTOR_SPEED_FULL)
  time.sleep(2)
  motor_turn_left(MOTOR_SPEED_HALF)
  # servo.set_servo(SERVO_PIN, SERVO_LEFT)
  changePWM(PWM_DMA_CHAN, SERVO_PIN, 0, SERVO_LEFT)
  time.sleep(2)
  motor_turn_right(MOTOR_SPEED_HALF)
  # servo.set_servo(SERVO_PIN, SERVO_RIGHT)
  changePWM(PWM_DMA_CHAN, SERVO_PIN, 0, SERVO_RIGHT)
  time.sleep(2)
  motor_stop()
  # servo.set_servo(SERVO_PIN, SERVO_FORWARD)
  changePWM(PWM_DMA_CHAN, SERVO_PIN, 0, SERVO_FORWARD)
  time.sleep(2)

cleanup()

