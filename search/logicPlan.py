# logicPlan.py
# ------------
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

# Project 2 - Gabriele Granzotto - Universita' degli studi di Trieste - Artificial Intelligence and Data Analytics -  Introduction to AI

"""
In logicPlan.py, you will implement logic planning methods which are called by
Pacman agents (in logicAgents.py).
"""

from typing import Dict, List, Tuple, Callable, Generator, Any
import util
import sys
import logic
import game

from logic import conjoin, disjoin
from logic import PropSymbolExpr, Expr, to_cnf, pycoSAT, parseExpr, pl_true

import itertools
import copy

pacman_str = 'P'
food_str = 'FOOD'
wall_str = 'WALL'
pacman_wall_str = pacman_str + wall_str
DIRECTIONS = ['North', 'South', 'East', 'West']
blocked_str_map = dict([(direction, (direction + "_blocked").upper()) for direction in DIRECTIONS])
geq_num_adj_wall_str_map = dict([(num, "GEQ_{}_adj_walls".format(num)) for num in range(1, 4)])
DIR_TO_DXDY_MAP = {'North':(0, 1), 'South':(0, -1), 'East':(1, 0), 'West':(-1, 0)}


#______________________________________________________________________________
# QUESTION 1

def sentence1() -> Expr:
    """Returns a Expr instance that encodes that the following expressions are all true.
    
    A or B
    (not A) if and only if ((not B) or C)
    (not A) or (not B) or C
    """
    "*** BEGIN YOUR CODE HERE ***"
    # declaration of 3 variables
    A = Expr('A')                                                   
    B = Expr('B')
    C = Expr('C')
    # return the CNF of 3 expressions
    return conjoin((A|B), (~A%(~B|C)), (disjoin(~A,~B,C)))                        
    "*** END YOUR CODE HERE ***"


def sentence2() -> Expr:
    """Returns a Expr instance that encodes that the following expressions are all true.
    
    C if and only if (B or D)
    A implies ((not B) and (not D))
    (not (B and (not C))) implies A
    (not D) implies C
    """
    "*** BEGIN YOUR CODE HERE ***"
    # declaration of 4 variables
    A = Expr('A')                                                   
    B = Expr('B')
    C = Expr('C')
    D = Expr('D')
    # return the CNF of 3 expressions
    return conjoin((C%(B|D)), (A>>(~B&~D)), (~(B&~C)>>A), ~D>>C)    
    "*** END YOUR CODE HERE ***"


def sentence3() -> Expr:
    """Using the symbols PacmanAlive_1 PacmanAlive_0, PacmanBorn_0, and PacmanKilled_0,
    created using the PropSymbolExpr constructor, return a PropSymbolExpr
    instance that encodes the following English sentences (in this order):

    Pacman is alive at time 1 if and only if Pacman was alive at time 0 and it was
    not killed at time 0 or it was not alive at time 0 and it was born at time 0.

    Pacman cannot both be alive at time 0 and be born at time 0.

    Pacman is born at time 0.
    """
    "*** BEGIN YOUR CODE HERE ***"
    # declaration of 4 expressions
    PacmanAlive_1 = PropSymbolExpr('PacmanAlive_1')
    PacmanAlive_0 = PropSymbolExpr('PacmanAlive_0')
    PacmanBorn_0 = PropSymbolExpr('PacmanBorn_0')
    PacmanKilled_0 = PropSymbolExpr('PacmanKilled_0')
    # return the CNF of 3 expressions
    return conjoin(PacmanAlive_1 % ((PacmanAlive_0 & ~PacmanKilled_0)|(~PacmanAlive_0&PacmanBorn_0)), ~(PacmanAlive_0 & PacmanBorn_0), PacmanBorn_0)
    "*** END YOUR CODE HERE ***"

def findModel(sentence: Expr) -> Dict[Expr, bool]:
    """Given a propositional logic sentence (i.e. a Expr instance), returns a satisfying
    model if one exists. Otherwise, returns False.
    """
    cnf_sentence = to_cnf(sentence)
    return pycoSAT(cnf_sentence)

def findModelUnderstandingCheck() -> Dict[Expr, bool]:
    """Returns the result of findModel(Expr('a')) if lower cased expressions were allowed.
    You should not use findModel or Expr in this method.
    """
    class relabelled:
        """We have to find a way to pass a non capital letter variable name but
        when printed result like a capital letter
        """
        def __init__(self, name: str = 'A'):
            self.name = name
        
        def __repr__(self):
            return self.name
        
    "*** BEGIN YOUR CODE HERE ***"
    # return a Dictionary with only one element, using "relabelled" class 
    return {relabelled('a'): True}
    "*** END YOUR CODE HERE ***"

