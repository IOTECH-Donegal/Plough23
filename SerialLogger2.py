""""
Main routine for Serial Mux
Forked from the Comm module of SD-Node
Takes two serial inputs and logs them.
Optionally, forward to a UDP address:port
Tested with Python >=3.6
By: JOR
    v0.1    26APR20     First go!
    v0.2    24MAY20     Removed all complexity, threading, etc.
    v0.3    06JUN20	    Modified as a single serial logger
    v0.4    20FEB23     Rewroked as dredge monitor
"""

from datetime import datetime
import sys
import serial
import csv

# Create the log file
def nmealogfilename():
    now = datetime.now()
    return '%0.4d%0.2d%0.2d-%0.2d%0.2d%0.2d.nmea' % \
                (now.year, now.month, now.day,
                 now.hour, now.minute, now.second)


# Create the log file and open it
output_filename = nmealogfilename()
output_file = open(output_filename, 'a', newline='')
writer = csv.writer(output_file)
header = ['Date','Time','Latitude','Longitude','SOG','COG','Strain']
writer.writerow(header)

# Configure the first serial port, this should be the master GPS
# U-Blox connected directly should be ttyACM0
Serial_Port1 = serial.Serial(
    port='COM7',
    #port='/dev/ttyACM0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    rtscts=True,
    dsrdtr=True,
    timeout=1
)
Serial_Port1.flushInput()

# Configure the second serial port
# A RS232-USB dongle should be ttyUSBx
Serial_Port2 = serial.Serial(
    port='COM6',
    #port='/dev/ttyS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    rtscts=True,
    dsrdtr=True,
    timeout=.1
)
Serial_Port2.flushInput()

# Main Loop
try:
    print("press [ctrl][c] at any time to exit...")
    while True:
        # Receive data from serial link 1
        read_buffer1 = Serial_Port1.readline().decode('ascii', errors='replace')
        read_buffer2 = Serial_Port2.readline().decode('ascii', errors='replace')
        Serial_Port2.flushInput()

        try:
            nmea = str(read_buffer1)
            rmc = nmea.split(',')
            # Check for valid sentence
            if rmc[2] == 'A':               
                latitude = round((float(rmc[3][:2]) + float(rmc[3][2:]) / 60), 7)
                if rmc[4] == 'S':
                    latitude = -latitude
                longitude = round((float(rmc[5][:3]) + float(rmc[5][3:]) / 60),7)
                if rmc[6] == 'W':
                    longitude = -longitude              
                if rmc[7] != "":
                    SOG = float(rmc[7])
                else: 
                    SOG = 0                
                if rmc[8] != "":
                    COG = float(rmc[8])
                else:
                    COG = 0               
                nowtime = str(rmc[1][0:6])
                nowdate = str(rmc[9])               
                data = nowdate, nowtime, latitude, longitude, SOG, COG, read_buffer2.strip()
                print(nowdate, nowtime, latitude, longitude, SOG, COG, read_buffer2.strip())
            else:
                print(f"NMEA not valid: {nmea.strip()}")

            # Write CSV data
            writer.writerow(data)
        
        except Exception as error:
            print("Main loop error: ", sys.exc_info()[0])
            print(nmea)      

except KeyboardInterrupt:
    print("\n" + "Caught keyboard interrupt, exiting")
    exit(0)
finally:
    print("Exiting Main Thread")
    exit(0)
