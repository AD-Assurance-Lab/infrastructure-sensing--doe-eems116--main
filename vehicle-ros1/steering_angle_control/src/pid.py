#!/usr/bin/python

import numpy as np
import rospy

MAXSTEER = np.deg2rad(35)

class PID():

  def __init__(self, P, I, D):
    self.P = P
    self.I = I
    self.D = D
    
    self.Ki = 0.0
    self.De = 0.0

    self.initialized = False
    self.lower_bound = None
    self.upper_bound = None

  def set_limits(self, lower, upper):
    self.lower_bound = lower
    self.upper_bound = upper
    
  def set_values(self, p,i,d):
    
    self.P = p 
    self.I = i
    self.D = d 

  def control(self, error):

    if self.upper_bound is None and self.lower_bound is None:

      raise ValueError("PID limits are not set")

    else:

      if not self.initialized:
        self.initialized = True
        self.previous_time = rospy.Time.now().to_sec()

      self.current_time = rospy.Time.now().to_sec()

      dt = self.current_time - self.previous_time
      self.previous_time = self.current_time

      Kp = error*self.P
      self.Ki += error*dt
      Kd = (error - self.De)/dt
      self.De = error
      
      # print("P: {}, I: {}, D: {}".format(Kp, self.Ki, Kd))

      return np.clip(Kp + self.Ki*self.I + Kd*self.D, self.lower_bound, self.upper_bound)
