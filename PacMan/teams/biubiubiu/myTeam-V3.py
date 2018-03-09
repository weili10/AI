# myTeam_V3.py
# v3 update:
#   attack can increase targetfood upto 5 if enermies are scared of no enemies
#   and after score > 10, the attack while change into baseline defence mode to help defender


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

# class DummyAgent(CaptureAgent):
#     """
#     A Dummy agent to serve as an example of the necessary agent structure.
#     You should look at baselineTeam.py for more details about how to
#     create an agent as this is the bare minimum.
#     """

#     def registerInitialState(self, gameState):
#         """
#         This method handles the initial setup of the
#         agent to populate useful fields (such as what team
#         we're on).

#         A distanceCalculator instance caches the maze distances
#         between each pair of positions, so your agents can use:
#         self.distancer.getDistance(p1, p2)

#         IMPORTANT: This method may run for at most 15 seconds.
#         """

#         '''
#         Make sure you do not delete the following line. If you would like to
#         use Manhattan distances instead of maze distances in order to save
#         on initialization time, please take a look at
#         CaptureAgent.registerInitialState in captureAgents.py.
#         '''

#         self.start = gameState.getAgentPosition(self.index)
#         CaptureAgent.registerInitialState(self, gameState)

#         '''
#         Your initialization code goes here, if you need any.
#         '''

#     def chooseAction(self, gameState):
#         """
#         Picks among actions randomly.
#         """
#         actions = gameState.getLegalActions(self.index)

#         '''
#         You should change this in your own agent.
#         '''
#         # You can profile your evaluation time by uncommenting these lines
#         # start = time.time()
#         values = [self.evaluate(gameState, a) for a in actions]
#         # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

#         maxValue = max(values)
#         bestActions = [a for a, v in zip(actions, values) if v == maxValue]

#         foodLeft = len(self.getFood(gameState).asList())

#         if foodLeft <= 2:
#             bestDist = 9999
#             for action in actions:
#                 successor = self.getSuccessor(gameState, action)
#                 pos2 = successor.getAgentPosition(self.index)
#                 dist = self.getMazeDistance(self.start, pos2)
#                 if dist < bestDist:
#                     bestAction = action
#                     bestDist = dist
#             return bestAction

#         return random.choice(bestActions)

#     def getSuccessor(self, gameState, action):
#         """
#         Finds the next successor which is a grid position (location tuple).
#         """
#         successor = gameState.generateSuccessor(self.index, action)
#         pos = successor.getAgentState(self.index).getPosition()
#         if pos != nearestPoint(pos):
#             # Only half a grid position was covered
#             return successor.generateSuccessor(self.index, action)
#         else:
#             return successor

#     def evaluate(self, gameState, action):
#         """
#         Computes a linear combination of features and feature weights
#         """
#         features = self.getFeatures(gameState, action)
#         weights = self.getWeights(gameState, action)
#         return features * weights

#     def getFeatures(self, gameState, action):
#         """
#         Returns a counter of features for the state
#         """
#         features = util.Counter()
#         successor = self.getSuccessor(gameState, action)
#         features['successorScore'] = self.getScore(successor)
#         return features

