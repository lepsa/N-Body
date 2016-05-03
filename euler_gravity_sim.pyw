#!/bin/env python3
## This program implements a very basic 2D gravity sim using Euler methods.

import random
import time
import tkinter as tk
import math

## Holds the mass, positition and velocity data of every body.
class Point:
    def __init__(self, xPos, yPos, xPos2, yPos2, xAccel, yAccel, mass, xScale, yScale, colour):
        self.xPos = xPos
        self.yPos = yPos
        self.xPos2 = xPos2
        self.yPos2 = yPos2
        self.xAccel = xAccel
        self.yAccel = yAccel
        self.mass = mass
        self.colour = colour
        self.xScale = xScale
        self.yScale = yScale

    ## Applies the velocity of the point to the points position to simulate movement.
    ## Could be moved into Field to unify the functions.
    def move(self, dt):
          xTemp = self.xPos
          yTemp = self.yPos
          self.xPos += self.xPos - self.xPos2 + (self.xAccel * dt * dt)
          self.yPos += self.yPos - self.yPos2 + (self.yAccel * dt * dt)
          self.xPos2 = xTemp
          self.yPos2 = yTemp

## Contains all of the points in the system, and performs all attraction / acceleration calculations
class Field:
    dt = 0.1
    G = 6.67 * (10**-10)
    colour = ['#ff0000','#ffff00','#00ff00','#00ffff','#0000ff','#ffffff'] #Colours for planets!
    mStar = 10**13 #Mass of central body

    ## Creates n random points in (x, y) range
    def __init__(self, numPoints, xScale, yScale):
        ## Create an empty array of the correct size. Stops the runtime having to move potentially very large arrays.
        self.pointArray = [None] * numPoints
        self.xScale = xScale
        self.yScale = yScale
        for i in range(len(self.pointArray)):
            ## Set the array to have a collection of random points scatered in the center of the window.
            pos = self.calcPolarCoord(xScale, yScale, 1/4) ##position of the point
            mRand = (random.random() * 10)**11      ##mass of the point
            colour = Field.colour[random.randint(0,5)]
            vel = self.calcInitVel(pos[0], pos[1], xScale, yScale, Field.G, Field.mStar, pos[2])
            self.pointArray[i] = Point(pos[0], pos[1], pos[0] - vel[0], pos[1] - vel[1], 0, 0, mRand, xScale, yScale, colour)
