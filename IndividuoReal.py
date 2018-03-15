from Individuo import *
import numpy as np
import math

class IndividuoReal(Individuo):
    def __init__(self, tam, minB=-10, maxB=10):
        self.min_bound = minB
        self.max_bound = maxB
        self.cod = "REAL"
        self.cromossomo = self.init_cromossomo(tam)
    
    def init_cromossomo(self, tamCrom):
        return np.random.RandomState().uniform(self.min_bound, self.max_bound, size=tamCrom)
        
    def fitness(self):
        ##
        first_sum = 0.0
        second_sum = 0.0
        for g in self.cromossomo:
            first_sum += g ** 2.0
            second_sum += math.cos(2.0 * math.pi * g)
        n = float(len(self.cromossomo))
        return -20.0*math.exp(-0.2*math.sqrt(first_sum/n)) - math.exp(second_sum/n) + 20 + math.e
        ##