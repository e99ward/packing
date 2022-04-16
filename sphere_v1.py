# hard sphere packing
# v1. random positioning
# with periodic boundary conditions

import numpy as np
#import pandas as pd
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

np.random.seed(1)
#initialize the system
L = 1 #length of box
N = 500 #number of particles in a box
phi = np.asarray([0.2,0.45]) #packing fractions
#calculating the particle diameters so that we get the right density and packing fractions
d = (phi[1]*6/(N*math.pi))**(1/3)
#d=0.12 (approx)
rho = N/(L**3) #number density

#intitalize box
box = np.random.uniform(0,1,(N, 3))

#simulation 1
diameter = d #tolerance
#check if box is valid

#this is a collection of loops to check if the particles we have placed are
#not overlapping
#we place i = 0 particle, no problem
#then we place the other particles, and we check with all the previously placed particles if
#the placement is okay or not

for i in range(1,N):
    mybool=True
    print("particles in box: " + str(i))
    while (mybool): #the deal with this while loop is that if we place a bad particle, we need to change its position, and restart the process of checking
        for j in range(0,i):
            displacement=box[j,:]-box[i,:]
            for k in range(3):
                if abs(displacement[k])>L/2:
                    displacement[k] -= L*np.sign(displacement[k])
            distance = np.linalg.norm(displacement,2) #check distance between ith particle and the trailing j particles
            if distance<diameter:
                box[i,:] = np.random.uniform(0,1,(1,3)) #change the position of the ith particle randomly, restart the process
                break
            if j==i-1 and distance>diameter:
                mybool = False
                break
#print(np.linalg.norm(box[0,:]-box[119,:]))
#test script to check if the above generated a sound configuration worked or not
for i in range(1,N):
    for j in range(0,i):
        displacement=box[j,:]-box[i,:]
        for k in range(3):
            if abs(displacement[k])>L/2:
                displacement[k] -= L*np.sign(displacement[k])
        distance = np.linalg.norm(displacement,2) #check distance between ith particle and the trailing j particles
        if distance<diameter:
            print("this is bad")
##########