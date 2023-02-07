#!/usr/bin/python3
import math
import sys
import time
import threading
import os
import json
import array

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from dpeaDPi.DPiComputer import DPiComputer
from dpeaDPi.DPiStepper import *
from time import sleep

"""
Globals
"""

YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
AWAY_FROM_HOME = 1
BACK_TO_HOME = -1

sm = ScreenManager()
MAIN_SCREEN_NAME = 'main'
SECOND_WINDOW_NAME = 'second'


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):
    def build(self):
        self.title = "Newtonscradle"
        return sm


Window.clearcolor = (.9, .9, .9, 1)  # (WHITE)

"""
Hardware Setup
"""

dpiStepper0 = DPiStepper()
dpiStepper1 = DPiStepper()

dpiStepper0.setBoardNumber(0)
dpiStepper1.setBoardNumber(1)

if not dpiStepper1.initialize():
    print("Communication with the DPiStepper board 1 failed.")
sleep(1)
if not dpiStepper0.initialize():
    print("Communication with the DPiStepper board 0 failed.")

dpiStepper0.enableMotors(True)
dpiStepper1.enableMotors(True)

#############################################################################################

# 1 inch per turn
# 50.2 millimeters per inch

speed_in_mm_per_sec = 200
accel_in_mm_per_sec_per_sec = 200
dpiStepper0.setStepsPerMillimeter(0, 64)
dpiStepper0.setStepsPerMillimeter(1, 64)
dpiStepper1.setStepsPerMillimeter(0, 64)
dpiStepper1.setStepsPerMillimeter(1, 64)
dpiStepper0.setAccelerationInMillimetersPerSecondPerSecond(0, accel_in_mm_per_sec_per_sec)
dpiStepper0.setAccelerationInMillimetersPerSecondPerSecond(1, accel_in_mm_per_sec_per_sec)
dpiStepper1.setAccelerationInMillimetersPerSecondPerSecond(0, accel_in_mm_per_sec_per_sec)
dpiStepper1.setAccelerationInMillimetersPerSecondPerSecond(1, accel_in_mm_per_sec_per_sec)
dpiStepper0.setSpeedInMillimetersPerSecond(0, speed_in_mm_per_sec)
dpiStepper0.setSpeedInMillimetersPerSecond(1, speed_in_mm_per_sec)
dpiStepper1.setSpeedInMillimetersPerSecond(0, speed_in_mm_per_sec)
dpiStepper1.setSpeedInMillimetersPerSecond(1, speed_in_mm_per_sec)

"""
Main functions
"""


def move_to_first():
    sm.current = "main"


def move_to_second():
    sm.current = "second"