#        self.pointArray.append(Point(xScale / 2, yScale / 2, xScale / 2, yScale / 2, 0, 0, Field.mStar, xScale, yScale, 'yellow'))

    def calcPolarCoord(self, xScale, yScale, rScale):
        ##calculate a radius and angle then return cartesian coordinates, offset to centre of canvas
        ##the radius is modified by rScale to cover various amounts of canvas.
        rRand = random.random() * rScale
        aRand = random.random() * 2 * math.pi
        xPos = (xScale * (rRand * math.cos(aRand))) + xScale/2
        yPos = (yScale * (rRand * math.sin(aRand))) + yScale/2
        ##Calculates the radius from the center of the canvas
        r = math.hypot((xPos - xScale/2), (yPos - yScale/2)) + random.randrange(10)
        return [xPos, yPos, r]

    def calcInitVel(self, xPos, yPos, xScale, yScale, G, mStar, r):
        ## Calculate initial velocities for circular orbits at the current point position.
        ## Assumes mass of point is smaller than the mass of the central star (mStar).
        direction = 1
        if random.randrange(2) == 0:
            direction = -1
        xVel = direction * (-(yPos - yScale/2) / r) * (G * mStar / r)**.5
        yVel = direction * ((xPos - xScale/2) / r) * (G * mStar / r)**.5
        xVel = random.randrange(-1, 2)
        yVel = random.randrange(-1, 2)
        return [xVel * self.dt, yVel * self.dt]
        
    def mergePoints(self, p1, p2):
        cMass = p1.mass + p2.mass
        p1Ratio = p1.mass / cMass
        p2Ratio = p2.mass / cMass
        p = Point(
            (p1.xPos * p1Ratio + p2.xPos * p2Ratio),
            (p1.yPos * p1Ratio + p2.yPos * p2Ratio),
            (p1.xPos2 * p1Ratio + p2.xPos2 * p2Ratio),
            (p1.yPos2 * p1Ratio + p2.yPos2 * p2Ratio),
            (p1.xAccel * p1Ratio + p2.xAccel * p2Ratio),
            (p1.yAccel * p1Ratio + p2.yAccel * p2Ratio),
            cMass,
            p1.xScale,
            p1.yScale,
            p1.colour
        )
        return p


    def update(self):
        ## Loop over every point
        for i in range(len(self.pointArray)):
            pi = self.pointArray[i]
            if pi != None:
                pi.xAccel = 0
                pi.yAccel = 0
                for j in range(len(self.pointArray)):
                    pj = self.pointArray[j]
                    if i == j or pj == None:
                        pass
                    else:
                        ## Calculate the distance between two points, how much force there is between them, and then the
                        ## resulting x and y velocities that need to be added to the point.
                        dist = Field.calcDist(pi.xPos, pi.yPos, pj.xPos, pj.yPos)
                        r = max(((pi.mass)**(1/3))/2000 + ((pj.mass)**(1/3))/2000, 1)
                        if dist <= r:
                          self.pointArray[i] = self.mergePoints(pi, pj)
                          self.pointArray[j] = None
                        else:
                           ## Calculate values against every other point, but not for a point against itself.
                          force = Field.calcForce(pi.mass, pj.mass, dist)
                          pi.xAccel += Field.calcAccl(pi.mass, force, dist, pi.xPos, pj.xPos)
                          pi.yAccel += Field.calcAccl(pi.mass, force, dist, pi.yPos, pj.yPos)
                ## Move the point once all of the forces have been applied to it.
                pi.move(self.dt)
        ## Make a deep copy of the temp array to the instance array so that it can be used for drawing and future iteration.
        #self.pointArray = [x for x in workArray if x != None]

    def calcDist(x1, y1, x2, y2):
        ## calculate the absolute differences of the points
        ## and then the distance between them using a^2 + b^2 = c^2
        return math.hypot(abs(x1 - x2), abs(y1 - y2))

    def calcForce(m1, m2, r):
        ## calculate the force betweem points using Newtonion Gravitation, returns 0 in case of errors such as divide by 0.
        try:
            temp = Field.G * ((m1 * m2)/(r**2))
        except:
            temp = 0
        return temp

    ## Calculate the acceleration of a point using Newtonion Mechanics, returns 0 in case of errors such as divide by 0.
    ## The acelleration is calculated in one plane, x or y, hence needing both positions of the points and the distance
    ## between them
    def calcAccl(m, f, r, x1, x2):
        try:
            temp = (((x2 - x1) / r) * f) / m
        except:
            temp = 0
        return temp

class Draw():
    ## Create the window and field.
    def __init__(self, master, numPoints):
        self.width = 700
        self.height = 700
        self.progress = None
        self.field = Field(numPoints, self.width, self.height)
        self.canvas = tk.Canvas(master, width = self.width, height = self.height, background = 'black')
        self.canvas.pack()

    ## For every point in the field, draw a circle at its co-ordinates.
    def drawFrame(self):
        for i in range(len(self.field.pointArray)):
            p = self.field.pointArray[i]
            if p != None:
              ## Calculate the drawn radius of each point
              r = ((p.mass)**(1/3))/2000
              x = p.xPos
              y = p.yPos
              colour = p.colour
              ## Draw each oval centered on the point co-ords.
              self.canvas.create_oval(x-r, y-r, x+r, y+r, fill = colour, outline = colour)
#              self.canvas.create_text(self.width/2, 10, fill='white', text=self.progress)
#              self.canvas.create_text(self.width/2, 25, fill='white', text='Press \'r\' to reset')
              ## Update the canvas, otherwise nothing will be visible because
              ## TK will wait until the program is out of a function to update the GUI by default.
        self.field.update()

class Application():
    def __init__(self):
        self.numObjects = 100
        self.root = tk.Tk()
        self.d = Draw(self.root, self.numObjects)
        self.i = 1
        self.root.bind('<Key>', self.reset)
        self.root.after(1, self.runSim)
        self.root.mainloop()

    ## Run the simulation. Used in call-backs from tkinter.
    def runSim(self):
        while True:
            self.d.progress = ('frame ' + str(self.i));
            self.i += 1
            self.d.canvas.delete('all')
            self.d.drawFrame()
            self.d.canvas.update()
            #time.sleep(1/60)
        self.d.canvas.destroy()

    ## Used to reset the simulation (new simulation).
    def reset(self, event):
        char = repr(event.char)
        if 'r' in char:
            print('Reset!')
            self.d.canvas.destroy()
            self.i = 1
            self.d = Draw(self.root, self.numObjects)

a = Application()
