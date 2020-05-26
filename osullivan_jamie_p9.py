"""
Snakes on a plane
OOP program of snakes that act as random walkers on a grid

Created: 2020-14-04

@author: Jamie O'Sullivan
"""

import random
import numpy as np
import matplotlib.pyplot as plt


# ====================================================================================

class Snake:

    """
    Input parameters include: initial head position, length of snake, initial direction, head symbol, and head color.
    The snake class starts off plotted as a straight line and then randomly "walks", updating its trail as it goes.
    """

    def __init__(self, headPos=(10,10), length=5, direction='north', headSym='o', color='b'):

        self.xpos = headPos[0]
        self.ypos = headPos[1]
        self.length = length
        self.direction = direction  # snakes should originally be facing linearly
        self.headSym = headSym
        self.color = color
        self.trapped = False
        self.trail = []  # list of tuples of every index snake is taking up

        # which borders the snake is crossing currently
        self.latCross = False  # side borders
        self.longCross = False  # top and bottom

        # fill trail with all points on grid that snake is currently taking up - in order
        for point in range(length + 1):
            if self.direction == 'north':
                self.trail.append((headPos[0], headPos[1] - point))
            elif self.direction == 'east':
                self.trail.append((headPos[0] - point, headPos[1]))
            elif self.direction == 'south':
                self.trail.append((headPos[0], headPos[1] + point))
            elif self.direction == 'west':
                self.trail.append((headPos[0] + point, headPos[1]))
            else:
                print('Invalid direction input for snake at head position: ' + str(headPos))

    def move(self, xmax, ymax, bc, taken):

        disallowed = set()  # add disallowed directions
        if bc == 'wall':  # allowed to walk on wall
            if self.ypos == ymax or taken[self.xpos, self.ypos + 1]:
                disallowed.add('north')
            if self.xpos == xmax or taken[self.xpos + 1, self.ypos]:
                disallowed.add('east')
            if self.ypos == 0 or taken[self.xpos, self.ypos - 1]:
                disallowed.add('south')
            if self.xpos == 0 or taken[self.xpos - 1, self.ypos]:
                disallowed.add('west')
        elif bc == 'periodic':  # determine if spots are taken
            if (self.ypos == ymax and taken[self.xpos, (self.ypos + 1) % ymax]) \
                    or (self.ypos < ymax and taken[self.xpos, self.ypos + 1]):
                disallowed.add('north')
            if (self.xpos == xmax and taken[(self.xpos + 1) % xmax, self.ypos]) \
                    or (self.xpos < xmax and taken[self.xpos + 1, self.ypos]):
                disallowed.add('east')
            if (self.ypos == 0 and taken[self.xpos, (self.ypos - 1) % ymax]) \
                    or (self.ypos > 0 and taken[self.xpos, self.ypos - 1]):
                disallowed.add('south')
            if (self.xpos == 0 and taken[(self.xpos - 1) % xmax, self.ypos]) \
                    or (self.xpos > 0 and taken[self.xpos - 1, self.ypos]):
                disallowed.add('west')

        allowed = {'north', 'east', 'south', 'west'}.difference(disallowed)  # filled with only allowable directions

        if len(allowed) == 0:  # snake cannot move any direction
            self.trapped = True
        else:
            self.direction = random.choice(list(allowed))
            if self.direction == 'north':
                if (bc == 'wall' and self.ypos < ymax) or bc == 'periodic':
                    self.ypos += 1
            elif self.direction == 'east':
                if (bc == 'wall' and self.xpos < xmax) or bc == 'periodic':
                    self.xpos += 1
            elif self.direction == 'south':
                if (bc == 'wall' and self.ypos > 0) or bc == 'periodic':
                    self.ypos -= 1
            elif self.direction == 'west':
                if (bc == 'wall' and self.xpos > 0) or bc == 'periodic':
                    self.xpos -= 1

            # used modulus to turn 'over max' periodic positions into correct ones
            if self.xpos != xmax:
                self.xpos = self.xpos % xmax
            if self.ypos != ymax:
                self.ypos = self.ypos % ymax


# ====================================================================================

