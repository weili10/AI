# search.py
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


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    from util import Stack

    pathStack = Stack()
    visitedList = [problem.getStartState()]
    actions = []

    DFSExplore(problem,problem.getStartState(),pathStack,visitedList)
    
    while not pathStack.isEmpty():
        actions.append(pathStack.pop()[1])

    actions.reverse()
    return actions


def  DFSExplore(problem, pos, pathStack, visitedList):
    if problem.isGoalState(pos):
        visitedList.append("END")
        return
    else:
        for successor in problem.getSuccessors(pos):     #successor((x,y),"direction",cost)
            if successor[0] not in visitedList and "END" not in visitedList:
                pathStack.push(successor)
                visitedList.append(successor[0])
                DFSExplore(problem, successor[0], pathStack, visitedList)
                if "END" not in visitedList:    #the path to the target didn't pass through this "pos"
                    pathStack.pop()


def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    from util import Queue
    
    pathQue = Queue()
    prev = {}    # {node:preNode}      node = ((x,y),"deriction",cost)
    startPos = (problem.getStartState(),None,0)
    visitedList = [startPos[0]]

    pathQue.push(startPos)
    
    while not pathQue.isEmpty():
        curPos = pathQue.pop()
        if problem.isGoalState(curPos[0]):
            return reconstructPath(prev,curPos)
     
        successors = problem.getSuccessors(curPos[0])
        for successor in successors:
            if successor[0] not in visitedList:
                pathQue.push(successor)
                prev[successor] = curPos
                visitedList.append(successor[0])
    return []

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    from util import PriorityQueue
    import sys

    startPos = (problem.getStartState(),None,0)
    dis = {startPos[0]:0}
    prev = {}
    visitedPos = []
    actions = []


    pathPQue = PriorityQueue()
    pathPQue.push(startPos,dis[startPos[0]])
    while not pathPQue.isEmpty():
        curPos = pathPQue.pop()
        # print "for position:",curPos,"distance:",dis[curPos[0]]
        # print "its successors are:"
        if problem.isGoalState(curPos[0]):
            return reconstructPath(prev, curPos)

        visitedPos.append(curPos[0])
        #print "curPos:", curPos
        
        successors = problem.getSuccessors(curPos[0])
        #print 'successors:',successors
        for successor in successors:

            if successor[0] in visitedPos:
                continue

            if successor[0] not in dis:
                dis[successor[0]] = sys.maxint    #test case cantains 10^7 value
                pathPQue.push(successor, dis[successor[0]])
            # print "successor:",successor,"dis:",dis[successor[0]]
            if dis[curPos[0]] + successor[2] < dis[successor[0]]:
                dis[successor[0]] = dis[curPos[0]] + successor[2]
                prev[successor] = curPos
                pathPQue.update(successor,dis[successor[0]])
    return []



def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    #util.raiseNotDefined()
    from util import PriorityQueue
    import sys

    openSet =  PriorityQueue()
    closeSet = []
    startPos = (problem.getStartState(),None,0)
    openSet.push(startPos,heuristic(startPos[0],problem))
    #startPosCo = getCoordinate(startPos)
    gs = {startPos[0]:0}
    hs = {startPos[0]:heuristic(startPos[0],problem)}
    prev = {}
    isEnd = False
    target = None
    actions = []

    while not openSet.isEmpty():
        curPos = openSet.pop()
        if problem.isGoalState(curPos[0]):
            return reconstructPath(prev,curPos)

        closeSet.append(curPos[0])
        
        successors = problem.getSuccessors(curPos[0])
        for successor in successors:
            if successor[0] in closeSet:
                continue

            if successor[0] not in gs:
                gs[successor[0]] = sys.maxint
                hs[successor[0]] = heuristic(successor[0],problem)
                openSet.push(successor,gs[successor[0]]+hs[successor[0]])

            ngs = gs[curPos[0]] + successor[2]
            if ngs < gs[successor[0]]:
                gs[successor[0]] = ngs
                prev[successor] = curPos
                openSet.update(successor,gs[successor[0]]+hs[successor[0]])
    return []

def reconstructPath(prev,curPos):
    actions = [curPos[1]]
    while curPos in prev:
        curPos = prev[curPos]
        actions.append(curPos[1])

    actions.reverse()
    return actions[1:]   #remove 'None' from the startPos

# to fix the bug that the state contains not only the coordinate but also a list of corners. 
# (list is unhashable for dictionary in python)
def getCoordinate(state):
    coordinate = state[0]
    while type(coordinate[0]) == type((0,0)):
        coordinate = coordinate[0]
    return coordinate


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
