import csv 
import numpy as np
import max30101
from statemachine import StateMachine, State
from datetime import datetime
import os

###########################
#Configurable parameters
###########################

BUFF_SIZE = 250
DATA_DIR = 'data'



##############################
### State machine        #####
##############################

class dataLogger(StateMachine):
    
    wait = State('Wait',initial=True)
    run = State('Run')
    exiting = State('Exit')

    
    start = wait.to(run)
    stop = run.to(wait)
    quit = exiting.from_(wait,run)
    
    buff_red = np.zeros(BUFF_SIZE,dtype=float)
    buff_ir = np.zeros(BUFF_SIZE,dtype=float)
    buff_green = np.zeros(BUFF_SIZE,dtype=float)
    
    csvfile = None
    #used? #mode = max30101.MAX30101_MODE_SPO2
    max = None
    
    
    
    def __init__(self, ppgHandle):
        # create an instance of the MAX30101 class
        try:
        
            self.max = ppgHandle
            # start a thread that reads and process raw data from the sensor
            self.max.set_fifo_afv(15) #set fifo almost full value to max to minimise number of reads 
            self.max.enable_interrupt(sources=["full"])  # Set up a trigger to fire when the FIFO buffer (on the MAX30100) fills up.
            os.makedirs(DATA_DIR, exist_ok=True)
            
        except Exception as e:
            print(e)
        super(StateMachine, self).__init__()
    
    
    
    def on_enter_run(self):
        
        #open file & set datawriter
        
        print("starting a recording")
        
        now = datetime.now()
        filename = DATA_DIR + '/' + now.strftime("%d-%m-%Y_%H-%M-%S") + ".csv"
        self.csvfile = open(filename,'a')
        self.datawriter = csv.writer(self.csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        #clear variables
        self.buff_red = np.zeros(BUFF_SIZE,dtype=float)
        self.buff_ir = np.zeros(BUFF_SIZE,dtype=float)
        self.buff_green = np.zeros(BUFF_SIZE,dtype=float)
        
        
        #start max30101
        self.max.init()
        self.max.set_fifo_afv(15) #set fifo almost full value to max to minimise number of reads 
        self.max.enable_interrupt(sources=["full"])  # Set up a trigger to fire when the FIFO buffer (on the MAX30100) fills up.
        #TODO change button label
        
        
        
    def on_exit_run(self):
        print("ending a recording")
        #stop max30101
        #close file
        #change button label
        self.max.shutdown()
        self.csvfile.close()
        self.buff_red = np.zeros(BUFF_SIZE,dtype=float)
        self.buff_ir = np.zeros(BUFF_SIZE,dtype=float)
        self.buff_green = np.zeros(BUFF_SIZE,dtype=float)
        
    
    def on_exiting(self):
        pass
        
    
    def read_data(self, source):
        
        data_red = []
        data_ir = []
        data_green = []
        
        interrupts = self.max.read_triggered_interrupt()
        #print(interrupts)
        
        #when fifo almost_full is triggered there should be at least 17 samples from each active LED 
        
        if self.max.led_mode == max30101.MAX30101_MODE_HR:
            raw = self.max.read_raw_samples(17*3)
            rawArray = np.asarray(raw)
            for i in range(int(len(rawArray)/3)):
                data_red.append(rawArray[i*3]*65536 + rawArray[i*3+1]*256 + rawArray[i*3+2]) #TODO could be written more elegantly...
                
        elif self.max.led_mode == max30101.MAX30101_MODE_SPO2:
            raw = self.max.read_raw_samples(17*3*2)
            rawArray = np.asarray(raw)
            for i in range(int(len(rawArray)/6)):
                data_red.append(rawArray[i*6]*65536 + rawArray[i*6+1]*256 + rawArray[i*6+2])
                data_ir.append(rawArray[i*6+3]*65536 + rawArray[i*6+4]*256 + rawArray[i*6+5])
                
        else : 
            raw = self.max.read_raw_samples(17*3*3)
            rawArray = np.asarray(raw)
            for i in range(int(len(rawArray)/9)):
                data_red.append(rawArray[i*9]*65536 + rawArray[i*9+1]*256 + rawArray[i*9+2])
                data_ir.append(rawArray[i*9+3]*65536 + rawArray[i*9+4]*256 + rawArray[i*9+5])
                data_green.append(rawArray[i*9+6]*65536 + rawArray[i*9+7]*256 + rawArray[i*9+8])
        
        
        #pad the lists to the same length
        if len(data_ir) < len(data_red):
            data_ir.extend([0]*len(data_red))
        if len(data_green) < len(data_red):
            data_green.extend([0]*len(data_red))    
        #print(data_red)
        #print(data_ir)
        #print(data_green)

        
        for i in range(len(data_red)):
            self.datawriter.writerow([data_red[i] ,data_ir[i] ,data_green[i]])
            self.buff_red = np.roll(self.buff_red,-1)
            self.buff_ir = np.roll(self.buff_ir,-1)
            self.buff_green = np.roll(self.buff_green,-1)
            
            self.buff_red[-1] = data_red[i]
            self.buff_ir[-1] = data_ir[i]
            self.buff_green[-1] = data_green[i]