def entails(premise: Expr, conclusion: Expr) -> bool:
    """Returns True if the premise entails the conclusion and False otherwise.
    """
    "*** BEGIN YOUR CODE HERE ***"
    # findModel try to resolve the logic model and the logic fomula is the definition of entails 
    if not findModel(premise&~conclusion):
        return True
    else:
        return False
    "*** END YOUR CODE HERE ***"

def plTrueInverse(assignments: Dict[Expr, bool], inverse_statement: Expr) -> bool:
    """Returns True if the (not inverse_statement) is True given assignments and False otherwise.
    pl_true may be useful here; see logic.py for its description.
    """
    "*** BEGIN YOUR CODE HERE ***"
    return pl_true(~inverse_statement, assignments)
    "*** END YOUR CODE HERE ***"

#______________________________________________________________________________
# QUESTION 2

def atLeastOne(literals: List[Expr]) -> Expr:
    """
    Given a list of Expr literals (i.e. in the form A or ~A), return a single 
    Expr instance in CNF (conjunctive normal form) that represents the logic 
    that at least one of the literals  ist is true.
    >>> A = PropSymbolExpr('A');
    >>> B = PropSymbolExpr('B');
    >>> symbols = [A, B]
    >>> atleast1 = atLeastOne(symbols)
    >>> model1 = {A:False, B:False}
    >>> print(pl_true(atleast1,model1))
    False
    >>> model2 = {A:False, B:True}
    >>> print(pl_true(atleast1,model2))
    True
    >>> model3 = {A:True, B:True}
    >>> print(pl_true(atleast1,model2))
    True
    """
    "*** BEGIN YOUR CODE HERE ***"
    # for an atLeastOne we need only one correct literals, so the DNF is what we want
    return disjoin(literals)
    "*** END YOUR CODE HERE ***"


def atMostOne(literals: List[Expr]) -> Expr:
    """
    Given a list of Expr literals, return a single Expr instance in 
    CNF (conjunctive normal form) that represents the logic that at most one of 
    the expressions in the list is true.
    itertools.combinations may be useful here.
    """
    "*** BEGIN YOUR CODE HERE ***"
    # all combinations of 2 literals
    combinatory = list(itertools.combinations(literals,2))
    # we have to make a list where all literals are "or the negation of 1 or the negation of the other"
    at_most_one_literal = []
    for item in combinatory:
        at_most_one_literal.append(~item[0]|~item[1])
    # we need all combinations to be true, so we have to apply the CNF to the combinatory list
    return(conjoin(at_most_one_literal))
    "*** END YOUR CODE HERE ***"


def exactlyOne(literals: List[Expr]) -> Expr:
    """
    Given a list of Expr literals, return a single Expr instance in 
    CNF (conjunctive normal form)that represents the logic that exactly one of 
    the expressions in the list is true.
    """
    "*** BEGIN YOUR CODE HERE ***"
    # we want exactly one, so we want at least one AND at most one, we have to combine the two previewsly classes
    return (atLeastOne(literals) & atMostOne(literals))
    "*** END YOUR CODE HERE ***"

#______________________________________________________________________________
# QUESTION 3

def pacmanSuccessorAxiomSingle(x: int, y: int, time: int, walls_grid: List[List[bool]]=None) -> Expr:
    """
    Successor state axiom for state (x,y,t) (from t-1), given the board (as a 
    grid representing the wall locations).
    Current <==> (previous position at time t-1) & (took action to move to x, y)
    Available actions are ['North', 'East', 'South', 'West']
    Note that STOP is not an available action.
    """
    now, last = time, time - 1
    possible_causes: List[Expr] = [] # enumerate all possible causes for P[x,y]_t
    # the if statements give a small performance boost and are required for q4 and q5 correctness
    if walls_grid[x][y+1] != 1:
        possible_causes.append( PropSymbolExpr(pacman_str, x, y+1, time=last)
                            & PropSymbolExpr('South', time=last))
    if walls_grid[x][y-1] != 1:
        possible_causes.append( PropSymbolExpr(pacman_str, x, y-1, time=last) 
                            & PropSymbolExpr('North', time=last))
    if walls_grid[x+1][y] != 1:
        possible_causes.append( PropSymbolExpr(pacman_str, x+1, y, time=last) 
                            & PropSymbolExpr('West', time=last))
    if walls_grid[x-1][y] != 1:
        possible_causes.append( PropSymbolExpr(pacman_str, x-1, y, time=last) 
                            & PropSymbolExpr('East', time=last))
    if not possible_causes:
        return None
    
    "*** BEGIN YOUR CODE HERE ***"
    # we have to evalate what are the next moves of pacman so 
    # (pacman is in that position) <=> (pacman can do one of this moves and can go in the corrisponding position)
    return PropSymbolExpr(pacman_str, x, y, time=now) % disjoin(possible_causes)
    "*** END YOUR CODE HERE ***"


