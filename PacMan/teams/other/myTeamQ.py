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
from baselineTeam import ReflexCaptureAgent
import random, time, util
from game import Directions
import game



#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='QLearningAgent', second='QLearningAgent'):
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

        return random.choice(actions)

class QLearningAgent(DummyAgent):

    def __init__(self, index, epsilon = 0.1, gamma = 0.9, alpha = 0.8):
        self.index = index
        self.epsilon = float(epsilon)
        self.gamma = float(gamma)
        self.alpha = float(alpha)
        self.brain = util.Counter()
        self.observationHistory = []

    def enemyPosition(self, gameState):
        enemyPos = []
        for enemy in self.getOpponents(gameState):
            pos = gameState.getAgentPosition(enemy)
            if pos != None:
                enemyPos.append((enemy, pos))
        return enemyPos

    def enemyDistance(self, gameState):
        pos = self.enemyPosition(gameState)
        minDis = None
        if len(pos) > 0:
            myPos = gameState.getAgentPosition(self.index)
            for i, p in pos:
                dist = self.getMazeDistance(p, myPos)
                if dist < minDis:
                    minDis = dist
        return minDis

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        foodList = self.getFood(successor).asList()
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [x for x in enemies if x.isPacman and x.getPosition() != None]
        pos = gameState.getAgentPosition(self.index)


        features['successorScore'] = -len(foodList)


        features['numInvaders'] = len(invaders)

        if len(invaders) > 0:
            dists = [self.getMazeDistance(pos, x.getPosition()) for x in invaders]
            features['invaderDis'] = min(dists)


        enemyDis = self.enemyDistance(gameState)
        if enemyDis < 4:
            features['danger'] = 1
        else:
            features['danger'] = 0

        if action == 'Stop':
            features['stop'] = 1


        capsules = self.getCapsules(gameState)
        if len(capsules) > 0:
            minCapsuleDis = min([self.getMazeDistance(pos, capsule) for capsule in capsules])
        else:
            minCapsuleDis = 0.1
        features['capsuleDis'] = 1.0 / minCapsuleDis



        # Compute distance to the nearest food

        if len(foodList) > 0: # This should always be True,  but better safe than sorry
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
        return features

    

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -1, 'danger': -400, 'capsuleDis': -3, 'stop': -2000}



    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)


    def getQValue(self, gameState, action):
        features = self.getFeatures(gameState,action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def computeValueFromQValues(self, gameState):
        maxQvalue = float('-inf')
        for action in gameState.getLegalActions(self.index):
            maxQvalue = max(maxQvalue, self.getQValue(gameState, action))
        return maxQvalue if maxQvalue != float('-inf') else 0.0

    def getBestAction(self, gameState):
        if len(gameState.getLegalActions(self.index)) == 0:
            return None

        bestQValue = self.computeValueFromQValues(gameState)
        bestActions = []
        for action in gameState.getLegalActions(self.index):
            if bestQValue == self.getQValue(gameState, action):
                bestActions.append(action)
        return random.choice(bestActions)

    def getFurthestFood(self, gameState):
        furthestFood = None
        foods = self.getFood(gameState).asList()
        curPos = gameState.getAgentPosition(self.index)
        if len(foods) == 0:
            return (0, 0)
        maxDis = 0
        for food in foods:
            if self.getMazeDistance(curPos, food) > maxDis:
                maxDis = self.getMazeDistance(curPos, food)
                furthestFood = food
        return furthestFood

    def update(self, gameState, action, nextState, reward):
        difference = (reward + self.gamma * self.computeValueFromQValues(nextState)) - self.getQValue(gameState, action)
        features = self.getFeatures(gameState, action)
        for feature, value in features.items():
            #print feature, value
            self.brain[feature] += self.alpha * difference * features[feature]

    def getFurthestFood(self, gameState):
        furthestFood = None
        foods = self.getFood(gameState).asList()
        curPos = gameState.getAgentPosition(self.index)
        if len(foods) == 0:
            return (0, 0)
        maxDis = 0
        for food in foods:
            if self.getMazeDistance(curPos, food) > maxDis:
                maxDis = self.getMazeDistance(curPos, food)
                furthestFood = food
        return furthestFood

    def getNearestFood(self, gameState):
        nearestFood = None
        foods = self.getFood(gameState).asList()
        curPos = gameState.getAgentPosition(self.index)
        if len(foods) == 0:
            return (0, 0)
        minDis = 9999
        for food in foods:
            if self.getMazeDistance(curPos, food) <= minDis:
                minDis = self.getMazeDistance(curPos, food)
                nearestFood = food
        return nearestFood

    def getReward(self, gameState, action):
        nextState = gameState.generateSuccessor(self.index, action)
        pos = nextState.getAgentPosition(self.index)
        foods = self.getFood(gameState)
        furtestFood = self.getFurthestFood(gameState)
        nearestFood = self.getNearestFood(gameState)
        legalActions = gameState.getLegalActions(self.index)
        enemiesPos = [nextState.getAgentState(i).getPosition() for i in self.getOpponents(nextState)]

        if pos in enemiesPos:
            return -100
        if action not in legalActions:
            return -10
        elif pos in foods:
            return 100
        else:
            return 0
            #return float(1) / self.getMazeDistance(pos, nearestFood)

    def containFoodIn3(self, gameState):
        foods = self.getFood(gameState)
        curState = gameState
        nextAction1 = curState.getLegalActions(self.index)
        nextAction1.remove('Stop')
        for action1 in nextAction1:
            nextState1 = curState.generateSuccessor(self.index, action1)
            if nextState1.getAgentPosition(self.index) in foods:
                return True
            nextAction2 = nextState1.getLegalActions(self.index)
            nextAction2.remove('Stop')
            for action2 in nextAction2:
                nextState2 = nextState1.generateSuccessor(self.index, action2)
                if nextState2.getAgentPosition(self.index) in foods:
                    return True
                nextAction3 = nextState2.getLegalActions(self.index)
                nextAction3.remove('Stop')
                for action3 in nextAction3:
                    nextState3 = nextState2.generateSuccessor(self.index, action3)
                    if nextState3.getAgentPosition(self.index) in foods:
                        return True
        return False

    def nearestFoodIn3(self, gameState):
        '''
        foods = self.getFood(gameState)
        curState = gameState
        nextAction1 = curState.getLegalActions(self.index)
        #nextAction1.remove('Stop')
        for action1 in nextAction1:
            nextState1 = curState.generateSuccessor(self.index, action1)
            if nextState1.getAgentPosition(self.index) in foods:
                return nextState1.getAgentPosition(self.index)
            nextAction2 = nextState1.getLegalActions(self.index)
           # nextAction2.remove('Stop')
            for action2 in nextAction2:
                nextState2 = nextState1.generateSuccessor(self.index, action2)
                if nextState2.getAgentPosition(self.index) in foods:
                    return nextState2.getAgentPosition(self.index)
                nextAction3 = nextState2.getLegalActions(self.index)
                #nextAction3.remove('Stop')
                for action3 in nextAction3:
                    nextState3 = nextState2.generateSuccessor(self.index, action3)
                    if nextState3.getAgentPosition(self.index) in foods:
                        return nextState3.getAgentPosition(self.index)
        '''
        foods = self.getFood(gameState).asList()
        for food in foods:
            if self.getMazeDistance(food, gameState.getAgentPosition(self.index)) <= 3:
                return food




    def chooseAction(self, gameState):
        legalActions = gameState.getLegalActions(self.index)
        legalActions.remove('Stop')
        if util.flipCoin(self.epsilon):
            return random.choice(legalActions)
        elif not self.containFoodIn3(gameState):
            return self.getBestAction(gameState)
        else:
            for i in range(50):
                curState = gameState
                nearestFood = self.nearestFoodIn3(gameState)
                while curState.getAgentPosition(self.index) != nearestFood:
                    #curPos = curState.getAgentPosition(self.index)
                    legalActions = curState.getLegalActions(self.index)
                    legalActions.remove('Stop')
                    action = random.choice(legalActions)
                    nextState = curState.generateSuccessor(self.index, action)
                    reward = self.getReward(curState, action)
                    self.update(curState, action, nextState, reward)
                    curState = nextState
            return self.getBestAction(gameState)
