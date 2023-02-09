# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

# Edited by:  Abdurrahman Lleshi (k20014224) for CW AIN 2022.

from pacman import Directions
from game import Agent
import api
import random
import game
import util
import sys

#
# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
#
# Code for the Grid class is provided by week 5 solution.
#
class Grid:
         
    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print
        
    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width


class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

        # Initialise values for MDP-solver agent
        self.gamma = 0.7 # discount factor
        self.reward = 0.55 # reward for each utility
        self.ghostPrice, self.foodPrice, self.capsulePrice = -15, 15, 15 # rewards for ghosts, eating food, and capsules
        self.utilityMap = [] # Store x and y coordinates with their corresponding utility values
        self.utilityMapCopy = [] # Store a copy of the utility map


    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)

        # Make a map of the right size
        self.makeMap(state)
        self.addWallsToMap(state)
        self.updateFoodInMap(state)
        self.updateGhostInMap(state)
        self.updateCapsulesInMap(state)
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"
    
    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)

        # Create a map for the utility values and a copy.
        self.utilityMap = Grid(width, height)
        self.utilityMapCopy = Grid(width, height)

    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    #
    # As provided by week 5 grid solution.
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map
    #
    # As provided by week 5 grid solution.
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    # Create a map with a current picture of the food that exists and add the value of food to the utility map.
    # Code modified from week 5 to add food to the utility map.
    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, ' ')
        food = api.food(state)
        for i in range(len(food)):
            self.utilityMap.setValue(food[i][0], food[i][1], self.foodPrice)
            self.map.setValue(food[i][0], food[i][1], '*')
    
    # Create a map with a current picture of the ghosts that exists and add the value of ghost to the utility map.
    # Code modified from week 5 to add ghost to the utility map.
    def updateGhostInMap(self, state):
        ghosts = api.ghosts(state)
        for i in range(len(ghosts)):
            self.utilityMap.setValue(int(ghosts[i][0]), int(ghosts[i][1]), self.ghostPrice)
            self.map.setValue(int(ghosts[i][0]), int(ghosts[i][1]), 'G')

    # Create a map with a current picture of the capsules that exists and add the value of capsule to the utility map.
    # Code modified from week 5 to add capsule to the utility map.
    def updateCapsulesInMap(self, state):
        capsules = api.capsules(state)
        for i in range(len(capsules)):
            self.utilityMap.setValue(capsules[i][0], capsules[i][1], self.capsulePrice)
            self.map.setValue(int(capsules[i][0]), int(capsules[i][1]), 'C')
    


    # This function is where the value iteration algorithm is implemented.
    # Value iteration is used to calculate the utility of each state over a set amount of iterations.
    # Instead of copying the utility map to a new map, and check it has converged, we simply iterate to a set amount of iterations as this saves computation time.
    # This value iteration algorithm is based on the pseudo code provided in the lecture slides.
    # The loops depends on the width and height of the map. For this coursework it would be either small grid or medium grid.
    def valueIteration(self, loops):    

        # Loop through the number of times specified by by getAction function depending on the size of the grid if it is medium it runs 245 times else it runs 195 times
        for i in range(loops):
            # # Copies the utilityCopyMap to a new utilityMap.
            # self.utilityMap = self.utilityMapCopy
            # Loop through the map width and height
            for x in range(self.map.getWidth()):
                for y in range(self.map.getHeight()):
                    # Check if the current element is not a wall, food, ghost or capsule.
                    if self.map.getValue(x, y) != '%' and self.map.getValue(x, y) != 'G' and self.map.getValue(x, y) != '*' and self.map.getValue(x, y) != 'C':
                        # Get the utility values around north, east, south and west of the current x, y coordinates.
                        
                        n = self.utilityMap.getValue(x, y+1)
                        e = self.utilityMap.getValue(x+1, y)
                        s = self.utilityMap.getValue(x, y-1)
                        w = self.utilityMap.getValue(x-1, y)

                        # Apply the bellman equation to get the utility value around the current x, y coordinates.      
                        up = (0.8 * n) + (0.1 * e) + (0.1 * w)
                        left = (0.8 * e) + (0.1 * n) + (0.1 * s)
                        down = (0.8 * s) + (0.1 * e) + (0.1 * w)
                        right = (0.8 * w) + (0.1 * n) + (0.1 * s)
                    
                        # Set the value of the current x, y coordinates to the maximum utility value around it.
                        self.utilityMap.setValue(x, y, self.reward + (self.gamma * max(up, left, down, right)))
            
        # self.utilityMap.prettyDisplay()

    # The function MDPSolver is used to determine the best action to take.
    # It works by taking all legal actions available to the agent and calculating the utility of each action.
    # It makes sure that the agent does not go into a ghost if it does the utility is set to 0 else it will update the utility of the action using the bellman equation for that action.
    # The action with the highest utility is then stored in maxUtility.
    # A set of if statements are used to determine which action has the highest utility and return that action.
    def MDPSolver(self, state):
        # Get the current position of the pacman and put into currentPosX for x and currentPosY for y into variables.
        currentLoc = api.whereAmI(state)
        currentPosX = currentLoc[0]
        currentPosY = currentLoc[1]

        # Get legal actions
        action = api.legalActions(state)

        # Initialize utilities for the move all to 0
        U_n = 0
        U_e = 0
        U_s = 0
        U_w = 0

        # Get the utility values around north, east, south and west of the current x, y coordinates.
        n = self.utilityMap.getValue(currentPosX, currentPosY+1)
        e = self.utilityMap.getValue(currentPosX+1, currentPosY)
        s = self.utilityMap.getValue(currentPosX, currentPosY-1)
        w = self.utilityMap.getValue(currentPosX-1, currentPosY)

        # Get the utility of the current position.
        current = self.utilityMap.getValue(currentPosX, currentPosY)

        # Check if the pacman can move north, if the action is legal and there is no ghost in the next position then update the utility of the action using the bellman equation.
        if 'North' in action:
            if self.map.getValue(currentPosX, currentPosY + 1) != 'G':
                U_n = (0.8 * n) + (0.1 * e) + (0.1 * w)
            else:
                U_n = 0
        # Check if the pacman can move east, if the action is legal and there is no ghost in the next position then update the utility of the action using the bellman equation.
        if 'East' in action:
            if self.map.getValue(currentPosX + 1, currentPosY) != 'G':
                U_e = (0.8 * e) + (0.1 * n) + (0.1 * s)
            else:
                U_e = 0
        # Check if the pacman can move south, if the action is legal and there is no ghost in the next position then update the utility of the action using the bellman equation.
        if 'South' in action:
            if self.map.getValue(currentPosX, currentPosY - 1) != 'G':
                U_s = (0.8 * s) + (0.1 * e) + (0.1 * w)
            else:
                U_s = 0
        # Check if the pacman can move west, if the action is legal and there is no ghost in the next position then update the utility of the action using the bellman equation.
        if 'West' in action:
            if self.map.getValue(currentPosX - 1, currentPosY) != 'G':
                U_w = (0.8 * w) + (0.1 * n) + (0.1 * s)
            else:
                U_w = 0
        
        # Get max utility of the actions
        maxUtility = max(U_n, U_e, U_s, U_w)

        # Return the action with Direction.ACTION with the highest utility.
        if U_n == maxUtility:
            return Directions.NORTH
        elif U_e == maxUtility:
            return Directions.EAST
        elif U_s == maxUtility:
            return Directions.SOUTH
        elif U_w == maxUtility:
            return Directions.WEST
        else:
            return Directions.STOP
        

    # For now I just move randomly, but I display the map to show my progress
    def getAction(self, state):
        """The getAction method is called by the game to get an action from the agent."""

        # Update the map with the new information
        self.updateFoodInMap(state)
        self.updateGhostInMap(state)
        self.updateCapsulesInMap(state)
        # self.valueIteration()

        # self.map.prettyDisplay()

        # Check if map is greater than 7x7 and if so, run value iteration for medium maps.
        # Else run value iteration for small maps.
        if self.map.getWidth() > 7 and self.map.getHeight() > 7:
            self.valueIteration(loops = 385)
        else:
            self.valueIteration(loops = 185)
            
        
        # Get the actions we can try.
        legal = api.legalActions(state)    

        # Get the best action to take based on the MDPSolver function.
        return api.makeMove(self.MDPSolver(state), legal)
