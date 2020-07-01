import csv
import sys
import argparse
import time
import numpy as np
from collections import deque
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets, uic
import os
from pyqtgraph import PlotWidget, plot

import max30101
import dataLogger

from time import sleep
from datetime import datetime
#from gpiozero import Button  # A button is a good approximation for what we need, a digital active-low trigger
import RPi.GPIO as GPIO
from statemachine import StateMachine, State

###########################
#Configurable parameters
###########################

BUFF_SIZE = 250
UPDATE_DELAY = 1  #update period in seconds
DISP_LENGTH = 100
SPO2_AVERAGING = 5



#################################
#   Setup PI environment
#################################
GPIO.setmode(GPIO.BCM) 





###########################
# Initialise variables
###########################


spo2_store = np.zeros(DISP_LENGTH,dtype=float)
spo2_smooth_store = np.zeros(DISP_LENGTH,dtype=float)
increment = 2.6e05

ptr = -DISP_LENGTH                      # set first x position

readPos = 0
    



#############################
# QT Window
#############################

class MainWindow(QtWidgets.QMainWindow):

    dl = None 

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('mainWindow.ui', self)
        self.btnStart.clicked.connect(self.startButtonClick)
        self.dl = dataLogger.dataLogger(max30101.MAX30101())
        
        
    def startButtonClick(self):
        if self.dl.is_wait:
            self.dl.start()
        elif self.dl.is_run:
            self.dl.stop()





##############################
### QtApp Initialisation #####
##############################

app = QtWidgets.QApplication(sys.argv)
main = MainWindow()


rawPen = pg.mkPen(color=(0, 120, 0))   #set up the line colour
raw_curve = main.graphWidget.plot(pen=rawPen)           # create an empty "plot" (a curve to plot)

smoothPen = pg.mkPen(color=(255, 255, 0), width=2)
smooth_curve = main.graphWidget.plot(pen=smoothPen)        

main.graphWidget.setYRange(50, 100, padding=0)
main.graphWidget.showGrid(x=False, y=True, alpha=0.5)


main.show()




##############################
### QtApp functions      #####
##############################

def updatePlt():
    global spo2_store, ptr, raw_curve, spo2_smooth_store, smooth_curve, main
    spo2 = 0
    if main.dl.is_run:
        dc_red = np.mean(main.dl.buff_red)
        dc_ir = np.mean(main.dl.buff_ir)
        ac_red = np.max(main.dl.buff_red) - np.min(main.dl.buff_red)
        ac_ir = np.max(main.dl.buff_ir) - np.min(main.dl.buff_ir)
        if not (ac_red ==0 or dc_red ==0 or ac_ir ==0 or dc_ir ==0) and np.mean(main.dl.buff_red[-10:]) > 10000:
            spo2 = 104 - 17.0*((ac_red/dc_red)/(ac_ir/dc_ir))
        print(dc_red,dc_ir,ac_red,ac_ir,spo2)
        
        spo2_store = np.roll(spo2_store,-1)
        spo2_store[-1] =  spo2
        spo2_smooth = np.mean(spo2_store[-SPO2_AVERAGING:-1])
        spo2_smooth_store = np.roll(spo2_smooth_store,-1)
        spo2_smooth_store[-1] = spo2_smooth
        
        
        ptr += 1                              # update x position for displaying the curve
        raw_curve.setData(spo2_store)                     # set the curve with this data
        smooth_curve.setData(spo2_smooth_store)                     
        raw_curve.setPos(ptr,0)                   # set x position in the graph to 0
        smooth_curve.setPos(ptr,0)      
        if spo2 ==0:
            main.lblSpo2.setText ('--')
        else:
            main.lblSpo2.setText (str(int(round(spo2)))  + "%" )
        
    else:
        main.lblSpo2.setText('--')
        ptr = -DISP_LENGTH
        spo2_store = np.zeros(DISP_LENGTH,dtype=float)
        spo2_smooth_store = np.zeros(DISP_LENGTH,dtype=float)
            
    QtGui.QApplication.processEvents()    # you MUST process the plot now
    



GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.add_event_detect(26, GPIO.FALLING, callback=main.dl.read_data)



timer  = pg.QtCore.QTimer()
timer.timeout.connect(updatePlt)
timer.start(UPDATE_DELAY*1000)





##################
### END QtApp ####
##################
if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

main.dl.quit()

