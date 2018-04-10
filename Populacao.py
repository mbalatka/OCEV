import numpy as np
import random
import Individuo
import IndividuoBin
import IndividuoInt
import IndividuoReal
import IndividuoIntPerm
import matplotlib.pyplot as plt
import copy



class Populacao():
    def __init__(self, tamPop, tamCrom, cod, minB=-10, maxB=10, elit=True):
        if cod == "BIN":
            self.individuos = [IndividuoBin.IndividuoBin(tamCrom, minB, maxB) for i in range(tamPop)]
            self.tipoCrossover = "1pto"
            self.tipoMutacao = "bitflip"
        elif cod == "INT":
            self.individuos = [IndividuoInt.IndividuoInt(tamCrom, minB, maxB) for i in range(tamPop)]
            self.tipoCrossover = "null"
            self.tipoMutacao = "null"
        elif cod == "REAL":
            self.individuos = [IndividuoReal.IndividuoReal(tamCrom, minB, maxB) for i in range(tamPop)]
            self.tipoCrossover = "null"
            self.tipoMutacao = "null"
        elif cod == "INT-PERM":
            self.individuos = [IndividuoIntPerm.IndividuoIntPerm(tamCrom, minB, maxB) for i in range(tamPop)]
            self.tipoCrossover = "null"
            self.tipoMutacao = "null"
        else:
            raise Exception("Codificacao invalida")
        self.tamPop = tamPop
        self.tipoCod = cod
        self.tamCrom = tamCrom
        self.maxDiv = None
        self.maxGeracoes = 2000
        self.elit = elit
        self.tipoSelecao = "roleta"
        self.txMut = 0.05#taxa de mutacao

    def popFitness(self):
        s = "Individuos->Fitness:\n"
        for i in self.individuos:
            s += str(i) + " -> " + str(i.fitness()) +"\n"
        return s


    def centroid(self):
        cent = []
        for i in range(self.tamCrom):#n dimensões
            s = 0
            for j in range(len(self.individuos)):
                s += self.individuos[j].cromossomo[i]
            cent += [s/len(self.individuos)]
        return cent

    def diversidade(self):
        c = self.centroid()
        i = 0
        for i in range(len(self.individuos)):
            iC = 0
            for j in range(len(self.individuos[i].cromossomo)):
                iC += (self.individuos[i].cromossomo[j] - c[j]) ** 2
            i += iC

        return i

    def diversidadeN(self):
        d = self.diversidade()
        if self.maxDiv:
            return d/self.maxDiv
        else:
            self.maxDiv = d
            return 1
    
    def totalFitness(self):
        totF = 0
        for i in self.individuos:
            totF += i.fitness()
        return totF
    
    def selecao(self):
        #executa o tipo de selecao desejada
        if self.tipoSelecao == "roleta":
            #selecao por roleta
            return self.selecaoRoleta()
        else:
            raise Exception("Selecao [", self.tipoSelecao, "] invalida")
            
    def selecaoRoleta(self):
        #Somatorio de fitness
        totF = self.totalFitness()

        #chance de cada individuo de ser escolhido
        chances = []
        for i in self.individuos:
            chances += [i.fitness()/totF]
        
        #escolha dos individuos
        selecionados = []
        for i in range(int(len(self.individuos)/2)):#cada iteracao seleciona 2
            #escolhe o individuo de acordo com o numero gerado aleatoriamente
            n = np.random.choice(list(range(len(self.individuos))), p=chances)
            selecionados += [self.individuos[n]]
            
            #recalcula a roleta
            chances2 = []
            for i in self.individuos:
                chances2 += [i.fitness()/(totF-self.individuos[n].fitness())]
            chances2[n] = 0.0
            n2 = np.random.choice(list(range(len(self.individuos))), p=chances2)
            selecionados += [self.individuos[n2]]
        
        #print("Total fitness: ", totF)
        #print("Chances: ", chances)
        return selecionados
        
    def recombinacao(self, individuos):
        popInt = []
        for i in range(int(len(self.individuos)/2)):
            inds = individuos[i*2].crossover(individuos[i*2+1], self.tipoCrossover)
            popInt += [inds[0]]
            popInt += [inds[1]]
        return popInt
    
    def loopEvolucao(self):
        #TODO calcular o fitness apenas uma vez por geracao
        melhorF = 0
        melhoresInd = []
        melhoresIndF = []
        mediasIndF = []
        diver = []
        for gen in range(self.maxGeracoes):
            if gen%10 == 0:
                print("---Geracao", gen, "---", "Melhor fitness: ", melhorF)
            
            #melhor individuo para elitismo
            diver += [self.diversidadeN()]
            eliteF = -1.0
            eliteInd = None
            if self.elit:
                for i in self.individuos:
                    f = i.fitness()
                    if f > eliteF:
                        eliteF = f
                        eliteInd = copy.deepcopy(i)
            #print(self.popFitness())
            
            #print("Selecao:")
            #selecao dos individuos
            sel = self.selecao()
            #for s in sel:
            #    print(s)
            
            #print("Recombinacao:")
            #criacao da populacao intermediaria
            popInterm = self.recombinacao(sel)
            #for s in popInterm:
            #    print(s)
            
            #substituia a populacao
            for i in range(len(popInterm)):
                self.individuos[i].cromossomo = popInterm[i]
                
            #mutacao
            for i in self.individuos:
                i.mutacao(self.txMut, self.tipoMutacao)
            
            #elitismo
            if self.elit:
                piorInd = 0
                piorF = self.individuos[0].fitness()
                for i in range(len(self.individuos)):
                    f = self.individuos[i].fitness()
                    if f < piorF:
                        piorF = f
                        piorInd = i
                self.individuos[piorInd] = eliteInd
            
            
            #calculo do melhor e media por geracao
            melhorF = -1
            melhor = None
            soma = 0
            for i in self.individuos:
                fit = i.fitness()
                soma += fit
                if fit > melhorF:
                    melhorF = fit
                    melhor = i.cromossomo
            melhoresInd += [melhor]
            melhoresIndF += [melhorF]
            mediasIndF += [soma/len(self.individuos)]
            #print ao final da geracao
            #print("Populacao final da geracao")
            #print(self.popFitness())
            #print("----------------")
            if melhorF == self.tamCrom-1:#parar se achar a solucao otima
                break
        return {"bInd":melhoresInd, "bF":melhoresIndF, "mF":mediasIndF, "diver":diver}
    
    def geraGraficos(self, result):    
        #criacao dos graficos
        fig, ax = plt.subplots(2, 1)
        #grafico do maior
        ax[0].set_xlabel("Geração")
        ax[0].set_ylabel("Fitness")
        ax[0].set_title("Fitness por geração")
        ax[0].plot(result["bF"], label="Melhor", lw=1)
        ax[0].plot(result["mF"], label="Media", lw=1)
        ax[0].legend(loc="upper left")
        
        #grafico da media
        ax[1].set_xlabel("Geração")
        ax[1].set_ylabel("Diversidade")
        ax[1].set_title("Diversidade por geração")
        ax[1].plot(result["diver"], lw=1)
        
        plt.tight_layout()
        plt.show()
    
    def info(self):
        print("---Configuracoes do AG---")
        print("Tipo de codificacao:", self.tipoCod)
        print("Tamanho da populacao:", self.tamPop)
        print("Tamanho do cromossomo:", self.tamCrom)
        print("Maximo de geracoes:", self.maxGeracoes)
        print("Tipo de selecao:", self.tipoSelecao)
        print("Elitismo:", self.elit)
        print("Tipo de crossover:", self.tipoCrossover)
        print("Tipo de mutacao:", self.tipoMutacao)        
        print("Taxa de mutacao:", self.txMut)
    
    def __str__(self):
        s = "Individuos:\n"
        for i in self.individuos:
            s += str(i) + "\n"
        return s

def main():
    pop = Populacao(5, 5, "BIN")
    print(pop)

if __name__ == "__main__":
    main()
