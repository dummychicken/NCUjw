import numpy as np
import math
from config import Config as cf
import function as fn

def levy_flight(Lambda):
    # levy飞行
    sigma1 = np.power((math.gamma(1 + Lambda) * np.sin((np.pi * Lambda) / 2)) \
                      / math.gamma((1 + Lambda) / 2) * np.power(2, (Lambda - 1) / 2), 1 / Lambda)
    sigma2 = 1
    u = np.random.normal(0, sigma1, size=cf.get_dimension())
    v = np.random.normal(0, sigma2, size=cf.get_dimension())
    step = u / np.power(np.fabs(v), 1 / Lambda)

    return step    # return np.array (ex. [ 1.37861233 -1.49481199  1.38124823])

def bin_levy_flight(Lambda):
    # levy飞行
    sigma1 = np.power((math.gamma(1 + Lambda) * np.sin((np.pi * Lambda) / 2)) \
                      / math.gamma((1 + Lambda) / 2) * np.power(2, (Lambda - 1) / 2), 1 / Lambda)
    sigma2 = 1
    u = np.random.normal(0, sigma1, size=cf.get_dimension())
    v = np.random.normal(0, sigma2, size=cf.get_dimension())
    step = u / np.power(np.fabs(v), 1 / Lambda)

    step = fn.sigmoid_KE(step)

    return step    # return np.array (ex. [ 1.37861233 -1.49481199  1.38124823])

def replace_bin(x,k,a):
    return x[:k] + a + x[k + 1:]

pop = cf.get_population_size()
list_cl = []
for i in range(pop):
    list_cl.append(str(bin(i)).replace("0b","").zfill(cf.get_bin()))
list_m = []
for i in range(pop):
    list_m.append(str(bin(i)).replace("0b","").zfill(cf.get_bin()))

class Individual:

    def __init__(self, m):
        self.__position = m
        #self.__position = np.random.rand(cf.get_dimension()) * (cf.get_max_domain() - cf.get_min_domain())  + cf.get_min_domain()
        self.__fitness = np.random.rand()
        #self.__fitness = fn.calculation(self.__position,0) # iteration = 0 时, 初始化解

    def get_position(self):
        return self.__position

    def set_position(self, position):
        self.__position = position

    def get_fitness(self):
        return self.__fitness

    def set_fitness(self, fitness):
        self.__fitness = fitness
    
    def init_position(self):
        p = np.random.randint(0,10)
        return p

    def abandon(self):
        # 根据概率P放弃部分鸟巢
        init_pos1 = []
        for p in range(pop):
            k = np.random.choice(pop,pop,replace=False)
            for i in k:
                init_pos1.append(list_cl[p] + list_m[i])
            self.__position = init_pos1
            init_pos1 = []
            #self.__position[i] = np.random.rand() * (cf.get_max_domain() - cf.get_min_domain())  + cf.get_min_domain()

    def get_cuckoo(self):

        #step_size = cf.get_stepsize() * levy_flight(cf.get_lambda())
        step_size = bin_levy_flight(cf.get_lambda())
        #step_size = fn.binary_KE(step_size) # 0, 1

        # 更新位置
        #self.__position = self.__position + step_size
        """for j in range(cf.get_population_size()):
            for k in range(cf.get_bin() * 2):
                r = np.random.rand()
                if r <= step_size:
                    self.__position[j] = replace_bin(self.__position[j],k,"1")
                else:
                    self.__position[j] = replace_bin(self.__position[j],k,"0")"""

        for j in range(cf.get_population_size()):
            for k in range(cf.get_bin() * 2):
                r = np.random.rand()
                if r <= step_size:
                    self.__position[j] = replace_bin(self.__position[j],k,"1")
                else:
                    self.__position[j] = replace_bin(self.__position[j],k,"0")

        #p = np.random.randint(0, 4)
        #self.__position = self.__position[:p] + str(step_size) + self.__position[p + 1:]

        # 边界检测
        """for i in range(len(self.__position)):
            if self.__position[i] > cf.get_max_domain():
                self.__position[i] = cf.get_max_domain()
            if self.__position[i] < cf.get_min_domain():
                self.__position[i] = cf.get_min_domain()"""

    def print_info(self,i):
        print("id:","{0:3d}".format(i),
              "|| fitness:",str(self.__fitness).rjust(14," "),
              "|| position:",np.round(self.__position,decimals=4))


if __name__ == '__main__':
    print(levy_flight(cf.get_lambda()))