#     def getWeights(self, gameState, action):
#         """
#         Normally, weights do not depend on the gameState.  They can be either
#         a counter or a dictionary.
#         """
#         return {'successorScore': 1.0}


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
        self.safeDistForBack = 2
        self.timeLimite = 0.9
        self.overtime = False

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

    def getCurFeatures(self,gameState):

        features = util.Counter()
        # foodList = self.getFood(gameState).asList()
        # features['Score'] = self.getScore(gameState)

        # # Compute distance to the nearest food

        # if len(foodList) > 0: # This should always be True,  but better safe than sorry
        #   myPos = gameState.getAgentState(self.index).getPosition()
        #   minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        #   features['distanceToFood'] = minDistance

        # find enemies
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]

        # # feature invader
        # features['numInvaders'] = len(invaders)
        # if len(invaders) > 0:
        #   invaderDists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        #   features['invaderDistance'] = min(invaderDists)

        # # feature ghost
        # features['numGhosts'] = len(ghosts)

        #feature enemy scare
        features["enemyScareTime"] = enemies[0].scaredTimer
        

        # # feature isPacman
        # if gameState.getAgentState(self.index).isPacman:
        #   features["isPacman"] = 1
        # else:
        #   features["isPacman"] = 0
        # return features

        #feature food eaten
        features["foodCarring"] = gameState.getAgentState(self.index).numCarrying

        return features

        
    def chooseAction(self,gameState):
        score = self.getScore(gameState)
        if score < 18:
            action = self.chooseAttackAction(gameState)
        else:
            action = self.chooseDefenceAction(gameState)

        return action


    def chooseAttackAction(self, gameState):

        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        
        enemyScareTime = enemies[0].scaredTimer
        foodCarring = gameState.getAgentState(self.index).numCarrying


        print foodCarring
        
        # don't scare ghosts
        if enemyScareTime>10:
            self.safeDistForEat = -1
            self.safeDistForBack = -1
        else:
            self.safeDistForEat = 3
            self.safeDistForBack = 2
        # take more food
        if foodCarring == self.targetFood and self.targetFood < 5:
            if len(ghosts) == 0 or enemyScareTime > 10:
                self.targetFood += 1
            else:
                self.targetFood = 1
        else:
            if self.targetFood > foodCarring+1:
                self.targetFood = foodCarring+1

                    

        if foodCarring < self.targetFood:
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
            # actions = gameState.getLegalActions(self.index)
            # actions.remove(Directions.STOP)
            # reversed_direction = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
            
            # if reversed_direction in actions and len(actions) > 1:
            #     actions.remove(reversed_direction)
            # return random.choice(actions)

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
        capsuleList = self.getCapsules(gameState)

        foodList = self.getFood(gameState).asList()
        foodList += capsuleList
        foodLeft = len(foodList)

        myPos = gameState.getAgentState(self.index).getPosition()
        minFoodDistance = min([self.getMazeDistance(myPos, food) for food in foodList])

        # if there are enemies
        enemies = [self.getCurrentObservation().getAgentState(i) for i in self.getOpponents(gameState)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]

        if len(ghosts) > 0:
            ghostDists = min([self.getMazeDistance(myPos, a.getPosition()) for a in ghosts])
            # best practice <= 3
            if ghostDists <= self.safeDistForEat:
                return len(ghosts) * 999999
            else:
                return minFoodDistance
        else:
            return foodLeft + minFoodDistance

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
        enemies = [self.getCurrentObservation().getAgentState(i) for i in self.getOpponents(gameState)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        if len(ghosts) > 0:
            ghostDists = min([self.getMazeDistance(myPos, a.getPosition()) for a in ghosts])
            # best 1
            if ghostDists <= self.safeDistForBack:
                return len(ghosts) * 999999
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



# class OffensiveReflexAgent(DummyAgent):
#   """
#   A reflex agent that seeks food. This is an agent
#   we give you to get an idea of what an offensive agent might look like,
#   but it is by no means the best or only way to build an offensive agent.
#   """
#   def getFeatures(self, gameState, action):
#     features = util.Counter()
#     successor = self.getSuccessor(gameState, action)
#     foodList = self.getFood(successor).asList()
#     features['successorScore'] = self.getScore(successor)

#     # Compute distance to the nearest food

#     if len(foodList) > 0: # This should always be True,  but better safe than sorry
#       myPos = successor.getAgentState(self.index).getPosition()
#       minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
#       features['distanceToFood'] = minDistance

#     # find enemies
#     enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#     invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
#     ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]

#     # feature invader
#     features['numInvaders'] = len(invaders)
#     if len(invaders) > 0:
#       invaderDists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#       features['invaderDistance'] = min(invaderDists)

#     # feature ghost
#     features['numGhosts'] = len(ghosts)
#     ghostsPos = [a.getPosition() for a in ghosts]

#     # feature isPacman
#     if successor.getAgentState(self.index).isPacman:
#       features["isPacman"] = 1
#     else:
#       features["isPacman"] = 0
#     return features

#     #feature food eaten


#   def getWeights(self, gameState, action):
#     successor = self.getSuccessor(gameState, action)
#     enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#     invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
#     ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
#     if len(ghosts) > 0:
#       return {'successorScore': 100, 'distanceToFood': -5,'isPacman':0}
#     else:
#       return {'successorScore': 100, 'distanceToFood': -1,'isPacman':100}




class DefensiveAStarAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.start = gameState.getAgentPosition(self.index)
        self.totalFood = len(self.getFood(gameState).asList())
        self.timeLimite = 0.9

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

    def chooseAction(self, gameState):
        goal = self.goalDefiner(gameState)
        actions = self.aStarSearch(gameState, goal)
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

    def UpdateSuccessor(self, startState):
        actions = startState.getLegalActions(self.index)
        actions.remove(Directions.STOP)

        successor_list = list()
        for action in actions:
            successor = self.getSuccessor(startState, action)
            # calculate action cost
            successor_position = successor.getAgentPosition(self.index)
            action_cost = self.getMazeDistance(self.start, successor_position)
            format = (successor, action, action_cost)
            successor_list.append(format)

        return successor_list