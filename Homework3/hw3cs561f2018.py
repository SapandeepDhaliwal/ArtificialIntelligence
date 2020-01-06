# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 21:25:05 2018

@author: sapandeepDhaliwal
"""

import numpy as np

GridSize = 0
NumberOfCars = 0
NumberOfObstacles = 0
Obstacles = set()
CarsStartXY = []
CarsTargetXY = []
CarsTargetLoc = []
CarsStartLoc = []
AllStateProb = []

#Dont change order
Actions = ['north', 'south', 'east', 'west']
States = []
CurrentPolicy = []
FinalPolicy = []

Gamma = np.float64(0.9)
ConvFactor = np.float64(0.1)

def ReadInputFile():
    global GridSize, NumberOfCars, NumberOfObstacles, CurrentPolicy,\
    States, FinalPolicy,AllStateProb, Actions
    with open("input.txt") as inp:
        for lineNumber, line in enumerate(inp):
            if lineNumber == 0:
                GridSize = int(line)
            elif lineNumber == 1:
                NumberOfCars = int(line)
            elif lineNumber == 2:
                NumberOfObstacles = int(line)
            elif lineNumber < NumberOfObstacles + 3:
                x, y = line.rstrip().split(',', 2)
                Obstacles.add((int(x), int(y)))
            elif lineNumber < NumberOfObstacles + NumberOfCars + 3:
                x, y = line.rstrip().split(',', 2)
                CarsStartXY.append((int(x), int(y)))
                CarsStartLoc.append(GetLoc(int(x), int(y)))
            elif lineNumber < NumberOfObstacles + 2*NumberOfCars + 3:
                x, y = line.rstrip().split(',', 2)
                CarsTargetXY.append((int(x), int(y)))
                CarsTargetLoc.append(GetLoc(int(x), int(y)))

    CurrentPolicy = [[Actions[np.random.random_integers(low=0, high=3)]
                      for state in xrange(GridSize*GridSize)]
                      for car in xrange(NumberOfCars)]

    FinalPolicy = CurrentPolicy[:]

    States = [x for x in xrange(GridSize*GridSize)]

    AllStateProb = [[0 for x in Actions] for x in States]

    for state in States:
        for actionId, action in enumerate(Actions):
            AllStateProb[state][actionId] = GetAllStatesandProb(state, action)

def GetXandY(loc):
    return loc % GridSize, loc/GridSize

def GetLoc(x, y):
    return x + y*GridSize

def GetNextLoc(loc, action):
    x,y = GetXandY(loc)
    newX, newY = GetNextXY(x,y, action)
    return GetLoc(newX, newY)

def GetNextXY(x, y, action):
    newX, newY = x,y
    if action is'north':
        newY = y - 1
    elif action is 'south':
        newY = y + 1
    elif action is 'east':
        newX = x + 1
    else:
        newX = x - 1

    if newX < 0 or newX >= GridSize or newY < 0 or newY >= GridSize:
        newX = x
        newY = y
    return newX, newY

def GetAllNextStates(loc):
    validLocations = []
    for a in Actions:
        nextLoc = GetNextLoc(loc, a)
        if nextLoc not in validLocations:
            validLocations.append(nextLoc)
    return validLocations[:]

def GetAllStatesandProb(loc, action):
    validLocations = GetAllNextStates(loc)
    probability = [np.float64(0.0) for x in validLocations]
    NewlocForAction = GetNextLoc(loc, action)

    if len(validLocations) == 4:
        for index, x in enumerate(validLocations):
            if NewlocForAction == x:
                probability[index] += np.float64(0.7)
            else:
                probability[index] += np.float64(0.1)
    else:
        #Fewer states
        for index, x in enumerate(validLocations):
            if x == loc and NewlocForAction == x:
                probability[index] += np.float64(0.8)
            elif x != loc and NewlocForAction == x:
                probability[index] += np.float64(0.7)
            elif x == loc and NewlocForAction != x:
                probability[index] += np.float64(0.2)
            else:
                probability[index] += np.float64(0.1)

    return validLocations[:], probability[:]

def GetNextAllStatesandProb(loc, actionID, carID):
    curX, curY = CarsTargetXY[carID]

    if loc == GetLoc(curX, curY):
        return [], []
    else:
        return AllStateProb[loc][actionID]

def GetReward(x, y, carId):
    if (x,y) in Obstacles:
        return np.float64(-101.0)
    elif (x,y) == CarsTargetXY[carId]:
        return np.float64(99.0)
    else:
        return np.float64(-1.0)

def PolicyEval(CurrentPolicy, value, carID):
    global States, Gamma, ConvFactor
    newValue = value[:]
    conv = False
    IterIdx = 0
    while conv is not True:
        value = newValue[:]
        MaxDiff = 0
        for stateIndex, state in enumerate(States):
            action = CurrentPolicy[stateIndex]
            curStateX, curStateY = GetXandY(state)
            NextStates, Probabilities = GetNextAllStatesandProb(state, Actions.index(action), carID)
            addition = sum([Probabilities[probIndex]*newValue[nextState] for probIndex, nextState in enumerate(NextStates)])
            newValue[stateIndex] = GetReward(curStateX, curStateY, carID) + Gamma*addition
            MaxDiff = max(MaxDiff, abs(newValue[stateIndex] - value[stateIndex]))

        if MaxDiff < ConvFactor*(1-Gamma)/Gamma:
            conv = True

        IterIdx += 1

    return newValue[:]

def PolicyExtraction(PolicyValue, carID):
    global States, Gamma, Actions
    newPolicy = []
    for state in States:
        bestValue = np.finfo(np.float64).min
        bestAction = 'north'
        for action in Actions:
            NextStates, Probabilities = GetNextAllStatesandProb(state, Actions.index(action),carID)
            value = sum([Probabilities[probIndex] * PolicyValue[nextState] for probIndex, nextState in enumerate(NextStates)])
            if value > bestValue:
                bestValue = value
                bestAction = action
            elif value == bestValue and Actions.index(action) < Actions.index(bestAction):
                bestAction = action

        newPolicy.append(bestAction)

    return newPolicy

def PolicyIteration(carId):
    StartingPolicy = CurrentPolicy[carId][:]
    PolicyConv = False
    IterIdx = 0
    value = [0 for x in xrange(GridSize*GridSize)]
    while PolicyConv is not True:
        value = PolicyEval(StartingPolicy, value, carId)
        Policy = PolicyExtraction(value, carId)
        if Policy == StartingPolicy:
            PolicyConv = True
        StartingPolicy = Policy[:]
        IterIdx += 1

    FinalPolicy[carId] = Policy[:]
    return Policy

def ValueUpdate(carID):
    global States, Gamma, ConvFactor
    value = [np.float64(0) for x in xrange(GridSize*GridSize)]
    newValue = value[:]
    conv = False
    IterIdx = 0
    while conv is not True:
        value = newValue[:]
        MaxDiff = 0
        for stateIndex, state in enumerate(States):
            maxVal = np.finfo(np.float64).min
            for action in Actions:
                newVal = np.float64(0)
                curStateX, curStateY = GetXandY(state)
                NextStates, Probabilities = GetNextAllStatesandProb(state, Actions.index(action), carID)
                for probIndex, nextState in enumerate(NextStates):
                    addition = Probabilities[probIndex]* value[nextState]
                    newVal += addition
                maxVal = max(maxVal, newVal)
            newValue[stateIndex] = (GetReward(curStateX, curStateY, carID) + Gamma*maxVal)
            MaxDiff = max(MaxDiff, abs(newValue[stateIndex] - value[stateIndex]))

        if MaxDiff < ConvFactor*(1-Gamma)/Gamma:
            conv = True

        IterIdx += 1

    return newValue[:]

def ValueIteration(carId):
    Value = ValueUpdate(cardId)
    Policy = PolicyExtraction(Value, carId)
    FinalPolicy[carId] = Policy[:]
    return Policy

def Left(action):
    if action == 'north':
        return 'west'
    elif action == 'west':
        return 'south'
    elif action == 'south':
        return 'east'
    else:
        return 'north'

def Right(action):
    if action == 'north':
        return 'east'
    elif action == 'east':
        return 'south'
    elif action == 'south':
        return 'west'
    else:
        return 'north'

def GetNextSimAction(action, value):
    if value > 0.7:
        if value > 0.8:
            if value > 0.9:
                return Right(Right(action))
            else:
                return Right(action)
        else:
            return Left(action)
    else:
        return action

Move = {"north": (0, -1),
        "south": (0, 1),
        "west": (-1, 0),
        "east": (1, 0)}

def Simulate():
    RewardSum = [np.float64(0) for x in xrange(NumberOfCars)]
    for cardId in xrange(NumberOfCars):
        for seed in xrange(0, 10):
            np.random.seed(seed)
            sample = np.random.random_sample(1000000)
            policy = FinalPolicy[cardId][:]
            curX, curY = CarsStartXY[cardId]
            targetX, targetY = CarsTargetXY[cardId]
            stepIdx = 0
            while (curX, curY) != (targetX, targetY):
                curLoc = GetLoc(curX, curY)
                suggested_action = policy[curLoc]
                prob = sample[stepIdx]
                next_action = GetNextSimAction(suggested_action, prob)
                curX, curY = GetNextXY(curX, curY, next_action)
                valueGained = GetReward(curX, curY, cardId)
                RewardSum[cardId] += valueGained
                stepIdx += 1

    for cardId in xrange(NumberOfCars):
        RewardSum[cardId] = int(np.floor(RewardSum[cardId]/10))

    return RewardSum[:]


if __name__ == "__main__":
    ReadInputFile()

    for cardId in xrange(NumberOfCars):
        ValueIteration(cardId)
    RewardSum = Simulate()
    with open("output.txt", 'w') as out_file:
        for cardId in xrange(NumberOfCars):
            out_file.write(str(RewardSum[cardId]) + "\n")
    out_file.close()

