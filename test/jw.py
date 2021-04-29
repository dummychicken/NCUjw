import csv
import time as ti

import numpy as np
import pandas as pd

import function as fn
from config import Config as cf


st_time = ti.time()
period = cf.get_period()
limited = cf.get_limited()
threshold = cf.get_threshold()

#sql_data = """
            #select ci_course_no,ci_class_name,
            #ci_student_number,ci_teacher_name,ci_class_dep
            #from classs_inf
            #"""

data = pd.read_csv("test\class.csv", usecols=["ci_course_no","ci_class_name","ci_student_number","ci_teacher_name","ci_class_dep"])

#data = fn.getDF(sql_data)

# 数据预处理模板
#fn.pre_split_class(data) # 拆分同一行内按类似“1-3”的班级
data["ci_class_name"] = data["ci_class_name"].apply(fn.pre_split_class) # 拆分同一行内按类似“1-3”的班级

# 建立每个老师和时间的联系
dictTeacherTime = {}
for cl_ter_name in data["ci_teacher_name"]:
#for i in range(len(data)):
    #teacher = data.loc[i]["ci_teacher_name"]
    teacher = cl_ter_name
    if teacher is np.nan:
        continue
    elif ":" in teacher:
        teacherlist = teacher.split(":")
        for teachers in teacherlist:
            dictTeacherTime[teachers] = dictTeacherTime.get(teachers,[1]*period)
    else:
        dictTeacherTime[teacher] = dictTeacherTime.get(teacher,[1]*period)


# 建立所有学院和老师的联系
dataCollege = pd.read_csv("test\class.csv", usecols=["ci_class_dep","ci_teacher_name"])
dictCollegeTeacher = fn.buildConnectionDict(dataCollege, "ci_class_dep","ci_teacher_name")
# 建立课程和学院的联系
dataCourse = pd.read_csv("test\class.csv", usecols=["ci_class_dep","ci_course_no"])
dictCourseCollege = fn.buildConnectionDict(dataCourse,"ci_course_no","ci_class_dep")
# 建立课程和老师的联系
dataCourseTeacher = pd.read_csv("test\class.csv", usecols=["ci_course_no","ci_teacher_name"])
dictCourseTeacher = fn.buildConnectionDict(dataCourseTeacher,"ci_course_no","ci_teacher_name")

# 生成一个字典，对应的形式是这样的{"班级1":[],"班级2":[],"班级3":[],...}
dictClassTime = {}
for courseNumber in fn.SamplingCourse("test\class.csv"):
    course = courseNumber[0]
    temp = [1] * period
    tempTeacher = [1] * period
    classWhoTakeCourse = []
    classCourseNumber = []
    unitClass = []
    classTeacherList = []
    indexList = []
    unitTeacher = []

    for i,cl_name,cl_num,cl_ter,cl_co in zip(data.index,data["ci_class_name"],data["ci_student_number"],data["ci_teacher_name"],data["ci_course_no"].values):
        # 查找每一个考这门课的班级
        if cl_co == course:
            className = cl_name
            classNumber = cl_num
            # 保存班级人数和班级的时候以整体为单位
            classWhoTakeCourse.append(className)
            classCourseNumber.append(classNumber)
            indexList.append(i)

            # 取每个班级的公共时间
            splitClassList = fn.unitedClass(className) 
            for className in splitClassList:
                # 对考这门课的班级的时间进行初始化, 如果不存在就生成一个[1,1,1,1...,]
                dictClassTime[className] = dictClassTime.get(className,[1] * period)
                # 找到所有参加这门考试 班级的共同空闲时间
                # [0,1,1,...,] 和 [1,0,1,...,] 相与
                temp = fn.findCommonTime(temp,dictClassTime[className])
                unitClass.append(className)
            
            classTeacher = cl_ter
            classTeacherList.append(classTeacher)
            
            # 接下取监考老师的公共时间
            if ":" in classTeacher:
                teachersList = classTeacher.split(":")
                for teacher in teachersList:
                    tempTeacher = fn.findCommonTime(tempTeacher, dictTeacherTime[teacher])
                    unitTeacher.append(teacher)
            else:
                tempTeacher = fn.findCommonTime(tempTeacher,dictTeacherTime[classTeacher])
                unitTeacher.append(classTeacher)
    
    # 去除重复老师
    unitTeacher = list(set(unitTeacher))
    #print(len(unitTeacher))

    # 两个公共时间相与
    temp = fn.findCommonTime(tempTeacher,temp)
    
    # 判断监考老师是否足够, 不够从同学院找
    if len(unitTeacher) < courseNumber[1]:
        college = dictCourseCollege[course]
        collegeTeachers = dictCollegeTeacher[college[0]]
        for Teacher in collegeTeachers:
            if Teacher not in unitTeacher and fn.findCommonTime(dictTeacherTime[Teacher], tempTeacher) == tempTeacher:
                unitTeacher.append(Teacher)

    # 监考老师多了, 就选到只有这么多老师, 非常粗糙         
    if len(unitTeacher) > courseNumber[1]:
        unitTeacher = unitTeacher[0:courseNumber[1]]
    
    di = 0
    if len(unitTeacher) < courseNumber[1]:
        di = courseNumber[1] - len(unitTeacher)
        print(courseNumber[0]+"课程，当前老师不足，缺少"+str(courseNumber[1])+" - "+str(len(unitTeacher))+" = "+str(di)+"个，用-1代替")
        di_list = ["-1"]*di
        unitTeacher.extend(di_list)


    # 记录没有授课老师的情况
    #fn.writeImperfect(indexList,unitTeacher,data)

    if 1 not in temp:
        print("当前" + course +"无法排考")
    # 找到共同可行的时间, 写入csv, 并且标记占用时间
    else:
        _time = fn.optimalTime(temp)
        # newClassWhoTakeCourse, newClassCourseNumber = splitClass(classWhoTakeCourse,classCourseNumber)
        college = dictCourseCollege[course]
        fn.writeToCsv(_time,course,classWhoTakeCourse,classCourseNumber, unitTeacher,college)      
        # writeToCsv(temp,course,classWhoTakeCourse,classCourseNumber,college)              
        # 更新老师班级的时间表
        fn.updateClassTime(dictClassTime, unitClass, _time)
        fn.updateTeacherTime(dictTeacherTime, unitTeacher, _time,di)

print(ti.time() - st_time)
