import smbus
from time import time
import operator
import math
from LSM9DS0 import *
import datetime

class Imu(object):
    def __init__(self):
        # initialize bus
        self.bus = smbus.SMBus(1)
        # initialize sensors
        self.setupACC(); self.setupMAG(); self.setupGYR()
        # address mapping for all the sensors
        self.sensors = {
            'ACC': {'address': ACC_ADDRESS, 'x' :[OUT_X_L_A,OUT_X_H_A], 'y' :[OUT_Y_L_A,OUT_Y_H_A], 'z' :[OUT_Z_L_A,OUT_Z_H_A]},
            'MAG': {'address': MAG_ADDRESS, 'x' :[OUT_X_L_M,OUT_X_H_M], 'y' :[OUT_Y_L_M,OUT_Y_H_M], 'z' :[OUT_Z_L_M,OUT_Z_H_M]},
            'GYR': {'address': GYR_ADDRESS, 'x' :[OUT_X_L_A,OUT_X_H_G], 'y' :[OUT_Y_L_G,OUT_Y_H_G], 'z' :[OUT_Z_L_G,OUT_Z_H_G]}
        }

    def setupACC(self):
        #initialise the accelerometer
        self.bus.write_byte_data(ACC_ADDRESS, CTRL_REG1_XM, 0b01100111) #z,y,x axis enabled, continuos update,  100Hz data rate
        self.bus.write_byte_data(ACC_ADDRESS, CTRL_REG2_XM, 0b00100000) #+/- 16G full scale
    def setupMAG(self):
        #initialise the magnetometer
        self.bus.write_byte_data(MAG_ADDRESS, CTRL_REG5_XM, 0b11110000) #Temp enable, M data rate = 50Hz
        self.bus.write_byte_data(MAG_ADDRESS, CTRL_REG6_XM, 0b01100000) #+/-12gauss
        self.bus.write_byte_data(MAG_ADDRESS, CTRL_REG7_XM, 0b00000000) #Continuous-conversion mode
    def setupGYR(self):
        #initialise the gyroscope
        self.bus.write_byte_data(GYR_ADDRESS, CTRL_REG1_G, 0b00001111) #Normal power mode, all axes enabled
        self.bus.write_byte_data(GYR_ADDRESS, CTRL_REG4_G, 0b00110000) #Continuos update, 2000 dps full scale

    def _read(self, sensor, axis):
        acc_l = self.bus.read_byte_data(self.sensors[sensor]['address'], self.sensors[sensor][axis][0])
        acc_h = self.bus.read_byte_data(self.sensors[sensor]['address'], self.sensors[sensor][axis][1])
        acc_combined = (acc_l | acc_h <<8)
        return acc_combined  if acc_combined < 32768 else acc_combined - 65536

    def readACCx(self): return self._read('ACC','x')
    def readACCy(self): return self._read('ACC','y')
    def readACCz(self): return self._read('ACC','z')
    def readMAGx(self): return self._read('MAG','x')
    def readMAGy(self): return self._read('MAG','y')
    def readMAGz(self): return self._read('MAG','z')
    def readGYRx(self): return self._read('GYR','x')
    def readGYRy(self): return self._read('GYR','y')
    def readGYRz(self): return self._read('GYR','z')
    def readACC(self): return self.readACCx(),self.readACCy(),self.readACCz()
    def readMAG(self): return self.readMAGx(),self.readMAGy(),self.readMAGz()
    def readGYR(self): return self.readGYRx(),self.readGYRy(),self.readGYRz()
    def read(self): return self.readACC(), self.readMAG(), self.readGYR()

    def flat_heading(self, MAGx=None, MAGy=None):
        if MAGx is None or MAGy is None:
            # get reading on the fly if not provided
            MAGx, MAGy = self.readMAGx(), self.readMAGy()
        heading = 180 * math.atan2(MAGy,MAGx)/math.pi
        return heading + 360 if heading < 0 else heading

    def pitch_roll_heading(self, ACCx=None, ACCy=None, ACCz=None, MAGx=None, MAGy=None, MAGz=None):
        if reduce(operator.__or__,map(lambda x: x is None, [ACCx,ACCy,ACCz,MAGx,MAGy,MAGz])):
            ACCx,ACCy,ACCz = self.readACC()
            MAGx,MAGy,MAGz = self.readMAG()
        # Normalize accelerometer raw values.
        accXnorm = ACCx/math.sqrt(ACCx*ACCx + ACCy*ACCy + ACCz*ACCz)
        accYnorm = ACCy/math.sqrt(ACCx*ACCx + ACCy*ACCy + ACCz*ACCz)
        # Calculate pitch and roll
        pitch = math.asin(accXnorm)
        roll = -math.asin(accYnorm/math.cos(pitch))
        # Calculate the new tilt compensated values
        magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
        magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)
        # Calculate tilt compensated heading
        heading = 180 * math.atan2(magYcomp,magXcomp)/math.pi
        heading = heading + 360 if heading < 0 else heading
        return pitch, roll, heading

    def reading(self):
        ACCx,ACCy,ACCz = self.readACC()
        MAGx,MAGy,MAGz = self.readMAG()
        GYRx,GYRy,GYRz = self.readGYR()
        pitch,roll,heading = self.pitch_roll_heading(ACCx,ACCy,ACCz,MAGx,MAGy,MAGz)
        return time(),pitch,roll,heading,ACCx,ACCy,ACCz,MAGx,MAGy,MAGz,GYRx,GYRy,GYRz


