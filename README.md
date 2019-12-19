#### Code for blue-driven HHG experiment in B1B35

### Overview: The picoammeter outputs analog voltage proportional to its amp measurement, which we read into computer using a DAQ card and convert back to amps

### Instuctions

# 1. Connect picoammeter analog output to labjack U6 with BNC. Connect USB from labjack to computer

# 2. Run master-gui.py - ideally in anaconda prompt but spyder or git bash (I was having trouble there with permissions) should work as well. A GUI should appear.

# 3. GUI buttons
- 'Read single voltage' button takes a single analog voltage measurement and displays the result
- 'Start scan' button scans a certain number of analog voltages according to:

# 4. GUI parameters
- Max of picoammeter range: max amp value which picoammeter can display (according to its settings). determines how we convert from volts back to amps
- Number of measurements to make: number of times to measure picoammeter voltage
- Time between measurements: number of seconds between measurements
- Settling Factor: waiting time at each measurement for transient currents (MANUAL: "Auto" (0) ensures enough settling for any gain and resolution with source impedances less than at least 1 kohms)
- Resolution Index: number of discrete voltages in DAQ card voltage range (recommend 8, which is maxed)
- csv filename for scan results: file to which to save scan results, ex. scan_results.csv (no quotes)
    