def SLAMSuccessorAxiomSingle(x: int, y: int, time: int, walls_grid: List[List[bool]]) -> Expr:
    """
    Similar to `pacmanSuccessorStateAxioms` but accounts for illegal actions
    where the pacman might not move timestep to timestep.
    Available actions are ['North', 'East', 'South', 'West']
    """
    now, last = time, time - 1
    moved_causes: List[Expr] = [] # enumerate all possible causes for P[x,y]_t, assuming moved to having moved
    if walls_grid[x][y+1] != 1:
        moved_causes.append( PropSymbolExpr(pacman_str, x, y+1, time=last)
                            & PropSymbolExpr('South', time=last))
    if walls_grid[x][y-1] != 1:
        moved_causes.append( PropSymbolExpr(pacman_str, x, y-1, time=last) 
                            & PropSymbolExpr('North', time=last))
    if walls_grid[x+1][y] != 1:
        moved_causes.append( PropSymbolExpr(pacman_str, x+1, y, time=last) 
                            & PropSymbolExpr('West', time=last))
    if walls_grid[x-1][y] != 1:
        moved_causes.append( PropSymbolExpr(pacman_str, x-1, y, time=last) 
                            & PropSymbolExpr('East', time=last))
    if not moved_causes:
        return None

    moved_causes_sent: Expr = conjoin([~PropSymbolExpr(pacman_str, x, y, time=last) , ~PropSymbolExpr(wall_str, x, y), disjoin(moved_causes)])

    failed_move_causes: List[Expr] = [] # using merged variables, improves speed significantly
    auxilary_expression_definitions: List[Expr] = []
    for direction in DIRECTIONS:
        dx, dy = DIR_TO_DXDY_MAP[direction]
        wall_dir_clause = PropSymbolExpr(wall_str, x + dx, y + dy) & PropSymbolExpr(direction, time=last)
        wall_dir_combined_literal = PropSymbolExpr(wall_str + direction, x + dx, y + dy, time=last)
        failed_move_causes.append(wall_dir_combined_literal)
        auxilary_expression_definitions.append(wall_dir_combined_literal % wall_dir_clause)

    failed_move_causes_sent: Expr = conjoin([
        PropSymbolExpr(pacman_str, x, y, time=last),
        disjoin(failed_move_causes)])

    return conjoin([PropSymbolExpr(pacman_str, x, y, time=now) % disjoin([moved_causes_sent, failed_move_causes_sent])] + auxilary_expression_definitions)


def pacphysicsAxioms(t: int, all_coords: List[Tuple], non_outer_wall_coords: List[Tuple], walls_grid: List[List] = None, sensorModel: Callable = None, successorAxioms: Callable = None) -> Expr:
    """
    Given:
        t: timestep
        all_coords: list of (x, y) coordinates of the entire problem
        non_outer_wall_coords: list of (x, y) coordinates of the entire problem,
            excluding the outer border (these are the actual squares pacman can
            possibly be in)
        walls_grid: 2D array of either -1/0/1 or T/F. Used only for successorAxioms.
            Do NOT use this when making possible locations for pacman to be in.
        sensorModel(t, non_outer_wall_coords) -> Expr: function that generates
            the sensor model axioms. If None, it's not provided, so shouldn't be run.
        successorAxioms(t, walls_grid, non_outer_wall_coords) -> Expr: function that generates
            the sensor model axioms. If None, it's not provided, so shouldn't be run.
    Return a logic sentence containing all of the following:
        - for all (x, y) in all_coords:
            If a wall is at (x, y) --> Pacman is not at (x, y)
        - Pacman is at exactly one of the squares at timestep t.
        - Pacman takes exactly one action at timestep t.
        - Results of calling sensorModel(...), unless None.
        - Results of calling successorAxioms(...), describing how Pacman can end in various
            locations on this time step. Consider edge cases. Don't call if None.
    """
    pacphysics_sentences = []

    "*** BEGIN YOUR CODE HERE ***"
    # 1- (there is a wall) => (there is no pacman) 
    for (x,y) in all_coords:
        pacphysics_sentences.append(PropSymbolExpr(wall_str, x, y) >> ~PropSymbolExpr(pacman_str, x, y, time=t))

    # 2- there is exactly one pacman per time in all the map
    position_pacman = []
    for (x,y) in non_outer_wall_coords:
        position_pacman.append(PropSymbolExpr(pacman_str, x, y, time=t))
    pacphysics_sentences.append(exactlyOne(position_pacman))

    # 3- pacman can make only one action per time
    pacman_actions = []
    for action in DIRECTIONS:
        pacman_actions.append(PropSymbolExpr(action, time=t))
    pacphysics_sentences.append(exactlyOne(pacman_actions))

    # 4- use sensorModel to look around
    if sensorModel is not None:
        pacphysics_sentences.append(sensorModel(t, non_outer_wall_coords=non_outer_wall_coords))

    # 5- the rules to move pacman
    if successorAxioms is not None and t>0:
        pacphysics_sentences.append(successorAxioms(t, walls_grid, non_outer_wall_coords=non_outer_wall_coords))
    "*** END YOUR CODE HERE ***"
    return conjoin(pacphysics_sentences)


