import csv 
import re 
import pandas as pd
import numpy as np
import numba as nb

from config import Config as cf
from sqlalchemy import create_engine

period = cf.get_period

# 按照每门课程的考试班级数目进行排序
def SamplingCourse(file):
    with open(file,"r",encoding="UTF-8") as f:
        reader = csv.reader(f)
        column = [row[0] for row in reader]
    hashmapClass = {}
    for i in range(len(column)):
        hashmapClass[column[i]] = hashmapClass.get(column[i],0) + 1
    sortedCourse = sorted(hashmapClass.items(), key=lambda d:d[1], reverse = True)
    return sortedCourse[15:500]

# 找出共同能考试的时间
def findCommonTime(temp, listClass):
    commonTime = []
    for i in range(len(temp)):
        commonTime.append(temp[i] & listClass[i])
    return commonTime

# 尽可能使考试平均分布
def optimalTime(temp):
    pt1 = 0
    pt2 = len(temp)
    while pt1 != pt2-1:
        mid = ( pt1 + pt2 ) // 2 
        if sum(temp[pt1:mid]) < sum(temp[mid:pt2]):
            pt1 = mid
        else:
            pt2 = mid
    if sum(temp[pt1: pt1+2]) <= 1:
        return temp.index(1)
    else:
        return pt1

# 将结果写入表中
def writeToCsv(time, course, classes, number, teacher, college):
    course = [course] * len(classes)
    time = [time] * len(classes)
    college = [college[0]] * len(classes)
    test = pd.DataFrame({'课程': course, "考试时间": time, "班级": classes,"班级人数": number, "监考老师": teacher, "开课学院": college})
    test.to_csv("temp.csv",encoding = "utf-8",mode="a",index = None, header = False)

# 讲已经排考成功的1修改成0, 如[1,1,1,1]->[0,1,1,1] 维护表
def updateClassTime(dict, listclass, index):
    for classes in listclass:
        dict[classes][index] = 0
    return dict

def updateTeacherTime(dict, listclass, index,di):
    for classes in listclass:
        if classes == "-1":
            break
        dict[classes][index] = 0
    return dict

# 函数的效果是对班级进行统计, 目的是每个班级必须有一个考试时间表 
# 比如 "行政管理[193-4]班,人工智能191班" -> ['行政管理193班', '行政管理194班', '人工智能191班']
def unitedClass(strClass):
    listClasses = strClass.split(",")
    splitClassList = []
    for classes in listClasses:
        if "-" in classes:
            middleIndex = classes.index("-")
            firstIndex = classes.index("[")
            lastIndex = classes.index("]")
            lastClassNum = int(classes[middleIndex + 1 :lastIndex])
            firstClassNum = int(classes[middleIndex - 1])
            for i in range( firstClassNum, lastClassNum + 1):
                splitClassList.append(classes[0:firstIndex] + classes[firstIndex + 1:middleIndex-1] + str(i) + "班")
        else:
            splitClassList.append(classes)
    return splitClassList

# 数据预处理，输入排课表,根据规则拆分班级
# '土木工程（建筑工程方向）[181-3]班,土木工程（地下工程方向）181班' ——>
# '土木工程（建筑工程方向）181班,土木工程（建筑工程方向）182班,土木工程（建筑工程方向）183班,土木工程（地下工程方向）181班'   
'''def pre_split_class(data):
    class_name = data["ci_class_name"]
    for inx, val in enumerate(class_name):
        st = ''
        for s in unitedClass(str(val)):
            st = st + s + ","
        data.iloc[inx,2] = st[:-1]'''
def pre_split_class(data):
    #print(data)
    st = ''
    for s in unitedClass(str(data)):
         st = st + s + ","
    return st[:-1]

# 这里是在定义拆分规则
# 可以人数超出阈值, 则拆分班级, 如果人数没有超过, 就不拆
# 可以避免合班的问题

def splitClass(classWhoTakeCourse,classCourseNumber):
    newClassWhoTakeCourse = []
    newClassCourseNumber = []
    for i in range(len(classCourseNumber)):
        # 这个数字怎么订 还是要看教室的具体规模
        if classCourseNumber[i] > 80:
            classes = unitedClass(classWhoTakeCourse[i])
            # 如果拆分出来的班级小于30人, 就没有必要拆
            if classCourseNumber[i] // len(classes) <= 30:
                newClassCourseNumber.append(classCourseNumber[i])
                newClassWhoTakeCourse.append(classWhoTakeCourse[i])
            else:
                for unit in classes:
                    newClassWhoTakeCourse.append(unit)
                    # 这里需要插一段每个班级真正人数的查询
                    # 这里是偷懒取了个平均 
                    newClassCourseNumber.append(classCourseNumber[i]//len(classes))
        else:
            newClassCourseNumber.append(classCourseNumber[i])
            newClassWhoTakeCourse.append(classWhoTakeCourse[i])
    return newClassWhoTakeCourse, newClassCourseNumber



# 建立每个key和value的联系
# 比如 课程 和 老师
def buildConnectionDict(data, key, value):
    dictKeyValue = {}
    for key,val in zip(data[key],data[value]):
    #for i in range(len(data)):
        keyName = key
       #keyName = data.loc[i][key]
        dictKeyValue[keyName] = dictKeyValue.get(keyName,[])
        #valueName = data.loc[i][value]
        valueName = val
        if valueName is np.nan:
            continue
        elif ":" in valueName:
            valueList = valueName.split(":")
            for values in valueList:
                dictKeyValue[keyName].append(values)
        else:
            dictKeyValue[keyName].append(valueName)
    for key,value in dictKeyValue.items():
        value = list(set(value))
        dictKeyValue[key] =  value
    return dictKeyValue

# 记录不完美情况
def writeImperfect(index,TeacherList,data):
    rows = []
    for i in range(len(index)):
        if TeacherList[i] not in data.iloc[index[i]]["ci_teacher_name"]:
            writeUnitRow = []
            writeUnitRow.append(index[i])
            for unit in range(len(data.iloc[0])):
                writeUnitRow.append(data.iloc[index[i]][unit])
            rows.append(writeUnitRow)
    with open("test\imperfect.csv","a",encoding = "utf-8",newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def getDF(sql):   # 'mysql+pymysql://root:123456@123.60.8.234:3306/examArrange1'
    engin = create_engine('mysql+pymysql://root:ncu@jw114@123.60.11.177:3306/examArrange1')
    df = pd.read_sql_query(sql, engin)
    return df