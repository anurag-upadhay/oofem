# -*- coding: iso-8859-1 -*-
# Author: Mikael Öhman
# License: CC0

from __future__ import print_function
from octree import *
import numpy as np
from itertools import product, combinations

# Generates non-overlaping inclusions in an periodic box.
def generateSphericalInclusions(minDensity, boxSize, minRadius, maxRadius, forcedDist, ndim, seed):
    np.random.seed(seed)
    tree = Octtree(ndim)
    inclusions = list()
    Volume = pow(boxSize,ndim)
    averageRadius = (minRadius + maxRadius)/2.
    if ndim == 3:
        averageVolume = 4./3. * np.pi * pow(averageRadius,3)
    elif ndim == 2:
        averageVolume = np.pi * pow(averageRadius,2)
    print("Volume =", Volume, "Average radius =", averageRadius, ", Average inclusion volume =", averageVolume, 
          ", expected number of spheres is", np.ceil(minDensity * Volume/averageVolume))
    volume = 0.
    ninc = 0
    miss = 0
    while volume < minDensity * Volume:
        # Generate an inclusion [radius followed by coordinate]
        r = np.random.uniform(minRadius, maxRadius)
        c = np.random.random(ndim) * boxSize
        # Check for overlaps, if so, skip and try again
        # Fetch all the inclusions in the vicinity:
        maxDist = r + forcedDist + maxRadius
        subInclusions = tree.getObjectsWithin(c - maxDist, c + maxDist)
        overlap = False
        for i in subInclusions:
            if np.dot(i[1] - c, i[1] - c) < (i[0] + r + forcedDist)**2:
                overlap = True
                break

        # Add it + any periodic copies
        if not overlap:
            inclusions.append( (r,c) )
            tree.insert( r, c )
            if ndim == 3:
                volume += 4./3. * np.pi * r * r * r
            elif ndim == 2:
                volume += np.pi * r * r
            else:
                print("Can't compute volume!")
            ninc += 1
            # Add periodic duplicates (this code generates some unnecessary duplicates in corners)
            for i in range(1,(1 << ndim) - 1):
                pos = [i >> k & 1 for k in range(ndim-1,-1,-1)]
                if all(c[np.array(pos) == 1] < r):
                    c2 = np.copy(c)
                    c2[np.array(pos) == 1] += boxSize
                    inclusions.append( (r,c2) )
                    tree.insert( r, c2 )
                if all(c[np.array(pos) == 1] > boxSize - r):
                    c2 = np.copy(c)
                    c2[np.array(pos) == 1] -= boxSize
                    inclusions.append( (r,c2) )
                    tree.insert( r, c2 )
            print("Number of inclusions = %d Density %.6f Misses = %d"%(ninc, volume / Volume, miss))
            miss = 0
        else:
            miss += 1
    return inclusions

# Takes out the inclusions which are within the box
def getInclusionsInBox(corner, boxSize, inclusions):
    intersectedInclusions = list()
    for inc in inclusions:
        ir = inc[0]
        ic = inc[1]
        # Check if sphere and cube intersects
        dmin = 0
        for i in range(0, corner.size):
            if ic[i] < corner[i]:
                dmin += (ic[i] - corner[i])**2
            elif ic[i] > (corner[i] + boxSize):
                dmin += (ic[i] - corner[i] - boxSize)**2
        if dmin <= (ir**2):
            intersectedInclusions.append(inc)
    return intersectedInclusions


#from mpl_toolkits.mplot3d import Axes3D
#import matplotlib.pyplot as plt

# Plots inclusions generated by generateSphericalInclusions
#def plotSphericalInclusions(inclusions, boxSize, ndim, drawAll=False):
#    if ndim == 2:
#        #fig = plt.figure()
#        # TODO
#        print("2d plotting not implemented yet")
#    elif ndim == 3:
#        fig = plt.figure()
#        ax = fig.gca(projection="3d")
#        ax.set_aspect("equal")
#        r = [0, boxSize]
#        for s, e in combinations(np.array(list(product(r,r,r))), 2):
#             if np.sum(np.abs(s-e)) == r[1]-r[0]:
#                ax.plot3D(*zip(s,e), color="b")
#
#        # A basic sphere:
#        u, v = np.mgrid[0:2*np.pi:30j, 0:np.pi:30j]
#        x=np.cos(u)*np.sin(v)
#        y=np.sin(u)*np.sin(v)
#        z=np.cos(v)
#
#        for i in inclusions:
#            radius = i[0]
#            center = i[1]
#            if drawAll or ( all(center < boxSize) and all(center > 0) ):
#                x2 = x*radius + center[0]
#                y2 = y*radius + center[1]
#                z2 = z*radius + center[2]
#                #ax.plot_wireframe(x2, y2, z2, color="r")
#                ax.plot_surface(x2, y2, z2, linewidth=0, shade=True, rstride=4, cstride=4, color="r")
#    else:
#        print("Only 2D and 3D plots are supported")
#    plt.show()
