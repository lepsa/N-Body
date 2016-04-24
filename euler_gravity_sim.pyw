## This program implements a very basic 2D gravity sim using Euler methods.

import random
import time
import tkinter as tk
import math

## Holds the mass, positition and velocity data of every body.
class Point:
    def __init__(self, xPos, yPos, xVel, yVel, mass, xScale, yScale, colour):
        self.xPos = xPos
        self.yPos = yPos
        self.xVel = xVel
        self.yVel = yVel
        self.mass = mass
        self.colour = colour
        self.xScale = xScale
        self.yScale = yScale

    ## Applies the velocity of the point to the points position to simulate movement.
    ## Could be moved into Field to unify the functions.
    def move(self):
        self.xPos += self.xVel
        self.yPos += self.yVel

## Contains all of the points in the system, and performs all attraction / acceleration calculations
class Field:
    G = 6.67 * (10**-11)
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
            pos = self.calcPolarCoord(xScale, yScale, 1/4)  ##position of the point
            mRand = (random.random() * 10)**11              ##mass of the point
            colour = Field.colour[random.randint(0,5)]
            vel = self.calcInitVel(pos[0], pos[1], xScale, yScale, Field.G, Field.mStar, pos[2])
            self.pointArray[i] = Point(pos[0], pos[1], vel[0], vel[1], mRand, xScale, yScale, colour)
        self.pointArray.append(Point(xScale / 2, yScale / 2, 0, 0, Field.mStar, xScale, yScale, 'yellow'))

    def calcPolarCoord(self, xScale, yScale, rScale):
        ##calculate a radius and angle then return cartesian coordinates, offset to centre of canvas
        ##the radius is modified by rScale to cover various amounts of canvas.
        rRand = random.random() * rScale
        aRand = random.random() * 2 * math.pi
        xPos = (xScale * (rRand * math.cos(aRand))) + xScale/2
        yPos = (yScale * (rRand * math.sin(aRand))) + yScale/2
        ##Calculates the radius from the center of the canvas
        r = math.hypot((xPos - xScale/2), (yPos - yScale/2))
        return [xPos, yPos, r]

    def calcInitVel(self, xPos, yPos, xScale, yScale, G, mStar, r):
        ## Calculate initial velocities for circular orbits at the current point position.
        ## Assumes mass of point is smaller than the mass of the central star (mStar).
        xVel = (-(yPos - yScale/2) / r) * (G * mStar / r)**.5
        yVel = ((xPos - xScale/2) / r) * (G * mStar / r)**.5
        return [xVel, yVel]
        

    def update(self):
        ## Create a temp array that will be used to store the updated positions as we work on each point.
        workArray = self.pointArray[:]
        ## Loop over every point
        for i in range(len(self.pointArray)):
            if self.pointArray[i] != None:
                for j in range(len(self.pointArray)):
                    if i == j or self.pointArray[j] == None:
                        pass
                    else:
                        ## Calculate the distance between two points, how much force there is between them, and then the
                        ## resulting x and y velocities that need to be added to the point.
                        dist = Field.calcDist(self.pointArray[i].xPos, self.pointArray[i].yPos, self.pointArray[j].xPos, self.pointArray[j].yPos)
                        r = ((self.pointArray[j].mass)**(1/3))/2000 + ((self.pointArray[i].mass)**(1/3))/2000
                        pi = self.pointArray[i]
                        pj = self.pointArray[j]

                        if dist <= r:
                            cMass = pi.mass + pj.mass
                            workArray[i] = Point((pi.xPos*pi.mass + pj.xPos*pj.mass)/cMass,
                                                 (pi.yPos*pi.mass + pj.yPos*pj.mass)/cMass,
                                                 (pi.xVel*pi.mass + pj.xVel*pj.mass)/cMass,
                                                 (pi.yVel*pi.mass + pj.yVel*pj.mass)/cMass,
                                                 cMass,
                                                 pi.xScale,
                                                 pi.yScale,
                                                 pi.colour)
                            workArray[j] = None
                            self.pointArray[j] = None
                        else:
                            ## Calculate values against every other point, but not for a point against itself.
                            force = Field.calcForce(self.pointArray[i].mass, self.pointArray[j].mass, dist)
                            workArray[i].xVel += Field.calcAccl(self.pointArray[i].mass, force, dist, self.pointArray[i].xPos, self.pointArray[j].xPos)
                            workArray[i].yVel += Field.calcAccl(self.pointArray[i].mass, force, dist, self.pointArray[i].yPos, self.pointArray[j].yPos)
                ## Move the point once all of the forces have been applied to it.
                workArray[i].move()
        ## Make a deep copy of the temp array to the instance array so that it can be used for drawing and future iteration.
        self.pointArray = [x for x in workArray if x != None]

    def calcDist(x1, y1, x2, y2):
        ## calculate the absolute differences of the points
        ## and then the distance between them using a^2 + b^2 = c^2
        return math.hypot(abs(x1 - x2), abs(y1 - y2))

    def calcForce(m1, m2, r):
    ##def calcForce(m1, m2, r, g = 0.0001):
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
        self.width = 600
        self.height = 600
        self.progress = None
        self.field = Field(numPoints, self.width, self.height)
        self.canvas = tk.Canvas(master, width = self.width, height = self.height, background = 'black')
        self.canvas.pack()

    ## For every point in the field, draw a circle at its co-ordinates.
    def drawFrame(self):
        for i in range(len(self.field.pointArray)):
            ## Calculate the drawn radius of each point
            r = ((self.field.pointArray[i].mass)**(1/3))/2000
            x = self.field.pointArray[i].xPos
            y = self.field.pointArray[i].yPos
            colour = self.field.pointArray[i].colour
            ## Draw each oval centered on the point co-ords.
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill = colour, outline = colour)
            self.canvas.create_text(self.width/2, 10, fill='white', text=self.progress)
            self.canvas.create_text(self.width/2, 25, fill='white', text='Press \'r\' to reset')
            ## Update the canvas, otherwise nothing will be visible because the TK will wait until the program is out of a function to update the GUI by default.
        self.field.update()

class Application():
    def __init__(self):
        self.numObjects = 20
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
            time.sleep(1/60)
        self.d.canvas.destroy()

    ## Used to reset the simulation (new simulation).
    def reset(self, event):
        char = repr(event.char)
        print(char)
        if 'r' in char:
            print('Reset!')
            self.d.canvas.destroy()
            self.i = 1
            self.d = Draw(self.root, self.numObjects)

a = Application()