class Grid:

    """
    Grid class input parameters include: snake objects as tuple, grid size, boundary conditions,
    and number of maximum steps, and runs the non-overlapping snakes on a random walk until they all can't move
    or until nSteps is reached, whichever comes first.
    """

    def __init__(self, snakes, size=(20,20), bc='wall', nSteps=400):
        self.snakes = snakes
        self.xmax = size[0]
        self.ymax = size[1]
        self.bc = bc
        self.nSteps = nSteps
        self.point = []
        self.lines = []
        # array to see what nodes are currently taken
        self.taken = np.zeros([self.xmax + 1, self.ymax + 1], dtype=bool)

        plt.figure()  # create new figure window if one is already open
        ax = plt.axes(xlim=(0, self.xmax), ylim=(0, self.ymax))

        # mark which spots are being taken and plot initial snake segments
        for i, s in enumerate(self.snakes):
            self.lines.append([])
            for j, seg in enumerate(s.trail):
                self.taken[seg[0] % self.xmax, seg[1] % self.ymax] = True
                # convert all segments in trail to real plotted coordinates using modulus
                s.trail[j] = (s.trail[j][0] % self.xmax, s.trail[j][1] % self.ymax)
                if j > 0:  # plot n-1 segments, where n is length of snake
                    if s.trail[j][0] - s.trail[j - 1][0] < -1:
                        # going WEST - crosses y axis
                        l, = ax.plot([0, 1],
                                     [s.trail[j - 1][1] % self.ymax, s.trail[j][1] % self.ymax], s.color)
                    elif s.trail[j][0] - s.trail[j - 1][0] > 1:
                        # going EAST - crosses y axis
                        l, = ax.plot([self.xmax, self.xmax - 1],
                                     [s.trail[j - 1][1] % self.ymax, s.trail[j][1] % self.ymax], s.color)
                    elif s.trail[j][1] - s.trail[j - 1][1] < -1:
                        # going SOUTH - crosses x axis
                        l, = ax.plot([s.trail[j - 1][0] % self.xmax, s.trail[j][0] % self.xmax],
                                     [0, 1], s.color)
                    elif s.trail[j][1] - s.trail[j - 1][1] > 1:
                        # going NORTH - crosses x axis
                        l, = ax.plot([s.trail[j - 1][0] % self.xmax, s.trail[j][0] % self.xmax],
                                     [self.ymax, self.ymax - 1], s.color)
                    else:
                        # no borders are being crossed
                        l, = ax.plot([s.trail[j - 1][0] % self.xmax, s.trail[j][0] % self.xmax],
                                     [s.trail[j - 1][1] % self.ymax, s.trail[j][1] % self.ymax], s.color)
                    self.lines[i].append(l)
            p, = ax.plot([s.xpos], [s.ypos], marker=s.headSym, c=s.color)
            self.point.append(p)
            self.borderCheck(s)

        plt.title('Stardust Crusaders')

    def go(self):
        stepCount = 0
        while not all([s.trapped for s in snakes]) and stepCount <= self.nSteps:
            for i, s in enumerate(snakes):
                s.move(self.xmax, self.ymax, self.bc, self.taken)
                if not s.trapped:

                    # Plot new point, mark spot as taken, and un-mark the last spot of the snake
                    # Then add to beginning of trail and remove from the end of trail
                    self.point[i].set_data(s.xpos, s.ypos)  # plot new head point
                    self.taken[s.xpos, s.ypos] = True  # mark new spot as taken
                    # mark last point as not taken anymore
                    self.taken[s.trail[-1][0] % self.xmax, s.trail[-1][1] % self.ymax] = False
                    s.trail.insert(0, (s.xpos, s.ypos))  # add new point to beginning of trail
                    s.trail.pop()

                    self.borderCheck(s)

                    # update line segments of each snake
                    for j, seg in enumerate(s.trail):
                        self.taken[seg[0] % self.xmax, seg[1] % self.ymax] = True
                        if j > 0:  # plot n-1 segments, where n is length of snake
                            # if snake is currently crossing border, fix (make sure length of line is 1)
                            if s.trail[j][0] - s.trail[j - 1][0] > 1:
                                # going WEST - crosses y axis
                                self.lines[i][j - 1].set_data([0, 1],
                                                              [s.trail[j - 1][1], s.trail[j][1]])
                            elif s.trail[j][0] - s.trail[j - 1][0] < -1:
                                # going EAST - crosses y axis
                                self.lines[i][j - 1].set_data([self.xmax, self.xmax - 1],
                                                              [s.trail[j - 1][1], s.trail[j][1]])
                            elif s.trail[j][1] - s.trail[j - 1][1] > 1:
                                # going SOUTH - crosses x axis
                                self.lines[i][j - 1].set_data([s.trail[j - 1][0], s.trail[j][0]],
                                                              [0, 1])
                            elif s.trail[j][1] - s.trail[j - 1][1] < -1:
                                # going NORTH - crosses x axis
                                self.lines[i][j - 1].set_data([s.trail[j - 1][0], s.trail[j][0]],
                                                              [self.ymax, self.ymax - 1])
                            else:
                                # no borders are being crossed
                                self.lines[i][j - 1].set_data([s.trail[j - 1][0], s.trail[j][0]],
                                                              [s.trail[j - 1][1], s.trail[j][1]])


            stepCount += 1
            plt.pause(0.2)

    def borderCheck(self, s):  # s is a snake
        # if periodic bc, max and min boundaries are the same spot, make sure lines are in correct spot, and fix trail
        if self.bc == 'periodic':
            if s.xpos == self.xmax:
                self.taken[0, s.ypos] = True
            elif s.xpos == 0:
                self.taken[self.xmax, s.ypos] = True
            if s.ypos == self.ymax:
                self.taken[s.xpos, 0] = True
            elif s.ypos == 0:
                self.taken[s.xpos, self.ymax] = True


# main program =======================================================================

jotaro = Snake(headPos=(10, 10), length=9, direction='north', headSym='o', color='k')
joseph = Snake(headPos=(15, 12), length=6, direction='south', headSym='o', color='khaki')
kakyoin = Snake(headPos=(20, 25), length=7, direction='east', headSym='o', color='g')
polnareff = Snake(headPos=(19, 15), length=7, direction='west', headSym='o', color='lightgray')
avdol = Snake(headPos=(1, 5), length=8, direction='west', headSym='o', color='r')
iggy = Snake(headPos=(20, 6), length=3, direction='south', headSym='o', color='slategrey')

snakes = (jotaro, joseph, polnareff, avdol, kakyoin, iggy)
plane = Grid(snakes, size=(30, 30), bc='periodic', nSteps=400)
plane.go()


