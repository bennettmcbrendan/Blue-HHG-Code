# general imports
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from statistics import mean
import time
from newportxps import NewportXPS
import u6

# imports for figure imbed
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk 
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
        NavigationToolbar2Tk(self.canvas,toolbar_frame)


    def createWidgets(self):

        # Max current setting - for conversion
        self.maxamps = tk.Label(self,text = 'Max of picoammeter range (A)')
        self.maxamps.grid(row = 1,column = 0)
        
        # Max current entry
        self.mavalue = tk.Entry(self)
        self.mavalue.grid(row = 1,column = 1,columnspan = 2)
        
        # DataQuant Label
        self.dataquant = tk.Label(self,text = 'Number of measurements to make (integer)')
        self.dataquant.grid(row = 2,column = 0)
        
        # DataQuant Entry
        self.dqvalue = tk.Entry(self)
        self.dqvalue.grid(row = 2,column = 1,columnspan = 2)

        # DataFreq Label
        self.datafreq = tk.Label(self, text = 'Time between measurements (s)')
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
        self.datares = tk.Label(self,text = 'Resolution Index (recommend 8)')
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
        
        # Filename Label
        self.filename = tk.Label(self,text = 'csv filename for scan results (rel to current dir)')
        self.filename.grid(row = 8,column = 0)

        # Filename Entry
        self.fnvalue = tk.Entry(self)
        self.fnvalue.grid(row = 8,column = 1,columnspan = 2)

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

        i = 1
        
        while i <= int(self.dqvalue.get()):

            time.sleep(float(self.dfvalue.get()))
            self.figdata_x.append(i)
            # voltage measurement as AIN port 0 minus GND port 15
            # gainIndex set to x1
            self.figdata_z.append(labjack.getAIN(positiveChannel = 0, resolutionIndex=int(self.drvalue.get()), 
                                                 gainIndex=0, settlingFactor=int(self.dsvalue.get())) -
                                  labjack.getAIN(positiveChannel = 15, resolutionIndex=int(self.drvalue.get()), 
                                                 gainIndex=0, settlingFactor=int(self.dsvalue.get())))
    
            self.figdata_y.append(self.figdata_z[i-1] / float(self.mavalue.get()))
            
            i = i+1
            
            if i%10 == 0:
                self.update()
     
        self.update()
               
        self.scandata = pd.DataFrame({'Measurement':self.figdata_x,
                                    'Voltage (V)':self.figdata_z,
                                    'Ampere (A)':self.figdata_y})
    
        self.scandata.to_csv(self.fnvalue.get(),index = False)

# Run the GUI
app = Application()
app.master.title('Blue Driven Flux Program')
ani = animation.FuncAnimation(app.figure, app.animate,fargs = ('arg',), interval=1000)
app.mainloop()
