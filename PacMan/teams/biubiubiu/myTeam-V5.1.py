# myTeam-v5.py
# v5 update:
#    for defender: check lost food, if yes, goal = lost food
#                  go that position until we checked that position or we find invader
# 
#  V5 ranked 12 (staff-top-team 16)
#  
#  V5.1:
#    attacker: score target 5->10  safebackdis 2->1   eat more when enemies scare
#

# ---------
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


from captureAgents import CaptureAgent
import random, time, util, sys
from game import Directions
import game

from util import nearestPoint, PriorityQueue
import distanceCalculator

import sys

sys.path.append('teams/biubiubiu/')


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='AstarAgent', second='DefensiveAStarAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

class AstarAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''

        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''
        # how many food to eat
        self.targetFood = 1
        self.safeDistForEat = 3
        self.safeDistForBack = 1
        self.timeLimite = 0.9
        self.overtime = False

        self.curEnemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        self.curInvaders = [a for a in self.curEnemies if a.isPacman and a.getPosition() != None]
        self.curGhosts = [a for a in self.curEnemies if not a.isPacman and a.getPosition() != None]
        
        self.curEnemyScareTime = self.curEnemies[0].scaredTimer
        self.curFoodCarring = gameState.getAgentState(self.index).numCarrying
        
        self.curCapsuleList = self.getCapsules(gameState)
        self.curFoodList = self.getFood(gameState).asList() + self.curCapsuleList
        self.curFoodLeft = len(self.curFoodList)



    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def setCurFeatures(self,gameState):

        # find enemies
        self.curEnemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        self.curInvaders = [a for a in self.curEnemies if a.isPacman and a.getPosition() != None]
        self.curGhosts = [a for a in self.curEnemies if not a.isPacman and a.getPosition() != None]
       
        #feature enemy scare
        self.curEnemyScareTime=self.curEnemies[0].scaredTimer
        

        #feature food eaten
        self.curFoodCarring = gameState.getAgentState(self.index).numCarrying
        self.curScore = self.getScore(gameState)

        self.curCapsuleList = self.getCapsules(gameState)
        self.curFoodList = self.getFood(gameState).asList() + self.curCapsuleList
        self.curFoodLeft = len(self.curFoodList)

        
    def chooseAction(self,gameState):
        self.setCurFeatures(gameState)
        
        if self.curScore < 10:
            action = self.chooseAttackAction(gameState)
        else:
            action = self.chooseDefenceAction(gameState)

        return action


    def chooseAttackAction(self, gameState):

        print self.curFoodCarring
        
        # don't scare ghosts
        if self.curEnemyScareTime>10:
            self.safeDistForEat = -1
            self.safeDistForBack = -1
        else:
            self.safeDistForEat = 3
            self.safeDistForBack = 1

        myPos = gameState.getAgentState(self.index).getPosition()

        if len(self.curGhosts) > 0:
            # print len(self.curGhosts)
            ghostDists = min([self.getMazeDistance(myPos, a.getPosition()) for a in self.curGhosts])
            # print ghostDists 
        else:
            ghostDists = sys.maxint

        # take more food
        if self.curFoodCarring == self.targetFood and self.targetFood < 5:
            if ghostDists > 6  or self.curEnemyScareTime > 10:
                self.targetFood += 1
            else:
                self.targetFood = 1
        else:
            if self.targetFood > self.curFoodCarring+1:
                self.targetFood = self.curFoodCarring+1

        if self.curFoodCarring == self.targetFood and self.targetFood < 8:
            if self.curEnemyScareTime > 10:
                self.targetFood += 1
            else:
                self.targetFood = 1
        else:
            if self.targetFood > self.curFoodCarring+1:
                self.targetFood = self.curFoodCarring+1


        

        if self.curFoodCarring < self.targetFood and ( ghostDists>3 or self.curEnemyScareTime>10):
            print self.targetFood
            print "eat"
            actions = self.aStarEatFood(gameState)
        else:
            print self.targetFood
            print "run"
            actions = self.aStarGoBack(gameState, self.start)
        ## if meet the time limite, choose a random action except goback
        if self.overtime == True:
            print "overtime"
            self.overtime = False

        if len(actions) == 0:
            print "random"
            actions = gameState.getLegalActions(self.index)
            return random.choice(actions)
        return actions[0]

    def aStarEatFood(self, gameState):
        """Search the node that has the lowest combined cost and heuristic first."""

        openSet = PriorityQueue()
        closeSet = []

        startState = (gameState, None, 0)  # (state directin cost)

        openSet.push(startState, self.heuristicFoodDistance(startState[0]))
       
        gs = {startState[0]: 0}
        hs = {startState[0]: self.heuristicFoodDistance(startState[0])}
        prev = {}
        actions = []

        startTime = time.time()  # overtime

        while not openSet.isEmpty():
            curState = openSet.pop()
            if self.shouldGoBack(curState[0]):
                return self.reconstructPath(prev, curState)

            closeSet.append(curState[0])

            if time.time() - startTime > self.timeLimite:
                self.overtime = True
                return self.reconstructPath(prev, curState)

            successors = self.getSuccessorState(curState[0])
            for successor in successors:
                if successor[0] in closeSet:
                    continue

                if successor[0] not in gs:
                    gs[successor[0]] = sys.maxint
                    hs[successor[0]] = self.heuristicFoodDistance(successor[0])
                    if hs[successor[0]] < 9999:
                        openSet.push(successor, gs[successor[0]] + hs[successor[0]])

                ngs = gs[curState[0]] + successor[2]
                if ngs < gs[successor[0]]:
                    gs[successor[0]] = ngs
                    prev[successor] = curState
                    openSet.push(successor, gs[successor[0]] + hs[successor[0]])
        return []

    def heuristicFoodDistance(self, gameState):
        
        myPos = gameState.getAgentState(self.index).getPosition()
        minFoodDistance = min([self.getMazeDistance(myPos, food) for food in self.curFoodList])

        if len(self.curGhosts) > 0:
            ghostDists = min([self.getMazeDistance(myPos, a.getPosition()) for a in self.curGhosts])
            # best practice <= 3
            if ghostDists <= self.safeDistForEat:
                return 999999
            else:
                return minFoodDistance
        else:
            return self.curFoodLeft + minFoodDistance

    def shouldGoBack(self, gameState):
        return gameState.getAgentState(self.index).numCarrying >= self.targetFood

    def reconstructPath(self, prev, curState):
        actions = [curState[1]]
        while curState in prev:
            curState = prev[curState]
            actions.append(curState[1])
        actions.reverse()
        return actions[1:]  # remove 'None' from the startPos

    def getSuccessorState(self, gameState):
        actions = gameState.getLegalActions(self.index)
        actions.remove(Directions.STOP)
       
        successors = []
        for action in actions:
            successorState = self.getSuccessor(gameState, action)

            successorPos = successorState.getAgentPosition(self.index)
            actionCost = self.getMazeDistance(gameState.getAgentPosition(self.index), successorPos)

            successor = (successorState, action, actionCost)
            successors.append(successor)

        return successors

    def aStarGoBack(self, gameState, gaolPos):

        openSet = PriorityQueue()
        closeSet = []
        startState = (gameState, None, 0)  # (state directin cost)
        goalPos = self.start

        openSet.push(startState, self.heuristicBackDistance(startState[0], goalPos))
        
        gs = {startState[0]: 0}
        hs = {startState[0]: self.heuristicBackDistance(startState[0], goalPos)}
        prev = {}
        actions = []
        startTime = time.time()  # overtime

        while not openSet.isEmpty():
            curState = openSet.pop()
            # goal state
            if curState[0].getAgentPosition(self.index) == goalPos:
                return self.reconstructPath(prev, curState)

            closeSet.append(curState[0])

            if time.time() - startTime > self.timeLimite:
                self.overtime = True
                return self.reconstructPath(prev, curState)

            successors = self.getSuccessorState(curState[0])
            for successor in successors:
                if successor[0] in closeSet:
                    continue

                if successor[0] not in gs:
                    gs[successor[0]] = sys.maxint
                    hs[successor[0]] = self.heuristicBackDistance(successor[0], goalPos)
                    if hs[successor[0]] < 9999:
                        openSet.push(successor, gs[successor[0]] + hs[successor[0]])

                ngs = gs[curState[0]] + successor[2]
                if ngs < gs[successor[0]]:
                    gs[successor[0]] = ngs
                    prev[successor] = curState
                    openSet.push(successor, gs[successor[0]] + hs[successor[0]])
        return []

    def heuristicBackDistance(self, gameState, goalPos):
        myPos = gameState.getAgentPosition(self.index)
        dist = self.getMazeDistance(myPos, goalPos)
        # enemies = [self.getCurrentObservation().getAgentState(i) for i in self.getOpponents(gameState)]
        # ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        if len(self.curGhosts) > 0:
            ghostDists = min([self.getMazeDistance(myPos, a.getPosition()) for a in self.curGhosts])
            # best 1
            if ghostDists <= self.safeDistForBack:
                return 999999
            else:
                return dist
        else:
            return dist

    #### defense code ####
    ####  baseline defence ####
    def chooseDefenceAction(self, gameState):
    
        # Picks among the actions with the highest Q(s,a).
        actions = gameState.getLegalActions(self.index)

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        foodLeft = len(self.getFood(gameState).asList())
        if foodLeft <= 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start,pos2)
            if dist < bestDist:
                bestAction = action
                bestDist = dist
            return bestAction

        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights
    
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0)
        features['onDefense'] = 1
        if myState.isPacman: features['onDefense'] = 0

        # Computes distance to invaders we can see
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        features['numInvaders'] = len(invaders)
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

        if action == Directions.STOP: features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1

        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}


class DefensiveAStarAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.start = gameState.getAgentPosition(self.index)
        self.totalFood = len(self.getFoodYouAreDefending(gameState).asList())
        self.timeLimite = 0.85
        
        self.preCapsuleList = self.getCapsulesYouAreDefending(gameState)
        self.preFoodList = self.getFoodYouAreDefending(gameState).asList() + self.preCapsuleList
        
        self.curCapsuleList = self.getCapsulesYouAreDefending(gameState)
        self.curFoodList = self.getFoodYouAreDefending(gameState).asList() + self.curCapsuleList

        self.losedChecked = True

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def heuristic(self, a, b):
        return self.getMazeDistance(a, b)

    def checkFoodList(self,gameState):
        if len(self.curFoodList) < len(self.preFoodList):
            goal = list(set(self.preFoodList)-set(self.curFoodList))
            return goal[-1]
        else:
            return None

    def chooseAction(self, gameState):

        self.curCapsuleList = self.getCapsulesYouAreDefending(gameState)
        self.curFoodList = self.getFoodYouAreDefending(gameState).asList() + self.curCapsuleList
        # self.curEnemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        # self.curInvaders = [a for a in self.curEnemies if a.isPacman and a.getPosition() != None]

        goal = self.checkFoodList(gameState)
        # print goal
        if goal == None:
            goal = self.goalDefiner(gameState)
        else:
            self.losedChecked = False
            if self.getMazeDistance(gameState.getAgentPosition(self.index),goal)<=1:
                self.losedChecked = True

        # print goal
        actions = self.aStarSearch(gameState, goal)

        if self.losedChecked == True:
            self.preCapsuleList = self.curCapsuleList
            self.preFoodList = self.curFoodList

        if actions == []:
            # print "empty actions list!"
            actions = gameState.getLegalActions(self.index)
            return random.choice(actions)
        return actions[0]

    def goalDefiner(self, gameState):
        myPos = gameState.getAgentPosition(self.index)
        enemies = self.getOpponents(gameState)
        enemy1State = gameState.getAgentState(enemies[0])
        enemy2State = gameState.getAgentState(enemies[1])
        enemy1Pos = enemy1State.getPosition()
        enemy2Pos = enemy2State.getPosition()
        maxDistanceMA = 0
        maxDistanceMI = 0
        # how to choose the nearest enemy
        if enemy1Pos != None and enemy1State.isPacman:
            return enemy1Pos
        if enemy2Pos != None and enemy2State.isPacman:
            return enemy2Pos

        foodList = self.getFoodYouAreDefending(gameState).asList()

        if len(foodList) > 0 :
            for food in foodList:
                temp=self.getMazeDistance(food, self.start)
                temp1=abs(food[0]-self.start[0])+ abs(food[1]-self.start[1])
                if temp+temp1>maxDistanceMI+maxDistanceMA:
                    maxDistanceMI=temp
                    maxDistanceMA = temp1
                    targetX=food[0]
                    targetY=food[1]

        return (targetX, targetY)

    def aStarSearch(self, gameState, goalCoord):
        start = time.time()
        frontier = util.PriorityQueue()
        startState = gameState
        start_coord = startState.getAgentPosition(self.index)
        frontier.push((startState, []), self.heuristic(start_coord, goalCoord))
        visited = []
        while not frontier.isEmpty():
            node = frontier.pop()
            coord = node[0].getAgentPosition(self.index)
            actions = node[1]
            if time.time() - start > self.timeLimite:
                return actions
            if coord == goalCoord:
                return actions
            if coord not in visited:
                visited.append(coord)
                for successor in self.UpdateSuccessor(node[0]):
                    coordnext = successor[0].getAgentPosition(self.index)
                    Directions = successor[1]
                    if not coordnext in visited:
                        nextactions = actions + [Directions]
                        cost = len(nextactions) + self.heuristic(coordnext, goalCoord)
                        frontier.push((successor[0], nextactions), cost)
        return []

    def UpdateSuccessor(self, gameState):
        actions = gameState.getLegalActions(self.index)
        actions.remove(Directions.STOP)

        successor_list = list()
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            # calculate action cost
            successor_position = successor.getAgentPosition(self.index)
            action_cost = self.getMazeDistance(self.start, successor_position)
            successorState = (successor, action, action_cost)
            successor_list.append(successorState)

        return successor_list