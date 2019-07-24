#!/usr/bin/python
import numpy as np
import random
from scipy import optimize
import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import Pose, PoseArray
from Sensor_Dist_ROS.msg import sens as Data
from Sensor_Dist_ROS.msg import floatArray as floatArray
from Sensor_Dist_ROS.msg import floatArray2 as floatArray2
import turtlesim
from End import End
from Sensor import Sensor
import time

rospy.init_node('rosEnd1', anonymous = True)
global bigS,bounding_box,desiredPos,robot
bigS = Sensor()
bounding_box = np.array((0,1,0,1))
desiredPos = [np.array([float('nan'),float('nan')])]
robot = End(3,[.75,.75],bigS,time.time(),bounding_box)
def posesCallback(data):
    global desiredPos
    desiredPos = np.array([data.x,data.y])
def modelCallback(data):
    robot.p = data.p
def robot1Callback(data):
    robot.points[0,:] = [data.x,data.y]
def robot2Callback(data):
    robot.points[1,:] = [data.x,data.y]
def robot3Callback(data):
    robot.points[2,:] = [data.x,data.y]
# def localizationCallback(data): # Callback for localization data
#     robot.pos = data

def initialize():

    global desiredPos,robot
    rospy.Subscriber("/cloud/poses",floatArray2,posesCallback,queue_size=1)
    rospy.Subscriber("/edge/model",floatArray,modelCallback,queue_size=1)
    rospy.Subscriber("/robot1/data",Data,robot1Callback,queue_size=1)
    rospy.Subscriber("/robot2/data",Data,robot2Callback,queue_size=1)
    rospy.Subscriber("/robot3/data",Data,robot3Callback,queue_size=1)
    # rospy.Subscriber("/robot/localization",Float64[],loalizationCallback,queue_size=1) # The subscription to the ouput localication value goes here
    data = rospy.Publisher("/robot4/data",Data,queue_size=1,latch = True)
    rate = rospy.Rate(20)

    data.publish(robot.pos[0],robot.pos[1],robot.Sensor.sensor(robot.pos))

    while not rospy.is_shutdown():
        robot.points[3,:] = robot.pos
        if np.isnan(np.sum(desiredPos)):
            robot.updateVoronoi()
            centroid = robot.computeCentroid()
            robot.updatePosition(centroid)
        else:
            robot.pos = desiredPos[:,3]
        data.publish(robot.pos[0],robot.pos[1],robot.Sensor.sensor(robot.pos))
        rate.sleep()

if __name__ == '__main__':
    try:
        initialize()
    except rospy.ROSInterruptException:
        pass