def checkLocationSatisfiability(x1_y1: Tuple[int, int], x0_y0: Tuple[int, int], action0, action1, problem):
    """
    Given:
        - x1_y1 = (x1, y1), a potential location at time t = 1
        - x0_y0 = (x0, y0), Pacman's location at time t = 0
        - action0 = one of the four items in DIRECTIONS, Pacman's action at time t = 0
        - action1 = to ensure match with autograder solution
        - problem = an instance of logicAgents.LocMapProblem
    Note:
        - there's no sensorModel because we know everything about the world
        - the successorAxioms should be allLegalSuccessorAxioms where needed
    Return:
        - a model where Pacman is at (x1, y1) at time t = 1
        - a model where Pacman is not at (x1, y1) at time t = 1
    """
    walls_grid = problem.walls
    walls_list = walls_grid.asList()
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))
    KB = []
    x0, y0 = x0_y0
    x1, y1 = x1_y1

    # We know which coords are walls:
    map_sent = [PropSymbolExpr(wall_str, x, y) for x, y in walls_list]
    KB.append(conjoin(map_sent))

    "*** BEGIN YOUR CODE HERE ***"
    # 1- append all the axioms at Knowledge Base at time 0 and 1
    KB.append(pacphysicsAxioms(t = 0, 
                               all_coords = all_coords, 
                               non_outer_wall_coords = non_outer_wall_coords, 
                               walls_grid = walls_grid, 
                               sensorModel = None, 
                               successorAxioms = allLegalSuccessorAxioms))   
    KB.append(pacphysicsAxioms(t = 1, 
                               all_coords = all_coords, 
                               non_outer_wall_coords = non_outer_wall_coords, 
                               walls_grid = walls_grid, 
                               sensorModel = None, 
                               successorAxioms = allLegalSuccessorAxioms)) 
    
    # 2- current location of pacman at time 0 added to Knowledge Base
    KB.append(PropSymbolExpr(pacman_str, x0, y0, time = 0)) 
    
    # 3- Action 0 and 1 added to Knowledge Base
    KB.append(PropSymbolExpr(action0, time = 0))
    KB.append(PropSymbolExpr(action1, time = 1))
    
    # 4- Evaluation of model1 and model2
    conjoin_KB = conjoin(KB)
    in_position = PropSymbolExpr(pacman_str, x1, y1, time = 1)
    model1 = findModel(conjoin(conjoin_KB, in_position))
    model2 = findModel(conjoin(conjoin_KB, ~in_position))
    return (model1, model2)
    "*** END YOUR CODE HERE ***"

#______________________________________________________________________________
# QUESTION 4

def positionLogicPlan(problem) -> List:
    """
    Given an instance of a PositionPlanningProblem, return a list of actions that lead to the goal.
    Available actions are ['North', 'East', 'South', 'West']
    Note that STOP is not an available action.
    Overview: add knowledge incrementally, and query for a model each timestep. Do NOT use pacphysicsAxioms.
    """
    walls_grid = problem.walls
    width, height = problem.getWidth(), problem.getHeight()
    walls_list = walls_grid.asList()
    x0, y0 = problem.startState
    xg, yg = problem.goal
    
    # Get lists of possible locations (i.e. without walls) and possible actions
    all_coords = list(itertools.product(range(width + 2), 
            range(height + 2)))
    non_wall_coords = [loc for loc in all_coords if loc not in walls_list]
    actions = [ 'North', 'South', 'East', 'West' ]
    KB = []

    "*** BEGIN YOUR CODE HERE ***"
    # 1- current location of pacman at time 0 added to Knowledge Base
    KB.append(PropSymbolExpr(pacman_str, x0, y0, time = 0))

    for t in range(50):
        print(t)
        # 2- in the map there must be exactly one pacman
        location = []
        for (x,y) in non_wall_coords:
            location.append(PropSymbolExpr(pacman_str, x, y, time = t))
        KB.append(exactlyOne(location))

        # 3- if we find a model we can return the action sequence...
        model = findModel(conjoin(PropSymbolExpr(pacman_str, xg, yg, time = t), conjoin(KB)))  
        if model:
            return extractActionSequence(model, actions)  
        
        # 4- ...otherwise we choose exactly one action
        action_x_ts = []
        for action in actions:
            action_x_ts.append(PropSymbolExpr(action, time = t))
        KB.append(exactlyOne(action_x_ts))
        
        # 5- we check that the pacman next location is not in a wall cell
        for (x,y) in non_wall_coords:
            KB.append(pacmanSuccessorAxiomSingle(x, y, t+1, walls_grid))
    "*** END YOUR CODE HERE ***"

