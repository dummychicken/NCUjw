import numpy as np
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from config import Config as cf
import individual as id

sql_M = """
        select ci_course_no, ci_teacher_name, ci_class_name, ci_student_number, ci_appoint, ci_class_dep 
        from classs_inf 
        where ci_exam_type = '笔试考试' 
        and ci_class_sign = 1 and ci_student_number != 0 order by ci_course_no limit 0,1023 """ # 开课信息

sql_N = "select cr_name, cr_special, cr_testseat from classroom_inf" # 教室信息
#sql_T = "select "
#sql_D = "select cr_name, mti_no, cr_state from dm_classroom_state"
sql_D = "SELECT a.cr_name, a.cr_special, a.cr_testseat, b.mti_no, b.cr_state \
FROM classroom_inf a INNER JOIN dm_classroom_state b ON a.cr_name = b.cr_name WHERE 1=1 limit 0,1023"

def getDF(sql):           # 'mysql+pymysql://root:123456@123.60.8.234:3306/examArrange1'
    engin = create_engine('mysql+pymysql://root:ncu@jw114@123.60.11.177:3306/examArrange1')
    df = pd.read_sql_query(sql, engin)
    return df

df_sql_M = getDF(sql_M)
df_sql_D = getDF(sql_D)

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

def get_teacode(cs,i,j):
    return cs.get_position()[j][:cf.get_bin()]

def bin_ten(x):
    return int("0b" + x, 2)

def teacher_con(cs):
    for i in range(pop):
        for j in range(cf.get_bin()):
            tea_num = bin_ten(get_teacode(cs,i,j))
            tea_name = df_sql_M.iloc[tea_num][1]