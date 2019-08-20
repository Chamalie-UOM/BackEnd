import csv
import os

from phyloGenie_backend import settings


class Recommendation(object):
    def __init__(self):
        self.noOfSeq = 0
        self.lengthOfSeq = 0
        self.typeOfSeq = ""
        self.score = 10.0
        self.recommendedAlgorithms = []

    def readFeaturesFile(self,path):
        file0 = open(os.path.join(settings.BASE_DIR, path))
        readFile = csv.reader(file0, delimiter=',')
        #readFile = csv.reader(file, delimiter=',')
        #readFile = file.split(',')
        for featureSet in readFile:
            self.noOfSeq = int(featureSet[0])
            self.lengthOfSeq = int(featureSet[1])
            self.typeOfSeq = featureSet[2]
            self.score = float(featureSet[3])
        #print(noOfSeq, lengthOfSeq, typeOfSeq, score)
        return (self.noOfSeq, self.lengthOfSeq, self.typeOfSeq)

    def RecommendationOne(self):
        self.recommendedAlgorithms.append("Bayesian")
        self.recommendedAlgorithms.append("Maximum Likelihood")

    def RecommendationTwo(self):
        self.recommendedAlgorithms.append("Maximum Parsimony")
        self.recommendedAlgorithms.append("NJ")
        self.recommendedAlgorithms.append("UPGMA")

    def RecommendationThree(self):
        self.recommendedAlgorithms.append("NJ")
        self.recommendedAlgorithms.append("UPGMA")

    def RecommendationFour(self):
        self.recommendedAlgorithms.append("Maximum Parsimony")

    def RecommendByScore(self,value):
        if (self.score <= value):
            self.RecommendationOne()
        else:
            self.RecommendationTwo()

    def RecommendByScore2(self,value):
        if (self.score <= value):
            self.RecommendationOne()
        else:
            self.RecommendationFour()

    def RecommendByScore3(self,value):
        if (self.score <= value):
            self.RecommendationOne()
        else:
            self.RecommendationThree()

    def recommendation( self,noOfSeq, lengthOfSeq, typeOfSeq):
        if (noOfSeq <= 25):
            if (lengthOfSeq <= 500):
                if (typeOfSeq == 'DNA'):
                    self.RecommendByScore(0.75)
                else:
                    self.RecommendByScore(0.25)

            else:
                if (typeOfSeq == 'DNA'):
                    self.RecommendByScore2(0.75)
                else:
                    self.RecommendByScore2(0.25)
        else:
            if (lengthOfSeq <= 500):
                if (typeOfSeq == 'DNA'):
                    self.RecommendByScore3(0.75)
                else:
                    self.RecommendByScore3(0.25)
            else:
                self.RecommendationOne()

        algorithms = ', '.join(self.recommendedAlgorithms)
        algo_dict ={'algorithms':algorithms}
        return algo_dict