#______________________________________________________________________________
# QUESTION 5

def foodLogicPlan(problem) -> List:
    """
    Given an instance of a FoodPlanningProblem, return a list of actions that help Pacman
    eat all of the food.
    Available actions are ['North', 'East', 'South', 'West']
    Note that STOP is not an available action.
    Overview: add knowledge incrementally, and query for a model each timestep. Do NOT use pacphysicsAxioms.
    """
    walls = problem.walls
    width, height = problem.getWidth(), problem.getHeight()
    walls_list = walls.asList()
    (x0, y0), food = problem.start
    food = food.asList()

    # Get lists of possible locations (i.e. without walls) and possible actions
    all_coords = list(itertools.product(range(width + 2), range(height + 2)))

    non_wall_coords = [loc for loc in all_coords if loc not in walls_list]
    actions = [ 'North', 'South', 'East', 'West' ]

    KB = []

    "*** BEGIN YOUR CODE HERE ***"
    # 1- current location of pacman at time 0 added to Knowledge Base
    KB.append(PropSymbolExpr(pacman_str, x0, y0, time = 0))

    # 2- add all the foods locations in the Knowledge Base 
    for (x,y) in food:
        KB.append(PropSymbolExpr(food_str, x, y, time = 0))

    for t in range(50):
        print(t)

        # 3- if pacman is in a food cell we add to eated_food
        eated_food = []
        for (x,y) in food:
            eated_food.append(PropSymbolExpr(food_str, x, y, time = t))

        # 4- in the map there must be exactly one pacman
        location = []
        for (x,y) in non_wall_coords:
            location.append(PropSymbolExpr(pacman_str, x, y, time = t))
        KB.append(exactlyOne(location))

        # 5- we choose exactly one action
        action_x_ts = []
        for action in actions:
            action_x_ts.append(PropSymbolExpr(action, time = t))
        KB.append(exactlyOne(action_x_ts))
        
        # 6- we check that the pacman next location is not in a wall cell
        for (x,y) in non_wall_coords:
            KB.append(pacmanSuccessorAxiomSingle(x, y, t+1, walls))

        # 7- ((pacman is in position (x,y)) OR (food is NOT in position (x,y)) in time t) <=> (food is not in position (x,y) in time t+1)
        for (x,y) in all_coords:
            KB.append(( PropSymbolExpr(pacman_str,x,y,time = t) | ~PropSymbolExpr(food_str,x,y,time = t)) % ~PropSymbolExpr(food_str,x,y,time=t+1))

        # 8- find a model that all the food have been eated and the conditions are respected 
        food_conditions = ~disjoin(eated_food)
        model = findModel(conjoin(food_conditions, conjoin(KB)))
        
        # 9- if we find a model we can return the action sequence
        if model:
            return extractActionSequence(model, actions)
    "*** END YOUR CODE HERE ***"

#______________________________________________________________________________
# QUESTION 6

def localization(problem, agent) -> Generator:
    '''
    problem: a LocalizationProblem instance
    agent: a LocalizationLogicAgent instance
    '''
    walls_grid = problem.walls
    walls_list = walls_grid.asList()
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))

    KB = []

    "*** BEGIN YOUR CODE HERE ***"
    # 1- add all the wall information to the Knowledge Base
    for (x,y) in all_coords:
        if (x,y) in walls_list:
            KB.append(PropSymbolExpr(wall_str, x, y))
        else:
            KB.append(~PropSymbolExpr(wall_str, x, y))

    for t in range(agent.num_timesteps):
        # 2- append the physics axioms to the Knowledge Base
        KB.append(pacphysicsAxioms(t = t, 
                                   all_coords = all_coords, 
                                   non_outer_wall_coords = non_outer_wall_coords, 
                                   walls_grid = walls_grid, 
                                   sensorModel = sensorAxioms, 
                                   successorAxioms = allLegalSuccessorAxioms))
        # 3- add the possible actions
        KB.append(PropSymbolExpr(agent.actions[t], time = t))
        
        # 4- check the wall perception around pacman
        KB.append(fourBitPerceptRules(t, agent.getPercepts()))

        # 5- check all the possible solutions of the logic expression, if we can't find an unique solution let's move on
        possible_locations = []
        for (x,y) in non_outer_wall_coords:
            sol_KB = conjoin(KB)
            pacman_loc = PropSymbolExpr(pacman_str, x, y, time = t)
            if findModel(conjoin(sol_KB, pacman_loc)):
                possible_locations.append((x,y))
            if entails(sol_KB, pacman_loc):
                KB.append(pacman_loc)
            elif entails(sol_KB, ~pacman_loc):
                KB.append(~pacman_loc)
        agent.moveToNextState(agent.actions[t])
        "*** END YOUR CODE HERE ***"
        yield possible_locations

