# general imports
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from statistics import mean
from datetime import datetime
import u6

# imports for figure imbed
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure, Axes

# imports for figure animation
import matplotlib.animation as animation

# define labjack objects
labjack = u6.U6()
labjack.getCalibrationData()


class Application(tk.Frame):


    def __init__(self, master=None):

        super(Application, self).__init__(master)
        
        # will use tkinter grid method to format gui
        self.grid()  

        # define AINvalue variable to track latest voltage reading
        self.AINvalue = tk.StringVar()
        self.EstFreqValue = tk.StringVar()
    
        # define figure
        self.figdata_x = [1,2,3,4,5]
        self.figdata_y = [1,2,3,4,5]
        self.figdata_z = [1,2,3,4,5]
        self.figure = Figure(figsize=(10,5), dpi=100)
        self.figsubplot = self.figure.add_subplot(111)
        self.figsubplot.plot(self.figdata_x,self.figdata_y)
        self.figsubplot.set_xlabel('Measurement')
        self.figsubplot.set_ylabel('Current (A)')
        
        # run functions below
        self.plotFigure()
        self.createWidgets()

    def animate(self,i,j):

        self.figsubplot.clear()
        self.figsubplot.plot(self.figdata_x,self.figdata_y)
        self.figsubplot.set_xlabel('Measurement')
        self.figsubplot.set_ylabel('Current (A)')

    
    def plotFigure(self):

        self.canvas = FigureCanvasTkAgg(self.figure,master = self)
        self.canvas.get_tk_widget().grid(row=0, column=11, rowspan=10, columnspan=8, sticky=tk.E + tk.W + tk.N + tk.S)

        toolbar_frame = tk.Frame(self)
        toolbar_frame.grid(row = 11,column = 11,columnspan = 2,sticky = tk.W+tk.E)
        NavigationToolbar2TkAgg(self.canvas,toolbar_frame)


    def createWidgets(self):

        # Max current setting - for conversion
        self.maxamps = tk.Label(self,text = 'Max of picoammeter range (A)')
        self.maxamps.grid(row = 1,column = 0)
        
        # Max current entry
        self.mavalue = tk.Entry(self)
        self.mavalue.grid(row = 1,column = 1,columnspan = 2)
        
        # DataQuant Label
        self.dataquant = tk.Label(self,text = 'Data to take (mult of 600)')
        self.dataquant.grid(row = 2,column = 0)

        # DataQuant Entry
        self.dqvalue = tk.Entry(self)
        self.dqvalue.grid(row = 2,column = 1,columnspan = 2)

        # DataFreq Label
        self.datafreq = tk.Label(self, text = 'Stream Frequency (Hz)')
        self.datafreq.grid(row = 3,column = 0)

        # DataFreq Entry
        self.dfvalue = tk.Entry(self)
        self.dfvalue.grid(row = 3,column = 1,columnspan = 2)
        
        # DataSettle Label
        # MANUAL: "Auto" (0) ensures enough settling for any gain and resolution with source impedances less than at least 1 kohms
        self.datasettle = tk.Label(self,text = 'Settling Factor (recommend 0)')
        self.datasettle.grid(row = 4,column = 0)

        # DataSettle Entry
        self.dsvalue = tk.Entry(self)
        self.dsvalue.grid(row = 4,column = 1,columnspan = 2)
        
        # DataRes Label
        # can be 1-8, with 8 the highest resolution
        self.datares = tk.Label(self,text = 'Resolution Index (recommend 4)')
        self.datares.grid(row = 5,column = 0)

        # DataRes Entry
        self.drvalue = tk.Entry(self)
        self.drvalue.grid(row = 5,column = 1,columnspan = 2)

        # ReadAIN Button
        self.readAIN = tk.Button(self,text = 'Read single voltage',command = self.readAINCallback)
        self.readAIN.grid(row = 6,column = 0)

        # readAIN Entry
        self.readAINvalue = tk.Entry(self,textvariable = self.AINvalue)
        self.readAINvalue.grid(row = 6,column = 1)
        
        # StartScan Button
        self.startscan = tk.Button(self,text = 'Start Scan',command = self.startscanCallback)
        self.startscan.grid(row = 7,column = 0)
        
        # Est Freq Label
        self.estfreq = tk.Label(self,text = 'Estimated Scan Frequency (Hz)')
        self.estfreq.grid(row = 8,column = 0)

        # Est Freq Entry
        self.efvalue = tk.Entry(self,textvariable = self.EstFreqValue)
        self.efvalue.grid(row = 8,column = 1)
        
        # Filename Label
        self.filename = tk.Label(self,text = 'csv filename for scan results (rel to current dir)')
        self.filename.grid(row = 9,column = 0)

        # Filename Entry
        self.fnvalue = tk.Entry(self)
        self.fnvalue.grid(row = 9,column = 1,columnspan = 2)

    def readAINCallback(self):

        # Fuction to read a single AIN value from photodiode
        self.AINvalue.set(labjack.getAIN(positiveChannel = 0, resolutionIndex=int(self.drvalue.get()), 
                                                 gainIndex=0, settlingFactor=int(self.dsvalue.get())) -
                          labjack.getAIN(positiveChannel = 15, resolutionIndex=int(self.drvalue.get()), 
                                                 gainIndex=0, settlingFactor=int(self.dsvalue.get())))

    def startscanCallback(self):
                    
        self.figdata_x = [] # measurement index
        self.figdata_z = [] # voltage measurement
        self.figdata_y = [] # convert to current - goes on figure
        errorString = []
        
        labjack.streamConfig(NumChannels=2, ChannelNumbers=[0,15], ChannelOptions=[0,0], 
                             SettlingFactor=int(self.dsvalue.get()), ResolutionIndex=int(self.drvalue.get()), 
                             ScanFrequency=float(self.dfvalue.get()))
        
        # stop stream in case there is one ongoing
        if labjack.streamStarted:
            labjack.streamStop()
            
        self.scandata = pd.DataFrame()
   
        dataCount = 0
        packetCount = 0     
               
        labjack.streamStart()
        
        # code here directly from https://github.com/labjack/LabJackPython/blob/master/Examples/streamTest.py
        # we have 25 samples per packet and 48 packets per data request for a total of 1200 samples per data request
        self.starttime = datetime.now()
        
        for r in labjack.streamData():
            if r is not None:
                # Our stop condition
                if dataCount >= float(self.dqvalue.get()):
                    break

                if r["errors"] != 0:
                    errorString.append("Errors counted: %s ; %s\n" % (r["errors"], datetime.now()))

                if r["numPackets"] != labjack.packetsPerRequest:
                    errorString.append("----- UNDERFLOW : %s ; %s\n" % (r["numPackets"], datetime.now()))

                if r["missed"] != 0:
                    # missed += r['missed']
                    errorString.append("+++ Missed %s\n" % r["missed"])

                self.scandata = pd.concat([self.scandata,
                                        pd.DataFrame({
                                        'Data Request':dataCount,
                                        'Packets per Request':r['numPackets'],
                                        'AIN Voltage (V)':r['AIN0'],
                                        'GND Voltage (V)':r['AIN15']})])
                        
                dataCount += 1
                packetCount += r['numPackets']
            else:
                        # Got no data back from our read.
                        # This only happens if your stream isn't faster than the USB read
                        # timeout, ~1 sec.
                print("No data ; %s" % datetime.now())

        self.stoptime = datetime.now()
        self.delta = (self.stoptime-self.starttime).seconds + (self.stoptime-self.starttime).microseconds/1000000
        self.EstFreqValue.set(600*dataCount/self.delta)        
        
        labjack.streamStop() 
        
        self.figdata_x = list(range(len(self.scandata['Data Request'])))
        # Emma and I think that the GND is already subtracted out on the AIN0 reading
        self.figdata_z = self.scandata['AIN Voltage (V)'] # - self.scandata['GND Voltage (V)']
        # Keithley 6485 manual: ANALOG OUT provides a scaled, inverting ±2V output
        self.figdata_y = (self.figdata_z*(-1) + 2)/4 * float(self.mavalue.get())
        
        self.update()
        
        self.scandata['Voltage (V)'] = self.figdata_z                 
        self.scandata['Current (A)'] = self.figdata_y
        self.scandata.to_csv(self.fnvalue.get(),index = False)

# Run the GUI
app = Application()
app.master.title('Blue Driven Flux Program')
ani = animation.FuncAnimation(app.figure, app.animate,fargs = ('arg',), interval=1000)
app.mainloop()
