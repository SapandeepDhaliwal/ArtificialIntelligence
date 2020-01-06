# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 15:40:45 2018

@author: sapandeepDhaliwal

"""
from itertools import islice
import time

numOfBeds = 0
numOfParkingSpots = 0
applicantsInLAHSA = set()
applicantsInSPLA = set()
totalApplicants = {}
applicantsFeasibleForLAHSA = []
applicantsFeasibleForSPLA = []
emptySpacesForLAHSA = []
emptySpacesForSPLA = []
bestAction = []
lastIterationBestAction = []
SPLA_move_list = []
LAHSA_move_list = []
# It is dictionary of moves and scores
transposition_table = {}
estimated_sum_total = 0
best_value = [-1, -1]
current_value = [-1, -1]
totalApplicantScore = {}
applicantID = {}
DepthLimit = 2
nodes_exp = 0
pruning = 0

# time related
timeElapsed = False
startTime = time.time()

def compare(applicant1, applicant2):
    return cmp(totalApplicantScore[applicant1], totalApplicantScore[applicant2])

def initialFeasibleMovesForLAHSA():
    for key in totalApplicants:
        if key not in applicantsInLAHSA and key not in applicantsInSPLA and \
                totalApplicants[key][0:1] == 'F' and int(totalApplicants[key][1:4]) > 17 \
                and totalApplicants[key][4:5] == 'N':
            add = True
            for i in xrange(7):
                if int(totalApplicants[key][i + 8]) > emptySpacesForLAHSA[i]:
                    add = False
                    break
            if add is True:
                applicantsFeasibleForLAHSA.append(key)
    applicantsFeasibleForLAHSA.sort(cmp = compare, reverse= True)


def initialFeasibleMovesForSPLA():
    for key in totalApplicants:
        if key not in applicantsInLAHSA and key not in applicantsInSPLA and \
                totalApplicants[key][5:6] == 'N' and totalApplicants[key][6:7] == 'Y' \
                and totalApplicants[key][7:8] == 'Y':
                add = True
                for i in xrange(7):
                    if int(totalApplicants[key][i + 8]) > emptySpacesForSPLA[i]:
                        add = False
                        break
                if add is True:
                    applicantsFeasibleForSPLA.append(key)
    applicantsFeasibleForSPLA.sort(cmp = compare, reverse= True)
    return applicantsFeasibleForSPLA


def transitionModelForLAHSA():
    for key in applicantsInLAHSA:
        for i in xrange(7):
            emptySpacesForLAHSA[i] = emptySpacesForLAHSA[i] - int(totalApplicants[key][i + 8])
    current_value[1] = calculateUtilityLAHSA(emptySpacesForLAHSA)


def transitionModelForSPLA():
    for key in applicantsInSPLA:
        for i in xrange(7):
            emptySpacesForSPLA[i] = emptySpacesForSPLA[i] - int(totalApplicants[key][i + 8])
    current_value[0] = calculateUtilitySPLA(emptySpacesForSPLA)


def calculateUtilitySPLA(emptySlotsInState):
    utilityValueSPLA = numOfParkingSpots * 7 - sum(emptySlotsInState)
    return utilityValueSPLA


def calculateUtilityLAHSA(emptySlotsInState):
    utilityValueLAHSA = numOfBeds * 7 - sum(emptySlotsInState)
    return utilityValueLAHSA


def estimate_total():
    global applicantsInLAHSA, applicantsInSPLA, estimated_sum_total, \
        numOfBeds, numOfParkingSpots

    individual_total = 0
    for applicant in applicantsInLAHSA:
        for i in xrange(7):
            individual_total += int(totalApplicants[applicant][i + 8])

    for applicant in applicantsFeasibleForLAHSA:
        for i in xrange(7):
            individual_total += int(totalApplicants[applicant][i + 8])

    for applicant in applicantsInSPLA:
        for i in xrange(7):
            individual_total += int(totalApplicants[applicant][i + 8])

    for applicant in applicantsFeasibleForSPLA:
        if applicant not in applicantsFeasibleForLAHSA:
            for i in xrange(7):
                individual_total += int(totalApplicants[applicant][i + 8])

    individual_total = min((7 * numOfParkingSpots) + (7 * numOfBeds), individual_total)
    estimated_sum_total = individual_total



def readFile():
    with open("input0.txt", "r") as inputFile:
        global numOfBeds
        numOfBeds = int(inputFile.readline())

        global numOfParkingSpots
        numOfParkingSpots = int(inputFile.readline())
        for i in xrange(7):
            emptySpacesForLAHSA.append(int(numOfBeds))
            emptySpacesForSPLA.append(int(numOfParkingSpots))
        numOfApplicantsInLAHSA = inputFile.readline()
        lineCount = islice(inputFile, int(numOfApplicantsInLAHSA))
        for current_line in lineCount:
            applicantsInLAHSA.add(current_line.strip('\n'))

        for i, line in enumerate(inputFile):
            if i == 0:
                numOfApplicantsInSPLA = line
                lineCount2 = islice(inputFile, int(numOfApplicantsInSPLA))
                for current_line2 in lineCount2:
                    applicantsInSPLA.add(current_line2.strip('\n'))
            else:
                numOfTotalApplicants = line
                lineCount3 = islice(inputFile, int(numOfTotalApplicants))
                for id,current_line3 in enumerate(lineCount3):
                    totalApplicants.update({current_line3[0:5]: current_line3[5:20]})
                    local_sum = 0
                    for l in xrange(7):
                        local_sum += int(current_line3[13 + l])
                    totalApplicantScore.update({current_line3[0:5]: local_sum})
                    applicantID.update({current_line3[0:5]: id})
                break

        global SPLA_move_list
        SPLA_move_list = [0 for i in xrange(int(numOfTotalApplicants) + 1)]
        global LAHSA_move_list
        LAHSA_move_list = [0 for i in xrange(int(numOfTotalApplicants) + 1)]


def updateEmptySpaces(candidateID, emptySpaces):
    for i in xrange(7):
        emptySpaces[i] = emptySpaces[i] - int(totalApplicants[candidateID][i + 8])


def updateFeasibleMoves(candidateID, emptySpaces, oldFeasibleMoves, compareEmpty):
    if candidateID in oldFeasibleMoves:
        oldFeasibleMoves.remove(candidateID)
    if compareEmpty is True:
        for candidate in oldFeasibleMoves[:]:
            remove = False
            for i in xrange(7):
                if int(totalApplicants[candidate][i + 8]) > emptySpaces[i]:
                    remove = True
                    break
            if remove is True and candidate in oldFeasibleMoves:
                oldFeasibleMoves.remove(candidate)


# Move lists should be sorted
def save_move_score(SPLA_move_list, LHSA_move_list, utility_list):
    global transposition_table
    if sum(SPLA_move_list) + sum(LHSA_move_list) > 2:
        if tuple(SPLA_move_list) not in transposition_table:
            transposition_table[tuple(SPLA_move_list)] = {}
        transposition_table[tuple(SPLA_move_list)][tuple(LHSA_move_list)] = utility_list



"""alpha - beta pruning """
def alphaBeta():
    global timeElapsed, lastIterationBestAction, transposition_table
    nextSPLAmoves = applicantsFeasibleForSPLA[:]
    nextLAHSAmoves = applicantsFeasibleForLAHSA[:]
    bestMove = []
    value = [-1, -1]
    currentEmptySpacesForSPLA = emptySpacesForSPLA[:]
    currentEmptySpacesForLAHSA = emptySpacesForLAHSA[:]
    currentDepth = 0
    for depthLimit in xrange(1, DepthLimit + 1):
        transposition_table = {}
        value = SPLANode(nextSPLAmoves, nextLAHSAmoves, bestMove,
                         currentEmptySpacesForSPLA, currentEmptySpacesForLAHSA,
                         currentDepth, current_value, [-1, -1], depthLimit)

        if timeElapsed is False:
            lastIterationBestAction = bestAction[:]
        else:
            break

    return value


def terminalTest(currentEmptySpaces, feasibleMoves):
    if sum(currentEmptySpaces) == 0 or len(feasibleMoves) == 0:
        return True
    else:
        return False


def cutOffTest(depth, cuttOffDepth):
    if depth >= cuttOffDepth:
        return True
    else:
        return False


def cutOffUtility(nextSPLAmoves, nextLAHSAmoves, currentEmptySpacesForSPLA, \
                  currentEmptySpacesForLAHSA):
    currentSPLAUtil = calculateUtilitySPLA(currentEmptySpacesForSPLA)
    currentLAHSAUtil = calculateUtilityLAHSA(currentEmptySpacesForLAHSA)
    return [currentSPLAUtil, currentLAHSAUtil]


def CheckTime():
    global timeElapsed
    current_time = time.time()
    if int(current_time - startTime) > 165:
        timeElapsed = True


def SPLANode(nextSPLAmoves, nextLAHSAmoves, bestMove, currentEmptySpacesForSPLA, \
             currentEmptySpacesForLAHSA, currentDepth, current_value, best_branch_value, cuttOffDepth):
    global timeElapsed
    value = [-1, -1]
    nextActions = nextSPLAmoves
    global transposition_table, best_value, nodes_exp

    nodes_exp += 1

    if best_branch_value[0] > estimated_sum_total - current_value[1]:
        global pruning
        pruning += 1
        return current_value[:]

    CheckTime()

    if terminalTest(currentEmptySpacesForLAHSA, nextLAHSAmoves)\
            and terminalTest(currentEmptySpacesForSPLA, nextSPLAmoves):
        return cutOffUtility(nextSPLAmoves, nextLAHSAmoves, \
                                currentEmptySpacesForSPLA, currentEmptySpacesForLAHSA)
    elif terminalTest(currentEmptySpacesForSPLA, nextActions):
        return LAHSANode(nextSPLAmoves, nextLAHSAmoves, bestMove, currentEmptySpacesForSPLA,
                        currentEmptySpacesForLAHSA, currentDepth, current_value,
                        best_branch_value, cuttOffDepth)
    elif cutOffTest(currentDepth, cuttOffDepth):
        utility = cutOffUtility(nextSPLAmoves, nextLAHSAmoves, \
                                currentEmptySpacesForSPLA, currentEmptySpacesForLAHSA)
        return utility
    elif timeElapsed is True:
        return value
    else:
        for a in nextActions:
            global SPLA_move_list
            appId = applicantID.get(a)
            SPLA_move_list[appId] = 1
            SPLA_move_tuple = tuple(SPLA_move_list)
            LAHSA_move_tuple = tuple(LAHSA_move_list)
            if SPLA_move_tuple not in transposition_table or \
                    LAHSA_move_tuple not in transposition_table[SPLA_move_tuple]:
                current_value[0] += totalApplicantScore[a]
                newEmptySpacesForSPLA = currentEmptySpacesForSPLA[:]
                newEmptySpacesForLAHSA = currentEmptySpacesForLAHSA[:]
                newSPLAmoves = nextSPLAmoves[:]
                newLAHSAmoves = nextLAHSAmoves[:]
                updateEmptySpaces(a, newEmptySpacesForSPLA)
                updateFeasibleMoves(a, newEmptySpacesForSPLA, newSPLAmoves, True)
                updateFeasibleMoves(a, newEmptySpacesForLAHSA, newLAHSAmoves, False)

                newValue = LAHSANode(newSPLAmoves, newLAHSAmoves, bestMove,
                                     newEmptySpacesForSPLA, newEmptySpacesForLAHSA, currentDepth + 1,
                                     current_value, best_branch_value, cuttOffDepth)

                current_value[0] -= totalApplicantScore[a]
                if timeElapsed is True:
                    break
            else:
                newValue = transposition_table[SPLA_move_tuple][LAHSA_move_tuple]

            if newValue[0] >= value[0]:
                global bestAction
                if currentDepth == 0:
                    if newValue[0] > value[0]:
                        bestAction = [a]
                    elif len(bestAction) != 0 and bestAction[0] > a:
                        bestAction = [a]
                    elif len(bestAction) == 0:
                        bestAction = [a]
                value = newValue[:]

            if newValue[0] > best_branch_value[0]:
                best_branch_value = newValue[:]

            if newValue[0] > best_value[0]:
                best_value = newValue[:]
            save_move_score(SPLA_move_list, LAHSA_move_list, newValue)
            SPLA_move_list[appId] = 0
        return value


def LAHSANode(nextSPLAmoves, nextLAHSAmoves, bestMove, currentEmptySpacesForSPLA,
              currentEmptySpacesForLAHSA, currentDepth, current_value, best_branch_value, cuttOffDepth):
    global nodes_exp, timeElapsed
    value = [-1, -1]
    nextActions = nextLAHSAmoves
    nodes_exp += 1

    CheckTime()

    if terminalTest(currentEmptySpacesForLAHSA, nextLAHSAmoves)\
            and terminalTest(currentEmptySpacesForSPLA, nextSPLAmoves):
        return cutOffUtility(nextSPLAmoves, nextLAHSAmoves, \
                                currentEmptySpacesForSPLA, currentEmptySpacesForLAHSA)
    elif terminalTest(currentEmptySpacesForLAHSA, nextActions):
        return SPLANode(nextSPLAmoves, nextLAHSAmoves, bestMove, currentEmptySpacesForSPLA,
                        currentEmptySpacesForLAHSA, currentDepth, current_value,
                        best_branch_value, cuttOffDepth)
    elif cutOffTest(currentDepth, cuttOffDepth):
        utility = cutOffUtility(nextSPLAmoves, nextLAHSAmoves,
                                currentEmptySpacesForSPLA, currentEmptySpacesForLAHSA)
        return utility
    elif timeElapsed is True:
        return value
    else:
        for a in nextActions:
            global SPLA_move_list, LAHSA_move_list
            appId = applicantID.get(a)
            LAHSA_move_list[appId] = 1
            SPLA_move_tuple = tuple(SPLA_move_list)
            LAHSA_move_tuple = tuple(LAHSA_move_list)
            if SPLA_move_tuple not in transposition_table or \
                    LAHSA_move_tuple not in transposition_table[SPLA_move_tuple]:
                newEmptySpacesForSPLA = currentEmptySpacesForSPLA[:]
                newEmptySpacesForLAHSA = currentEmptySpacesForLAHSA[:]
                newSPLAmoves = nextSPLAmoves[:]
                newLAHSAmoves = nextLAHSAmoves[:]
                current_value[1] += totalApplicantScore[a]
                updateEmptySpaces(a, newEmptySpacesForLAHSA)
                updateFeasibleMoves(a, newEmptySpacesForSPLA, newSPLAmoves, False)
                updateFeasibleMoves(a, newEmptySpacesForLAHSA, newLAHSAmoves, True)

                newValue = SPLANode(newSPLAmoves, newLAHSAmoves, bestMove,
                                    newEmptySpacesForSPLA, newEmptySpacesForLAHSA,
                                    currentDepth + 1, current_value, best_branch_value, cuttOffDepth)

                current_value[1] -= totalApplicantScore[a]

                if timeElapsed is True:
                    break

            else:
                newValue = transposition_table[SPLA_move_tuple][LAHSA_move_tuple]

            if newValue[1] > value[1]:
                value = newValue[:]

            if newValue[1] > best_branch_value[1]:
                best_branch_value = newValue[:]

            save_move_score(SPLA_move_list, LAHSA_move_list, newValue)
            LAHSA_move_list[appId] = 0

        return value


def setMaxDepthLimit():
    global DepthLimit
    DepthLimit = len(set(applicantsFeasibleForSPLA).
                     union(set(applicantsFeasibleForLAHSA)))

def printDebugInfo():
    SPLA_set = set(applicantsFeasibleForSPLA)
    LAHSA_set = set(applicantsFeasibleForLAHSA)
    common_set = SPLA_set.intersection(LAHSA_set)
    print "Common_set: {}".format(common_set)


if __name__ == "__main__":
    readFile()
    transitionModelForLAHSA()
    transitionModelForSPLA()
    initialFeasibleMovesForLAHSA()
    initialFeasibleMovesForSPLA()
    estimate_total()
    setMaxDepthLimit()
    alphaBeta()
    with open("output.txt", 'w') as out_file:
        if len(lastIterationBestAction) > 0:
            out_file.write(str(lastIterationBestAction[0]) + "\n")
    out_file.close()