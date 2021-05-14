import pandas as pd
import csv
import argparse
import pymysql

import function as fn
from config import Config as cf

period = cf.get_period()


def initialSourceDict(file, period):
    dict = {}
    data = pd.read_csv(file, usecols=[1], header=None)
    for unit in data[1]:
        dict[unit] = [1] * period
    return dict


def csv2dict(file):
    dict_club = {}
    with open(file) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            dict_club[row[0]] = eval(row[1])
    return dict_club


def dict2csv(dict, file):
    with open(file, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerows(dict.items())


# 初始化 教师, 班级 两张资源大表
# teacherDict = initialSource("data/teacher_inf.csv", period)
# studentDict = initialSource("data/student_inf.csv", period)
# dict2csv(teacherDict,"TeacherSource.csv")
# dict2csv(studentDict,"StudentSource.csv")


def from_mysql_get_all_info(argsYear, argsName):
    sql = 'select * from ' + argsName + ' where 所属年度 > ' + str(
        int(argsYear) - 4)
    with fn.get_connection() as con:
        with con.cursor() as cursor:
            cursor.execute(sql.encode('utf-8'))
            data = cursor.fetchall()
        con.commit()
    return data


def from_mysql_get_teacher_info(teacherTableName):
    sql = 'select * from ' + teacherTableName
    with fn.get_connection() as con:
        with con.cursor() as cursor:
            cursor.execute(sql.encode('utf-8'))
            data = cursor.fetchall()
        con.commit()
    return data


def write2csv(name, data):
    filename = 'data/' + name + '.csv'
    with open(filename, mode='w', encoding='utf-8', newline="") as f:
        write = csv.writer(f, dialect='excel')
        for item in data:
            write.writerow(item)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--loadTeacherTable",
                        default="teacher_inf",
                        type=str,
                        required=False,
                        help="输入教师总表名称")

    parser.add_argument("--loadStudentTable",
                        default="student_info",
                        type=str,
                        required=False,
                        help="输入班级总表名称")

    parser.add_argument("--loadStudentYear",
                        default="2020",
                        type=str,
                        required=False,
                        help="输入最新一届班级所属年度")
    args = parser.parse_args()

    sqlTeacher = "select * from mid_teacherorder"
    dataTeacher = fn.getDF(sqlTeacher)
    sqlCourse = "select * from mid_courseorder"
    dataCourse = fn.getDF(sqlCourse)
    # 读取数据库中的表格, 并且转化为csv文件
    student_inf = from_mysql_get_all_info(args.loadStudentYear,
                                          args.loadStudentTable)
    teacher_inf = from_mysql_get_teacher_info(args.loadTeacherTable)
    write2csv("student_inf", student_inf)
    write2csv("teacher_inf", teacher_inf)
    dataTeacher.to_csv("data/mid_teacherorder.csv")
    dataCourse.to_csv("data/mid_courseorder.csv")
    # 将csv文件转化为字典, 并且初始化资源池
    teacherDict = initialSourceDict("data/teacher_inf.csv", period)
    studentDict = initialSourceDict("data/student_inf.csv", period)
    dict2csv(teacherDict, "TeacherSource.csv")
    dict2csv(studentDict, "StudentSource.csv")

    #==== 对不监考的教师处理 ===#
    # 生成监考老师的字典
    data = pd.read_csv("data//teacher_inf.csv", header=None, usecols=[0, 1])
    dataTeacherMonitor = pd.read_csv("data/mid_teacherorder.csv",
                                     converters={
                                         u"tei_no": str,
                                         u"mti_id": int
                                     })
    dictTeacherTime = fn.csv2dict("TeacherSource.csv")

    numberTeacher = fn.buildConnectionDict(data, 0, 1)
    for mti_id, number in zip(dataTeacherMonitor["mti_id"],
                              dataTeacherMonitor["tei_no"]):
        teacher = numberTeacher[number][0]
        if mti_id == -1:
            dictTeacherTime[teacher] = [0] * period
        else:
            dictTeacherTime[teacher][mti_id] = 0

    dict2csv(dictTeacherTime, "TeacherSource.csv")
    print("初始化教师，班级状态成功。")
    
    #===== 对选定时间的公共课排考 ====#
    data = pd.read_csv("data//mid_course.csv", header=None, usecols=[2, 4])

if __name__ == "__main__":
    main()
