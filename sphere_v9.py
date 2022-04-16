# hard sphere packing
# Lubachevsky–Stillinger algorithm
# with periodic boundary conditions

import numpy as np
import math
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D

# for spheres
N = 100 # number of spheres (grains)
eventspercycle = 1 # events per particle per cycle
initialpf = 0.3
maxpf = 0.6
temp = 0 # initial temperature (temp=0 means v=0)
growthrate = 1
maxpressure = 1
# for container
SIZE = 1.0            #// size of box
VOLUMESPHERE = pow(PI,((double)(DIM))/2.)/exp(lgamma(1+((double)(DIM))/2.)) # volume prefactor for sphere
DBL_EPSILON = 2.2204460492503131e-016 #// smallest # such that 1.0+DBL_EPSILON!=1.0
M = 1.0
ngrids = 10 #;                    // number of cells in one direction
r = 1.0 #                      // radius, defined at gtime = 0
# statistics
pressure = 1.0 #;               // pressure
xmomentum = 1.0 #;              // exchanged momentum
pf = 1.0 #;                     // packing fraction
energy = 1.0 #;                // kinetic energy
energychange = 1.0 #;;
ncollisions = 1 #;               // number of collisions
ntransfers = 1 #;                // number of transfers
nchecks = 1 #;                   // number of checks
neventstot = 1 #;                // total number of events 
ncycles = 1 #;                   // counts # cycles for output
#grid_field<DIM, int> cells; // array that keeps track of spheres in each cell
#vector<DIM> *x;                 // positions of spheres.used for graphics

r = pow(initialpf*pow(SIZE, DIM)/(N*VOLUMESPHERE), 1.0/DIM))

box b(input.N, r, input.growthrate, input.maxpf);
  
  std::cout << "ngrids = " << b.ngrids << std::endl;
  std::cout << "DIM = " << DIM << std::endl;

  if(input.readfile[0])
    {
      std::cout << "Reading in positions of spheres" << std::endl;
      b.RecreateSpheres(input.readfile, input.temp);
    }
  else 
    {
      std::cout << "Creating new positions of spheres" << std::endl;
      b.CreateSpheres(input.temp);
    } 
  
  std::ofstream output(input.datafile);
  output.precision(16);  

  while ((b.pf < input.maxpf) && (b.pressure < input.maxpressure)) 
    {
      b.Process(input.eventspercycle*input.N);
      output << b.pf << " " << b.pressure << " " << 
	b.energychange << " " << b.neventstot << " " << std::endl;

      b.Synchronize(true);