#______________________________________________________________________________
# QUESTION 7

def mapping(problem, agent) -> Generator:
    '''
    problem: a MappingProblem instance
    agent: a MappingLogicAgent instance
    '''
    pac_x_0, pac_y_0 = problem.startState
    KB = []
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))

    # map describes what we know, for GUI rendering purposes. -1 is unknown, 0 is open, 1 is wall
    known_map = [[-1 for y in range(problem.getHeight()+2)] for x in range(problem.getWidth()+2)]

    # Pacman knows that the outer border of squares are all walls
    outer_wall_sent = []
    for x, y in all_coords:
        if ((x == 0 or x == problem.getWidth() + 1)
                or (y == 0 or y == problem.getHeight() + 1)):
            known_map[x][y] = 1
            outer_wall_sent.append(PropSymbolExpr(wall_str, x, y))
    KB.append(conjoin(outer_wall_sent))

    "*** BEGIN YOUR CODE HERE ***"
    # 1- append initial position to Knowledge Base
    KB.append(PropSymbolExpr(pacman_str, pac_x_0, pac_y_0, time = 0))

    # 2- add to the Knowledge Base if cells around the actual cell are walls 
    if known_map[pac_x_0][pac_y_0] == 1:
        KB.append(PropSymbolExpr(wall_str, pac_x_0, pac_y_0))
    elif known_map[pac_x_0][pac_y_0] == 0:
        KB.append(~PropSymbolExpr(wall_str, pac_x_0, pac_y_0))

    for t in range(agent.num_timesteps):
        # 3- add the physics axioms to the Knowledge Base
        KB.append(pacphysicsAxioms(t = t, 
                                   all_coords = all_coords, 
                                   non_outer_wall_coords = non_outer_wall_coords, 
                                   walls_grid = known_map, 
                                   sensorModel = sensorAxioms, 
                                   successorAxioms = allLegalSuccessorAxioms))
        
        # 4- add the possible actions
        KB.append(PropSymbolExpr(agent.actions[t], time = t))

        # 5- check the wall perception around pacman
        KB.append(fourBitPerceptRules(t, agent.getPercepts()))

        # 6- if we find a wall in an adjacent cell we set to 1 in known_map and add that to Knowledge Base, than move to next state 
        for (x,y) in non_outer_wall_coords:
            sol_KB = conjoin(KB)
            wall_loc = PropSymbolExpr(wall_str, x, y)
            if entails(sol_KB, wall_loc):
                KB.append(wall_loc)
                known_map[x][y] = 1
            elif entails(sol_KB, ~wall_loc):
                KB.append(~wall_loc)
                known_map[x][y] = 0
        agent.moveToNextState(agent.actions[t])
        "*** END YOUR CODE HERE ***"
        yield known_map

#______________________________________________________________________________
# QUESTION 8

def slam(problem, agent) -> Generator:
    '''
    problem: a SLAMProblem instance
    agent: a SLAMLogicAgent instance
    '''
    pac_x_0, pac_y_0 = problem.startState
    KB = []
    all_coords = list(itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)))
    non_outer_wall_coords = list(itertools.product(range(1, problem.getWidth()+1), range(1, problem.getHeight()+1)))

    # map describes what we know, for GUI rendering purposes. -1 is unknown, 0 is open, 1 is wall
    known_map = [[-1 for y in range(problem.getHeight()+2)] for x in range(problem.getWidth()+2)]

    # We know that the outer_coords are all walls.
    outer_wall_sent = []
    for x, y in all_coords:
        if ((x == 0 or x == problem.getWidth() + 1)
                or (y == 0 or y == problem.getHeight() + 1)):
            known_map[x][y] = 1
            outer_wall_sent.append(PropSymbolExpr(wall_str, x, y))
    KB.append(conjoin(outer_wall_sent))

    "*** BEGIN YOUR CODE HERE ***"
    # 1- append initial position to Knowledge Base
    KB.append(PropSymbolExpr(pacman_str, pac_x_0, pac_y_0, time = 0))

    # 2- add to the Knowledge Base if cells around the actual cell are walls 
    if known_map[pac_x_0][pac_y_0] == 1:
        KB.append(PropSymbolExpr(wall_str, pac_x_0, pac_y_0))
    elif known_map[pac_x_0][pac_y_0] == 0:
        KB.append(~PropSymbolExpr(wall_str, pac_x_0, pac_y_0))    

    for t in range(agent.num_timesteps):
        # 3- add the physics axioms to the Knowledge Base
        KB.append(pacphysicsAxioms(t = t, 
                                   all_coords = all_coords, 
                                   non_outer_wall_coords = non_outer_wall_coords, 
                                   walls_grid = known_map, 
                                   sensorModel = SLAMSensorAxioms, 
                                   successorAxioms = SLAMSuccessorAxioms))
        # 4- add the possible actions
        KB.append(PropSymbolExpr(agent.actions[t], time = t))

        # 5- check the wall perception around pacman
        KB.append(numAdjWallsPerceptRules(t, agent.getPercepts()))   

        # 6- if we find a wall in an adjacent cell we set to 1 in known_map and add that to Knowledge Base...
        # ...check all the possible solutions of the logic expression...
        # ...if we can't find an unique solution let's move to next state
        possible_locations = []
        for (x,y) in non_outer_wall_coords:
            sol_KB = conjoin(KB)
            wall_loc = PropSymbolExpr(wall_str, x, y)
            pacman_loc = PropSymbolExpr(pacman_str, x, y, time = t)
            if entails(sol_KB, wall_loc):
                KB.append(wall_loc)
                known_map[x][y] = 1
            elif entails(sol_KB, ~wall_loc):
                KB.append(~wall_loc)
                known_map[x][y] = 0    
            if findModel(conjoin(sol_KB, pacman_loc)):
                possible_locations.append((x,y))
            if entails(sol_KB, pacman_loc):
                KB.append(pacman_loc)
            elif entails(sol_KB, ~pacman_loc):
                KB.append(~pacman_loc)   
        agent.moveToNextState(agent.actions[t])  
        "*** END YOUR CODE HERE ***"
        yield (known_map, possible_locations)


