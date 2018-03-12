from search import dfs,bfs,ucs,astar

"""
expending x represents calling getSuccessor(x)
"""

class problem():
    successors = []
    startState = []
    goalState = []
# ***     graph:
# ***          B   
# ***          ^
# ***          |
# ***         *A --> C --> G
# ***          |
# ***          V
# ***          D 
    successors.append([
                ['A',   ('D','A->D',1), ('C','A->C',1), ('B','A->B',1) ],
                ['C',   ('G','C->G',1) ]
                ])
    startState.append('A')
    goalState.append('G')


# ***     graph:
# ***         /-- B
# ***         |   ^
# ***         |   |
# ***         |  *A -->[G]
# ***         |   |     ^
# ***         |   V     |
# ***         \-->D ----/

    successors.append([
                ['A',   ('D','A->D',1), ('G','A->G',1), ('B','A->B',1) ],
                ['B',   ('D','B->D',2)],
                ['D',   ('G','D->G',2)]
                ])
    startState.append('A')
    goalState.append('G')

# ***     graph:
# ***          B <--> C
# ***          ^     /|
# ***          |    / |
# ***          V   /  V
# ***         *A<-/  [G]

    successors.append([
                ['A',   ('B','A->B',1) ],
                ['B',   ('C','B->C',4),('A','B->A',2)],
                ['C',   ('B','C->B',32),('A','C->A',8),('G','C->G',16)]
                ])
    startState.append('A')
    goalState.append('G')


    def __init__(self,index = 0):
        self.index = index


    def getStartState(self):
        return self.startState[self.index]

    def isGoalState(self,pos):
        if pos == self.goalState[self.index]:
            return True
        else:
            return False

    def getSuccessors(self,pos):
        for node in self.successors[self.index]:
            if pos == node[0]:
                node.remove(pos)
                return node
        return []


if __name__ == '__main__':
    problem = problem(2)
    actions = astar(problem)
    print actions