if False:
    gyroXangle = 0.0
    gyroYangle = 0.0
    gyroZangle = 0.0
    CFangleX = 0.0
    CFangleY = 0.0

    #RAD_TO_DEG = 57.29578
    #G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
    #LP = 0.041    	# Loop period = 41ms.   This needs to match the time it takes each loop to run
    #AA =  0.80      # Complementary filter constant

    while True:
        a = datetime.datetime.now()
        #Read our accelerometer,gyroscope and magnetometer  values
        ACCx = readACCx();ACCy = readACCy();ACCz = readACCz()
        GYRx = readGYRx();GYRy = readGYRx();GYRz = readGYRx()
        MAGx = readMAGx();MAGy = readMAGy();MAGz = readMAGz()
        ##Convert Accelerometer values to degrees
        AccXangle =  (math.atan2(ACCy,ACCz)+math.pi)*RAD_TO_DEG
        AccYangle =  (math.atan2(ACCz,ACCx)+math.pi)*RAD_TO_DEG
        #Convert Gyro raw to degrees per second
        rate_gyr_x =  GYRx * G_GAIN
        rate_gyr_y =  GYRy * G_GAIN
        rate_gyr_z =  GYRz * G_GAIN
        #Calculate the angles from the gyro. LP = loop period
        gyroXangle+=rate_gyr_x*LP
        gyroYangle+=rate_gyr_y*LP
        gyroZangle+=rate_gyr_z*LP
        #Change the rotation value of the accelerometer to -/+ 180 and move the Y axis '0' point to up.
        #Two different pieces of code are used depending on how your IMU is mounted.
        #If IMU is upside down
        #if AccXangle >180:
        #        AccXangle -= 360.0
        #AccYangle-=90
        #if (AccYangle >180):
        #        AccYangle -= 360.0
        #If IMU is up the correct way, use these lines
        AccXangle -= 180.0
        if AccYangle > 90:
                AccYangle -= 270.0
        else:
            AccYangle += 90.0
        #Complementary filter used to combine the accelerometer and gyro values.
        CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
        CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle
        print ("\033[1;34;40mACCX Angle %5.2f ACCY Angle %5.2f\033[1;31;40m\tGRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f \033[1;35;40m    \tCFangleX Angle %5.2f \033[1;36;40m  CFangleY Angle %5.2f \33[1;32;40m  HEADING  %5.2f \33[1;37;40m tiltCompensatedHeading %5.2f\033[0m  " % (AccXangle, AccYangle,gyroXangle,gyroYangle,gyroZangle,CFangleX,CFangleY,heading,tiltCompensatedHeading))
        time.sleep(0.03)
        b = datetime.datetime.now()
        c = b - a
        print "Loop Time |",  c.microseconds/1000,"|",