def countdown(ti):
    while ti:
        mins, secs = divmod(ti, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        ti -= 1

    move_to_first()


class MainScreen(Screen):
    pos_right_horizontal = 0
    pos_right_vertical = 0
    pos_left_horizontal = 0
    pos_left_vertical = 0

    stopballs = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def sethome(self):
        self.pos_right_horizontal = 0
        self.pos_right_vertical = 0
        self.pos_left_horizontal = 0
        self.pos_left_vertical = 0

    def moveRightCradle(self, mm, waitToMove):
        stepper_num = 0
        dpiStepper0.moveToRelativePositionInMillimeters(stepper_num, mm, waitToMove)
        self.pos_right_horizontal += mm

    def moveLeftCradle(self, mm, waitToMove):
        stepper_num = 0
        dpiStepper1.moveToRelativePositionInMillimeters(stepper_num, mm, waitToMove)
        self.pos_left_horizontal += mm

    def moveUp(self, dpistepper, mm, waitToMove):
        stepper_num = 1
        dpistepper.moveToRelativePositionInMillimeters(stepper_num, mm, waitToMove)
        if dpistepper == dpiStepper0:
            self.pos_right_vertical += mm
        if dpistepper == dpiStepper1:
            self.pos_left_vertical += mm

    def moveDown(self, dpistepper, mm, waitToMove):
        stepper_num = 1
        dpistepper.moveToRelativePositionInMillimeters(stepper_num, mm, waitToMove)
        if dpistepper == dpiStepper0:
            self.pos_right_vertical += mm
        if dpistepper == dpiStepper1:
            self.pos_left_vertical += mm

    def resetCradles(self):
        horizontalstepper_num1 = 0
        horizontalstepper_num2 = 0
        verticalstepper_num1 = 1
        verticalstepper_num2 = 1

        # stepperStatus = dpiStepper.getStepperStatus(0)
        # print(f"Pos = {stepperStatus}")

        # home = array('b', [True, False])

        # if not home[3] = True:

        dpiStepper1.moveToRelativePositionInMillimeters(verticalstepper_num1, - + self.pos_right_vertical, False)
        sleep(.5)
        dpiStepper0.moveToRelativePositionInMillimeters(horizontalstepper_num2, - + self.pos_right_horizontal, False)
        sleep(.5)
        dpiStepper1.moveToRelativePositionInMillimeters(horizontalstepper_num1, - + self.pos_left_horizontal, False)
        sleep(.5)
        dpiStepper0.moveToRelativePositionInMillimeters(verticalstepper_num2, - + self.pos_left_vertical, True)
        sleep(.5)

        self.sethome()
        self.speed_reset()

    def speed_reset(self):
        # reset speeds on each motor
        dpiStepper0.setSpeedInMillimetersPerSecond(0, speed_in_mm_per_sec)
        dpiStepper0.setSpeedInMillimetersPerSecond(1, speed_in_mm_per_sec)
        dpiStepper1.setSpeedInMillimetersPerSecond(0, speed_in_mm_per_sec)
        dpiStepper1.setSpeedInMillimetersPerSecond(1, speed_in_mm_per_sec)

    def grabFirstBallRight(self):
        if self.stopballs:
            self.stopballs = False
            move_to_second()
            self.moveRightCradle(230.5875, True)
            self.moveUp(dpiStepper0, 50, True)
            self.moveRightCradle(-230.5875, True)
            self.moveDown(dpiStepper0, -50, True)
            sleep(0.1)
        else:
            self.stopBallMovement()



    def grabSecondBallRight(self):
        if self.stopballs:
            self.stopballs = False
            move_to_second()
            self.moveRightCradle(345, True)
            self.moveUp(dpiStepper0, 50, True)
            self.moveRightCradle(-220, True)
            self.moveDown(dpiStepper0, -50, True)
            self.moveRightCradle(-125, True)
            sleep(0.1)
        else:
            self.stopBallMovement()


    def grabThirdBallRight(self):
        if self.stopballs:
            self.stopballs = False
            move_to_second()
            self.moveRightCradle(461, True)
            self.moveUp(dpiStepper0, 50, True)
            self.moveRightCradle(-215, True)
            self.moveDown(dpiStepper0, -50, True)
            self.moveRightCradle(-246, True)
            sleep(0.1)
        else:
            self.stopBallMovement()


    def grabFirstBallLeft(self):
        if self.stopballs:
            self.stopballs = False
            move_to_second()
            self.moveLeftCradle(223, True)
            self.moveUp(dpiStepper1, 50, True)
            self.moveLeftCradle(-223, True)
            self.moveDown(dpiStepper1, -50, True)
            sleep(0.1)
        else:
            self.stopBallMovement()

    def grabSecondBallLeft(self):
        if self.stopballs:
            self.stopballs = False
            move_to_second()
            self.moveLeftCradle(336, True)
            self.moveUp(dpiStepper1, 50, True)
            self.moveLeftCradle(-220, True)
            self.moveDown(dpiStepper1, -50, True)
            self.moveLeftCradle(-116, True)
            sleep(0.1)
        else:
            self.stopBallMovement()

    def stopBallMovement(self):
        self.stopballs = True
        # The balls are closer to the left cradle -- resulting in the cradles needing to move different distances.
        move_to_second()
        self.moveUp(dpiStepper0, 60, False)
        self.moveUp(dpiStepper1, 60, True)
        self.moveRightCradle(127.5, False)
        self.moveLeftCradle(117, True)
        sleep(1.5)
        self.moveRightCradle(-10, False)
        self.moveLeftCradle(-10, True)
        self.moveDown(dpiStepper1, -60, False)
        self.moveDown(dpiStepper0, -60, True)
        self.moveRightCradle(-117.5, False)
        self.moveLeftCradle(-107, True)
        sleep(0.1)

    def child_proof(self):
        countdown(int(0.00001))  # 9 seconds before you can press another button

    def quit(self):
        print("Exit")
        MyApp().stop()


class SecondWindow(Screen):

    def quit(self):
        print("Exit")
        MyApp().stop()


Builder.load_file('main.kv')
sm.add_widget(MainScreen(name='main'))
sm.add_widget(SecondWindow(name='second'))
# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////
MyApp().run()