# Abbreviations
plp = positionLogicPlan
loc = localization
mp = mapping
flp = foodLogicPlan
# Sometimes the logic module uses pretty deep recursion on long expressions
sys.setrecursionlimit(100000)

#______________________________________________________________________________
# Important expression generating functions, useful to read for understanding of this project.


def sensorAxioms(t: int, non_outer_wall_coords: List[Tuple[int, int]]) -> Expr:
    all_percept_exprs = []
    combo_var_def_exprs = []
    for direction in DIRECTIONS:
        percept_exprs = []
        dx, dy = DIR_TO_DXDY_MAP[direction]
        for x, y in non_outer_wall_coords:
            combo_var = PropSymbolExpr(pacman_wall_str, x, y, x + dx, y + dy, time=t)
            percept_exprs.append(combo_var)
            combo_var_def_exprs.append(combo_var % (
                PropSymbolExpr(pacman_str, x, y, time=t) & PropSymbolExpr(wall_str, x + dx, y + dy)))

        percept_unit_clause = PropSymbolExpr(blocked_str_map[direction], time = t)
        all_percept_exprs.append(percept_unit_clause % disjoin(percept_exprs))

    return conjoin(all_percept_exprs + combo_var_def_exprs)


def fourBitPerceptRules(t: int, percepts: List) -> Expr:
    """
    Localization and Mapping both use the 4 bit sensor, which tells us True/False whether
    a wall is to pacman's north, south, east, and west.
    """
    assert isinstance(percepts, list), "Percepts must be a list."
    assert len(percepts) == 4, "Percepts must be a length 4 list."

    percept_unit_clauses = []
    for wall_present, direction in zip(percepts, DIRECTIONS):
        percept_unit_clause = PropSymbolExpr(blocked_str_map[direction], time=t)
        if not wall_present:
            percept_unit_clause = ~PropSymbolExpr(blocked_str_map[direction], time=t)
        percept_unit_clauses.append(percept_unit_clause) # The actual sensor readings
    return conjoin(percept_unit_clauses)


def numAdjWallsPerceptRules(t: int, percepts: List) -> Expr:
    """
    SLAM uses a weaker numAdjWallsPerceptRules sensor, which tells us how many walls pacman is adjacent to
    in its four directions.
        000 = 0 adj walls.
        100 = 1 adj wall.
        110 = 2 adj walls.
        111 = 3 adj walls.
    """
    assert isinstance(percepts, list), "Percepts must be a list."
    assert len(percepts) == 3, "Percepts must be a length 3 list."

    percept_unit_clauses = []
    for i, percept in enumerate(percepts):
        n = i + 1
        percept_literal_n = PropSymbolExpr(geq_num_adj_wall_str_map[n], time=t)
        if not percept:
            percept_literal_n = ~percept_literal_n
        percept_unit_clauses.append(percept_literal_n)
    return conjoin(percept_unit_clauses)


