import numpy as np
import individual as id
import function as fn
import sys
import os
import csv
from config import Config as cf


if os.path.exists("results"):
    pass
else:
    os.mkdir("results")

results = open("results" + os.sep + "results.csv", "w")
results_writer = csv.writer(results, lineterminator="\n")


def main():
    pop = cf.get_population_size()
    list_cl = []
    for i in range(pop):
        list_cl.append(str(bin(i)).replace("0b","").zfill(cf.get_bin()))
    list_m = []
    for i in range(pop):
        list_m.append(str(bin(i)).replace("0b","").zfill(cf.get_bin()))


    for trial in range(cf.get_trial()):
        np.random.seed(trial)

        init_pos = []
        position_list = []
        results_list = [] # fitness list
        cs_list = []
        # 初始化 初始解
        for p in range(pop):
            k = np.random.choice(pop,pop,replace=False)
            for i in k:
                #k = int(np.random.randint(0,pop))
                init_pos.append(list_cl[p] + list_m[i])
            cs_list.append(id.Individual(init_pos))
            init_pos = []

        for i in cs_list:
            print(i.get_position())
            
        # 排序, 找到最优解
        cs_list = sorted(cs_list, key=lambda ID: ID.get_fitness())

        # 找到初始最优解
        BestPosition = cs_list[0].get_position()
        #BestFitness = fn.calculation(cs_list[0].get_position(),0)
        BestFitness = cs_list[0].get_fitness()

        # 主循环
        for iteration in range(cf.get_iteration()):

            # 通过Levy飞行产生新解
            for i in range(len(cs_list)):
                cs_list[i].get_cuckoo()
                cs_list[i].set_fitness(np.random.rand())
                #cs_list[i].set_fitness(fn.calculation(cs_list[i].get_position(),iteration))

                """random choice (say j)"""
                j = np.random.randint(low=0, high=cf.get_population_size())
                while j == i: #random id[say j] ≠ i
                    j = np.random.randint(0, cf.get_population_size())

                # for minimize problem
                if(cs_list[i].get_fitness() < cs_list[j].get_fitness()):
                    cs_list[j].set_position(cs_list[i].get_position())
                    cs_list[j].set_fitness(cs_list[i].get_fitness())

            # 排序, 找到最优解并保留
            cs_list = sorted(cs_list, key=lambda ID: ID.get_fitness())

            # 除了最好的那个, 其他鸟巢根据概率P被放弃
            k = np.random.choice(range(1,pop),pop - 1,replace=False)
            ks = slice(0,round(cf.get_Pa()*pop))
            for i in k[ks]:
                cs_list[i].abandon()
                cs_list[i].set_fitness(np.random.rand())
                #cs_list[a].set_fitness(fn.calculation(cs_list[a].get_position(),iteration))

            # 排序, 找到最优解
            cs_list = sorted(cs_list, key=lambda ID: ID.get_fitness())

            if cs_list[0].get_fitness() < BestFitness:
                BestFitness = cs_list[0].get_fitness()
                BestPosition = cs_list[0].get_position()

            sys.stdout.write("\r Trial:%3d , Iteration:%7d, BestFitness:%.4f" % (trial , iteration, BestFitness))
            #results_list.append(str(BestFitness))
            results_writer.writerow(BestPosition)
            #position_list.append(str(BestPosition))
       
        #results_writer.writerow(position_list)

if __name__ == '__main__':
    main()
    results.close()