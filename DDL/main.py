import csv
import re
import time as ti

import numpy as np
import pandas as pd
import argparse
import pymysql
import warnings
warnings.filterwarnings("ignore")
import function as fn

from config import Config as cf
from itertools import product

st_time = ti.time()
period = cf.get_period()
limited = cf.get_limited()
threshold = cf.get_threshold()

parser = argparse.ArgumentParser()
'''
parser.add_argument(
    "--loadCourseFile", default="class.csv", type=str, required=False, help="输入待排课表位置"
    )'''

parser.add_argument("--class_inf",
                    default="classs_inf",
                    type=str,
                    required=False,
                    help="待输入排考表名")

parser.add_argument("--outputFile",
                    default="排考最终结果.csv",
                    type=str,
                    required=False,
                    help="输入输出文件名")

parser.add_argument("--building",
                    default="信工楼",
                    type=str,
                    required=False,
                    help="输入指定楼栋资源名称(例如：教学主楼，外经楼，法学楼，人文楼，建工楼，机电楼，信工楼，材料楼，环境楼，理生楼)")

args = parser.parse_args()



def main(args):
    with open("temp.csv", "w") as f:
        csv_write = csv.writer(f)
        csv_write.writerow([])
    sql = "select ci_course_no,ci_teacher_name,ci_class_name,ci_student_number,ci_class_dep from " + args.class_inf + " where ci_teacher_name != ' ' and ci_class_dep = '信工学院'"

    data = fn.getDF(sql)
    #data = pd.read_csv(args.loadCourseFile, usecols=["ci_course_no","ci_class_name","ci_student_number","ci_teacher_name","ci_class_dep"])

    # 数据预处理模板 拆分同一行内按类似“1-3”的班级
    data["ci_class_name"] = data["ci_class_name"].apply(fn.pre_split_class)

    # 读取当前资源表
    dictTeacherTime = fn.csv2dict("TeacherSource.csv")
    dictStudentTime = fn.csv2dict("StudentSource.csv")

    # 建立所有学院和老师的联系
    #dataCollege = pd.read_csv(args.loadCourseFile, usecols=["ci_class_dep","ci_teacher_name"])
    dataCollege = pd.DataFrame(data,
                               columns=["ci_class_dep", "ci_teacher_name"])
    dictCollegeTeacher = fn.buildConnectionDict(dataCollege, "ci_class_dep",
                                                "ci_teacher_name")

    # 建立课程和学院的联系
    #dataCourse = pd.read_csv(args.loadCourseFile, usecols=["ci_class_dep","ci_course_no"])
    dataCourse = pd.DataFrame(data, columns=["ci_course_no", "ci_class_dep"])
    dictCourseCollege = fn.buildConnectionDict(dataCourse, "ci_course_no",
                                               "ci_class_dep")

    # 生成一个字典，对应的形式是这样的{"班级1":[],"班级2":[],"班级3":[],...}
    # dictClassTime = {}
    for courseNumber in fn.SamplingCourse(data):
        course = courseNumber[0]
        temp = [1] * period
        tempTeacher = [1] * period
        classWhoTakeCourse = []
        classCourseNumber = []
        unitClass = []
        #classTeacherList = []
        indexList = []
        unitTeacher = []

        for i, cl_name, cl_num, cl_ter, cl_co in zip(
                data.index, data["ci_class_name"], data["ci_student_number"],
                data["ci_teacher_name"], data["ci_course_no"].values):
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
                    dictStudentTime[className] = dictStudentTime.get(
                        className, [1] * period)
                    # 找到所有参加这门考试 班级的共同空闲时间
                    # [0,1,1,...,] 和 [1,0,1,...,] 相与
                    temp = fn.findCommonTime(temp, dictStudentTime[className])
                    unitClass.append(className)

                classTeacher = cl_ter
                #classTeacherList.append(classTeacher)

                # 接下取监考老师的公共时间
                if ":" in classTeacher:
                    teachersList = classTeacher.split(":")
                    for teacher in teachersList:
                        dictTeacherTime[teacher] = dictTeacherTime.get(
                            teacher, [1] * period)
                        tempTeacher = fn.findCommonTime(
                            tempTeacher, dictTeacherTime[teacher])
                        unitTeacher.append(teacher)
                else:
                    dictTeacherTime[classTeacher] = dictTeacherTime.get(
                        classTeacher, [1] * period)
                    tempTeacher = fn.findCommonTime(
                        tempTeacher, dictTeacherTime[classTeacher])
                    unitTeacher.append(classTeacher)

        # 去除重复老师
        unitTeacher = list(set(unitTeacher))

        # 两个公共时间相与
        temp = fn.findCommonTime(tempTeacher, temp)

        # 判断监考老师是否足够, 不够从同学院找
        if len(unitTeacher) < courseNumber[1]:
            college = dictCourseCollege[course]
            collegeTeachers = dictCollegeTeacher[college[0]]
            for Teacher in collegeTeachers:
                dictTeacherTime[Teacher] = dictTeacherTime.get(
                    Teacher, [1] * period)
                if Teacher not in unitTeacher and fn.findCommonTime(
                        dictTeacherTime[Teacher], tempTeacher) == tempTeacher:
                    unitTeacher.append(Teacher)

        # 监考老师多了, 就选到只有这么多老师, 非常粗糙
        if len(unitTeacher) > courseNumber[1]:
            unitTeacher = unitTeacher[0:courseNumber[1]]

        di = 0
        if len(unitTeacher) < courseNumber[1]:
            di = courseNumber[1] - len(unitTeacher)
            print(courseNumber[0] + "课程，当前老师不足，缺少" + str(di) + "个，用\"-1\"代替")
            di_list = ["-1"] * di
            unitTeacher.extend(di_list)

        # 记录没有授课老师的情况
        #fn.writeImperfect(indexList,unitTeacher,data)

        if 1 not in temp:
            print("当前" + course + "无法排考")
        # 找到共同可行的时间, 写入csv, 并且标记占用时间
        else:
            _time = fn.optimalTime(temp)
            # newClassWhoTakeCourse, newClassCourseNumber = splitClass(classWhoTakeCourse,classCourseNumber)
            college = dictCourseCollege[course]
            fn.writeToCsv(_time, course, classWhoTakeCourse, classCourseNumber,
                          unitTeacher, college)
            # writeToCsv(temp,course,classWhoTakeCourse,classCourseNumber,college)
            # 更新老师班级的时间表
            fn.updateClassTime(dictStudentTime, unitClass, _time)
            fn.updateTeacherTime(dictTeacherTime, unitTeacher, _time, di)
    fn.dict2csv(dictTeacherTime, "TeacherSource.csv")
    fn.dict2csv(dictStudentTime, "StudentSource.csv")

    #===== 连接数据库=====#
    temp = pd.read_csv("./temp.csv",
                       names=[
                           "ci_course_no", "test_time", "ci_class_name",
                           "ci_student_number", "ci_teacher_name",
                           "ci_class_unit"
                       ])
    temp.insert(0, "index", temp.index.values)

    sql_res = "select * from dm_classroom_state_new"
    dm_classroom_state_new = fn.getDF(sql_res)

    D = dm_classroom_state_new

    PreCollege = args.building
    Commen_building = D[D["cr_building"] == "教学主楼"]
    Private_building = D[D["cr_building"] == PreCollege]
    UsedRe = Commen_building.append(Private_building)

    # 课程 -> index 字典
    tmp_c = pd.DataFrame(temp,columns=["ci_course_no","index"])
    dict_tmp_c = fn.buildConnectionDict_Class(tmp_c, "ci_course_no","index")

    PreCollegeAllData, cannt_find_class_id = fn.schedule_algorithm(
        UsedRe, temp, dict_tmp_c)
    PreCollegeoutdata = PreCollegeAllData[PreCollegeAllData.cr_state == 0]
    
    dfoutdata = PreCollegeoutdata
    dfcannt_find_class_id = cannt_find_class_id
    dfSyncdata = dfoutdata

    # 同步教室资源状态
    fn.SyncBuildingState(dfSyncdata)

    dfoutdata = dfoutdata.rename(columns={"state_id": "index"})
    df = pd.merge(temp, dfoutdata, how='inner',
                  on=["index"]).iloc[:, [1, 2, 3, 4, 5, 8, 7]]
    cannt_temp = temp[temp.apply(lambda x: x[0] in dfcannt_find_class_id,
                                 axis=1)]

    df.to_csv(args.outputFile)
    cannt_temp.to_csv("canntArrangeClass.csv", mode="a")
    print(ti.time() - st_time)

    return print("Exam ready")

if __name__ == "__main__":
    main(args)

# 此处由于写入数据库速度过慢, 先注掉
# fn.uploadCsv("TeacherSource.csv")
# fn.uploadCsv("StudentSource.csv")