def SLAMSensorAxioms(t: int, non_outer_wall_coords: List[Tuple[int, int]]) -> Expr:
    all_percept_exprs = []
    combo_var_def_exprs = []
    for direction in DIRECTIONS:
        percept_exprs = []
        dx, dy = DIR_TO_DXDY_MAP[direction]
        for x, y in non_outer_wall_coords:
            combo_var = PropSymbolExpr(pacman_wall_str, x, y, x + dx, y + dy, time=t)
            percept_exprs.append(combo_var)
            combo_var_def_exprs.append(combo_var % (PropSymbolExpr(pacman_str, x, y, time=t) & PropSymbolExpr(wall_str, x + dx, y + dy)))

        blocked_dir_clause = PropSymbolExpr(blocked_str_map[direction], time=t)
        all_percept_exprs.append(blocked_dir_clause % disjoin(percept_exprs))

    percept_to_blocked_sent = []
    for n in range(1, 4):
        wall_combos_size_n = itertools.combinations(blocked_str_map.values(), n)
        n_walls_blocked_sent = disjoin([
            conjoin([PropSymbolExpr(blocked_str, time=t) for blocked_str in wall_combo])
            for wall_combo in wall_combos_size_n])
        # n_walls_blocked_sent is of form: (N & S) | (N & E) | ...
        percept_to_blocked_sent.append(
            PropSymbolExpr(geq_num_adj_wall_str_map[n], time=t) % n_walls_blocked_sent)

    return conjoin(all_percept_exprs + combo_var_def_exprs + percept_to_blocked_sent)


def allLegalSuccessorAxioms(t: int, walls_grid: List[List], non_outer_wall_coords: List[Tuple[int, int]]) -> Expr:
    """walls_grid can be a 2D array of ints or bools."""
    all_xy_succ_axioms = []
    for x, y in non_outer_wall_coords:
        xy_succ_axiom = pacmanSuccessorAxiomSingle(
            x, y, t, walls_grid)
        if xy_succ_axiom:
            all_xy_succ_axioms.append(xy_succ_axiom)
    return conjoin(all_xy_succ_axioms)


def SLAMSuccessorAxioms(t: int, walls_grid: List[List], non_outer_wall_coords: List[Tuple[int, int]]) -> Expr:
    """walls_grid can be a 2D array of ints or bools."""
    all_xy_succ_axioms = []
    for x, y in non_outer_wall_coords:
        xy_succ_axiom = SLAMSuccessorAxiomSingle(
            x, y, t, walls_grid)
        if xy_succ_axiom:
            all_xy_succ_axioms.append(xy_succ_axiom)
    return conjoin(all_xy_succ_axioms)

#______________________________________________________________________________
# Various useful functions, are not needed for completing the project but may be useful for debugging


def modelToString(model: Dict[Expr, bool]) -> str:
    """Converts the model to a string for printing purposes. The keys of a model are 
    sorted before converting the model to a string.
    
    model: Either a boolean False or a dictionary of Expr symbols (keys) 
    and a corresponding assignment of True or False (values). This model is the output of 
    a call to pycoSAT.
    """
    if model == False:
        return "False" 
    else:
        # Dictionary
        modelList = sorted(model.items(), key=lambda item: str(item[0]))
        return str(modelList)


def extractActionSequence(model: Dict[Expr, bool], actions: List) -> List:
    """
    Convert a model in to an ordered list of actions.
    model: Propositional logic model stored as a dictionary with keys being
    the symbol strings and values being Boolean: True or False
    Example:
    >>> model = {"North[2]":True, "P[3,4,0]":True, "P[3,3,0]":False, "West[0]":True, "GhostScary":True, "West[2]":False, "South[1]":True, "East[0]":False}
    >>> actions = ['North', 'South', 'East', 'West']
    >>> plan = extractActionSequence(model, actions)
    >>> print(plan)
    ['West', 'South', 'North']
    """
    plan = [None for _ in range(len(model))]
    for sym, val in model.items():
        parsed = parseExpr(sym)
        if type(parsed) == tuple and parsed[0] in actions and val:
            action, _, time = parsed
            plan[time] = action
    #return list(filter(lambda x: x is not None, plan))
    return [x for x in plan if x is not None]


# Helpful Debug Method
def visualizeCoords(coords_list, problem) -> None:
    wallGrid = game.Grid(problem.walls.width, problem.walls.height, initialValue=False)
    for (x, y) in itertools.product(range(problem.getWidth()+2), range(problem.getHeight()+2)):
        if (x, y) in coords_list:
            wallGrid.data[x][y] = True
    print(wallGrid)


# Helpful Debug Method
def visualizeBoolArray(bool_arr, problem) -> None:
    wallGrid = game.Grid(problem.walls.width, problem.walls.height, initialValue=False)
    wallGrid.data = copy.deepcopy(bool_arr)
    print(wallGrid)

class PlanningProblem:
    """
    This class outlines the structure of a planning problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the planning problem.
        """
        util.raiseNotDefined()

    def getGhostStartStates(self):
        """
        Returns a list containing the start state for each ghost.
        Only used in problems that use ghosts (FoodGhostPlanningProblem)
        """
        util.raiseNotDefined()
        
    def getGoalState(self):
        """
        Returns goal state for problem. Note only defined for problems that have
        a unique goal state such as PositionPlanningProblem
        """
        util.raiseNotDefined()
