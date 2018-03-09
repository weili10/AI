# myTeam.py


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

from util import nearestPoint,PriorityQueue
import distanceCalculator

import sys
sys.path.append('teams/biubiubiu/')


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AstarAgent', second = 'DefensiveReflexAgent'):
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

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

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


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
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

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gameState.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

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
    # how many food to eat each time
    self.foodEachTime = 1;

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


  def chooseAction(self, gameState):

    if gameState.getAgentState(self.index).numCarrying<1:
      actions = self.aStarSearch(gameState)
    else:
      actions = self.aStarGoBack(gameState,self.start) 

    if len(actions)==0:
      actions = gameState.getLegalActions(self.index)
      return random.choice(actions)
    return actions[0]
    

  def aStarSearch(self, gameState):
    """Search the node that has the lowest combined cost and heuristic first."""

    openSet =  PriorityQueue()
    closeSet = []

    startState = (gameState,None,0)  # (state directin cost)
    
    openSet.push(startState,self.heuristicFoodDistance(startState[0]))
    #startPosCo = getCoordinate(startPos)
    gs = {startState[0]:0}
    hs = {startState[0]:self.heuristicFoodDistance(startState[0])}
    prev = {}
    actions = []

    startTime = time.time()   #overtime

    while not openSet.isEmpty():
        curState = openSet.pop()
        if self.shouldGoBack(curState[0]):
            return self.reconstructPath(prev,curState)

        closeSet.append(curState[0])

        if time.time()-startTime>0.5:
          return self.reconstructPath(prev,curState)
        
        successors = self.getSuccessorState(curState[0])
        for successor in successors:
            if successor[0] in closeSet:
                continue

            if successor[0] not in gs:
                gs[successor[0]] = sys.maxint
                hs[successor[0]] = self.heuristicFoodDistance(successor[0])
                # V2 add, if this succesor meet ghost don't add it to consideration
                # if hs[successor[0]] < 10000:
                openSet.push(successor,gs[successor[0]]+hs[successor[0]])

            ngs = gs[curState[0]] + successor[2]
            if ngs < gs[successor[0]]:
                gs[successor[0]] = ngs
                prev[successor] = curState
                openSet.push(successor,gs[successor[0]]+hs[successor[0]])
    return []

  def heuristicFoodDistance(self, gameState):
    capsuleList=self.getCapsules(gameState)

    foodList = self.getFood(gameState).asList()
    foodList+=capsuleList
    foodLeft=len(foodList)

    myPos = gameState.getAgentState(self.index).getPosition()
    minFoodDistance = min([self.getMazeDistance(myPos, food) for food in foodList])

    # if there are enemies
    enemies = [self.getCurrentObservation().getAgentState(i) for i in self.getOpponents(gameState)]
    ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]

    if len(ghosts)>0:
      #dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
      return len(ghosts)*999999
    else:
      return minFoodDistance

  def shouldGoBack(self,gameState):

    # enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    # enemies are scared or didn't take any food
    if gameState.getAgentState(self.index).numCarrying<1:
      return False
    else:
      return True

  def reconstructPath(self,prev,curState):
    actions = [curState[1]]
    while curState in prev:
        curState = prev[curState]
        actions.append(curState[1])
    actions.reverse()
    return actions[1:]   #remove 'None' from the startPos


  def getSuccessorState(self,gameState):
    actions = gameState.getLegalActions(self.index)
    actions.remove(Directions.STOP)

    reversed_direction = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

    if reversed_direction in actions and len(actions) > 1:
        actions.remove(reversed_direction)

    successors = []
    for action in actions:
      successorState = self.getSuccessor(gameState, action)
      
      successorPos=successorState.getAgentPosition(self.index)
      actionCost = self.getMazeDistance(gameState.getAgentPosition(self.index),successorPos)
      
      successor = (successorState,action,actionCost)
      successors.append(successor)

    return successors

  def aStarGoBack(self, gameState,gaolPos):

    openSet =  PriorityQueue()
    closeSet = []
    startState = (gameState,None,0)  # (state directin cost)
    goalPos = self.start

    openSet.push(startState,self.heuristicBackDistance(startState[0],goalPos))
    #startPosCo = getCoordinate(startPos)
    gs = {startState[0]:0}
    hs = {startState[0]:self.heuristicBackDistance(startState[0],goalPos)}
    prev = {}
    actions = []
    startTime = time.time()   #overtime

    while not openSet.isEmpty():
        curState = openSet.pop()
        # goal state
        if curState[0].getAgentPosition(self.index) == goalPos:
            return self.reconstructPath(prev,curState)

        closeSet.append(curState[0])

        if time.time()-startTime > 0.5:
          return self.reconstructPath(prev,curState)
        
        successors = self.getSuccessorState(curState[0])
        for successor in successors:
            if successor[0] in closeSet:
                continue

            if successor[0] not in gs:
                gs[successor[0]] = sys.maxint
                hs[successor[0]] = self.heuristicBackDistance(successor[0],goalPos)
                # V2 add, if this succesor meet ghost don't add it to consideration
                # if hs[successor[0]] < 10000:
                openSet.push(successor,gs[successor[0]]+hs[successor[0]])

            ngs = gs[curState[0]] + successor[2]
            if ngs < gs[successor[0]]:
                gs[successor[0]] = ngs
                prev[successor] = curState
                openSet.push(successor,gs[successor[0]]+hs[successor[0]])
    return []

  def heuristicBackDistance(self,gameState,goalPos):
    myPos = gameState.getAgentPosition(self.index)
    dist = self.getMazeDistance(myPos, goalPos)
    enemies = [self.getCurrentObservation().getAgentState(i) for i in self.getOpponents(gameState)]
    ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    if len(ghosts)>0:
      ghostDists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
      return len(ghosts)*999999
    else:
      return dist


class OffensiveReflexAgent(DummyAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = self.getScore(successor)

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    # find enemies
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]

    # feature invader
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      invaderDists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(invaderDists)
    
    # feature ghost
    features['numGhosts'] = len(ghosts)
    ghostsPos = [a.getPosition() for a in ghosts]

    # feature isPacman
    if successor.getAgentState(self.index).isPacman:
      features["isPacman"] = 1
    else:
      features["isPacman"] = 0
    return features

    #feature food eaten


  def getWeights(self, gameState, action):
    successor = self.getSuccessor(gameState, action)
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    if len(ghosts) > 0:
      return {'successorScore': 100, 'distanceToFood': -5,'isPacman':0}
    else:
      return {'successorScore': 100, 'distanceToFood': -1,'isPacman':100}

    

class DefensiveReflexAgent(DummyAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

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


