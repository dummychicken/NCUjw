import numpy as np

"""
[Reference]
https://www.sfu.ca/~ssurjano/index.html
"""


def calculation(array, t):#as you want
    fitness = schwefel(array)
    return fitness

"""Benchmark Functions"""
def eggholder(array):
    z = - (array[1] + 47) * np.sin(np.sqrt(abs(array[1] + (array[0]/2) +47))) - array[0] *np.sin(np.sqrt(abs(array[0] - (array[1]+47))))
    return z

def sphere(array):
    fitness = 0
    for i in range(len(array)):
        fitness = fitness + array[i]**2
    return fitness

def rastrigin(array):
    sum = 0
    fitness = 0
    for x in array:
        sum = sum + x**2 - 10 * np.cos(2 * np.pi * x)
    fitness = 10.0 * len(array) + sum
    return fitness

def schwefel(array):
    sum = 0
    fitness = 0
    for x in array:
        sum = sum + x * np.sin(np.sqrt(np.abs(x)))
    fitness = 418.9829 * len(array) - sum
    return fitness

def michalewicz(array):#for the number of Dimension is 2
    sum = 0
    fitness = 0
    m = 10
    for (i,x) in enumerate(array, start=1):
        sum = sum + np.sin(x) * np.sin((i * (x**2) )/np.pi)**(2*m)
    fitness = -sum
    return fitness

def sigmoid_KE(x):
    if x >= 0:
        return 1 / (1 + np.exp(-x))
    else:
        return np.exp(x) / (1 + np.exp(x))

def sigmoid_Liu(x):
    if x <= 0:
        return 1 - 2 / (1 + np.exp(-x))
    else:
        return 2 / (1 + np.exp(-x)) - 1

def binary_KE(x):
    p = np.random.rand()
    if p <= x:
        return 1
    else:
        return 0

def binary_Liu(x,k):
    if x <= 0:
        if np.random.rand() <= x:
            return 0
        else:
            return k
    else:
        if np.random.rand() <= x:
            return 1
        else:
            return k
            

if __name__ == '__main__':
    a = np.array([2.20,1.0])
    print (michalewicz(a))
