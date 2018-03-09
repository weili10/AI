Authors: 
Wei Li      wli10@student.unimelb.edu.au    
Jiahao Yu   jiahaoy@student.unimelb.edu.au 
Xing Fan    xfan2@student.unimelb.edu.au 

date: 15-10-2017


################################
###  Approaches Implemented  ###
################################

1.Astar algorithm to find the shortest path to the goal state.

2.Pruning methods to reduce the search space. 

3.the game theoretic methods to determine the goal state.


################################
###     code documentation   ###
################################

### the Astar attacker class ###
class AstarAgent(CaptureAgent)

    ## register the initial state of the game
    def registerInitialState(self, gameState)

    ## get next state of applying the action
    def getSuccessor(self, gameState, action)

    ## set current features used to make desicions
    def setCurFeatures(self,gameState)

    ## choose action base on current features   
    def chooseAction(self,gameState)

    ## choose actions according to current situation
    def chooseAttackAction(self, gameState)

    ## use astar algorithm to search the goal state
    def aStarEatFood(self, gameState)

    ## calculate the heuristic distence to a state
    def heuristicFoodDistance(self, gameState)

    ## reach the goal state of aStarEatFood
    def shouldGoBack(self, gameState)

    ## reconstructPath form state link list prev and the current state
    def reconstructPath(self, prev, curState)

    ## astar to find the shortest path to go back to the gaolPos
    def aStarGoBack(self, gameState, gaolPos)

    ## heuristic distance to go back to the goalPos
    def heuristicBackDistance(self, gameState, goalPos)

### defense agent using astar algorithm ###
class DefensiveAStarAgent(CaptureAgent)
    
    ## register initial game state
    def registerInitialState(self, gameState)

    ## get next state of applying the action
    def getSuccessor(self, gameState, action)

    ## calculate heuristic distance (mazdistance)
    def heuristic(self, a, b)

    ## get the position of lost food
    def checkFoodList(self,gameState)

    ## choose a defense action base on current gamestate
    def chooseAction(self, gameState)

    ## find the goal state of Astar search
    def goalDefiner(self, gameState)

    ## astar serch the shortest path to goal position
    def aStarSearch(self, gameState, goalCoord)

    ## get successor state in format of (state, action, cost)
    def UpdateSuccessor(self, gameState)



