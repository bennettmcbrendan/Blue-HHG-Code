from datetime import datetime
import time
import u6


labjack = u6.U6()
labjack.getCalibrationData()

def check_sleep(amount):
    start = datetime.now()
    # time.sleep(amount)
    u6.WaitShort(amount*1000000/64)
    end = datetime.now()
    delta = end-start
    return delta.seconds + delta.microseconds/1000000.

error = sum(abs(check_sleep(0.10)-0.10) for i in range(100))*10
print("Average error is " + str(error) + " ms")
