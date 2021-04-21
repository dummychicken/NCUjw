import numpy as np
#from sklearn.utils.linear_assignment_ import linear_assignment
import sklearn

## 法1：使用sklearn的模块
cost_matrix = np.array([[1,4,7],[2,5,6],[6,7,1]]) #这里自己定义
#indices = linear_assignment(cost_matrix)
#indices = sklearn.linear_assignment(cost_matrix)
# indices 是一个n x 2的矩阵 对应代价矩阵的最大匹配的位置
#print(indices)


## 法2：使用scipy的模块
#from scipy.optimize import linear_sum_assignment
#row_ind, col_ind = linear_sum_assignment(cost_matrix)
#print([(x,y) for x,y in zip(row_ind,col_ind)])
# row_ind,col为代价矩阵最佳匹配元素的行号和列号