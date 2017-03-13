# maxEntClassifier.py
# By Jon Bisila and Daniel Lewitz
# Winter 2017 Final Project
# CS 321: Artificial Intelligence

import numpy as np
import preprocess
import warnings
import sys
import os
import itertools
warnings.filterwarnings('error')


def load_data(filename, features):
     return preprocess.processData(filename,features)


# Creates empiricals given the set of feature vectors, and the true labels
def getEmpiricals(instances, labels):

    F = len(instances[0])
    N = len(instances)
    # Empirical1[i] will store the probability that some instance will have true
    # label 0, and will have a 1 for feature i
    empirical0 = np.zeros(F)
    empirical1 = np.zeros(F)
    for i in range(N):
        # If the true label is 0, adds features from instance to empirical0
        if labels[i] == 0:
            empirical0 = np.add(empirical0, instances[i])
        else:
            empirical1 = np.add(empirical1, instances[i])

    # Normalizes empiricals
    empirical0 /= N
    empirical1 /= N
    return (empirical0, empirical1)


# Given a feature vector, and current weight vectors, returns probability
# that instance is from class 0 or class 1
def getProbs(instance, w0, w1):
    # print("w0 :", w0, " w1: ", w1)
    # print("\n")

    prob0 = np.exp(np.dot(instance, w0))
    prob1 = np.exp(np.dot(instance, w1))
    const = prob0 + prob1
    return(prob0/ const, prob1/const)


# Classifies feature vectors from instances, and returns the proportion of
# guesses that are correct
def testTraining(instances, labels, weights0, weights1):
    correct = 0
    N = len(instances)
    for i in range(N):
        prob1 = getProbs(instances[i], weights0, weights1)[1]
        guess = int(prob1 > .5)
        correct += int(guess == labels[i])
    return correct/N


# Performs a full iteration of maxent, and updates the weights
def update(instances, weights0, weights1, V, F, N, emp0, emp1):

    # Model0, model1 are the feature distributions as per our model given the
    # current weights
    model0 = np.zeros(F)
    model1 = np.zeros(F)
    for instance in instances:
        probs = getProbs(instance, weights0, weights1)
        model0 = np.add(model0, instance * probs[0])
        model1 = np.add(model1, instance * probs[1])
    model0 /= N
    model1 /= N
    for i in range(F):

        # If the model prediction is 0 for some feature, sets
        # corresponding weight to 0. In some cases, this may be due
        # to python rounding down very small numbers to 0
        try:
            weights0[i] *= (emp0[i] / model0[i]) ** (1 / V)
        except:
            weights0[i] = 0
        try:
            weights1[i] *=(emp1[i] / model1[i]) ** (1 / V)
        except:
            weights1[i] = 0

    return weights0, weights1


# Creates and tests a maximum entropy model, given a list of desired features
def maxEnt(features):
    print(features)
    instances, labels = load_data("processData.txt", features)
    V = sum(instances[0])
    F = len(instances[0])
    N = len(instances)
    emp0, emp1 = getEmpiricals(instances, labels)
    weights0 = np.ones(F)
    weights1 = np.ones(F)
    testingData, testingLabels = load_data("testData.txt", features)

    beforeTesting = testTraining(testingData, testingLabels, weights0, weights1)

    # Runs 20 iterations of updating weights. We chose 20 iterations because we
    # observed that for any choice of features, the weights would always converge
    # essentially completely after 20 iterations
    for j in range(20):
        weights0, weights1 = update(instances, weights0, weights1, V, F, N, emp0, emp1)


    afterTesting = testTraining(testingData, testingLabels, weights0, weights1)
    print(afterTesting)
    return beforeTesting, afterTesting


# Runs maxent on all possible combinations of N features, and writes results to
# the desired output file
def compareN(output, N):
    allFeatures = ["age", "workclass", "education", "education-num", "marital-status", "occupation", "capital-gain",
                   "capital-loss", "sex", "hours-per-week"]# "race", "native-country"]
    combos = itertools.combinations(allFeatures, N)
    if os.path.isfile(output):
        os.remove(output)
    with open(output, "a") as f:
        for combo in combos:
            before, after = maxEnt(combo)
            f.write(str(combo).replace(",", " ") + "," + str(after) + "\n")


# Runs maxEnt with the desired features
def main():
    if len(sys.argv) == 1:
        allFeatures = ["age", "workclass", "education", "education-num", "marital-status", "occupation", "capital-gain", "capital-loss", "race", "native-country"]
        sig_features = ["workclass", "education", "education-num", "capital-gain", "capital-loss", "occupation"]

        for i in range(1, len(allFeatures) +1):
            compareN("compare" + str(i) + ".csv", i)
        before, after = maxEnt(allFeatures)
        print(before,after)

    else:
        print(maxEnt(sys.argv[1:]))

if __name__ == "__main__":
    main()
