import pandas as pd
import csv
import argparse
import pymysql

from config import Config as cf

period = cf.get_period()

def initialSourceDict(file, period):
    dict = {}
    data = pd.read_csv(file, usecols=[1], header = None)
    for unit in data[1]:
        dict[unit] = [1] * period
    return dict

def csv2dict(file):
    dict_club={}
    with open(file)as f:
        reader=csv.reader(f,delimiter=',')
        for row in reader:
            dict_club[row[0]]=eval(row[1])
    return dict_club

def dict2csv(dict, file):
    with open(file,"w",encoding = "utf-8",newline = "") as f:
        w = csv.writer(f)
        w.writerows(dict.items())


# 初始化 教师, 班级 两张资源大表 
# teacherDict = initialSource("data/teacher_inf.csv", period)
# studentDict = initialSource("data/student_inf.csv", period)
# dict2csv(teacherDict,"TeacherSource.csv")
# dict2csv(studentDict,"StudentSource.csv")

def from_mysql_get_all_info(argsYear, argsName):
    conn = pymysql.connect(
        host='123.60.11.177',
        port=3306,
        user='root',
        db='examArrange1',
        password='ncu@jw114',
        charset='utf8mb4')
    cursor = conn.cursor()
    sql = 'select * from ' + argsName + ' where 所属年度 > ' + str(int(argsYear) - 4)
    cursor.execute(sql.encode('utf-8'))
    data = cursor.fetchall()
    conn.close()
    return data


def from_mysql_get_teacher_info(teacherTableName):
    conn = pymysql.connect(
        host='123.60.11.177',
        port=3306,
        user='root',
        db='examArrange1',
        password='ncu@jw114',
        charset='utf8mb4')
    cursor = conn.cursor()
    sql = 'select * from ' + teacherTableName
    cursor.execute(sql.encode('utf-8'))
    data = cursor.fetchall()
    conn.close()
    return data



def write2csv(name,data):
    filename = 'data/'+ name + '.csv'
    with open(filename, mode='w',encoding='utf-8',newline = "") as f:
        write = csv.writer(f,dialect='excel')
        for item in data:
            write.writerow(item)


def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--loadTeacherTable", default=None, type=str, required=True, help="输入教师总表名称"
        )

    parser.add_argument(
        "--loadStudentTable", default=None, type=str, required=True, help="输入班级总表名称"
    )

    parser.add_argument(
        "--loadStudentYear", default=None, type=str, required=True, help="输入最新一届班级所属年度"
        )
    args = parser.parse_args()
    
    # 读取数据库中的表格, 并且转化为csv文件
    student_inf = from_mysql_get_all_info(args.loadStudentYear,args.loadStudentTable)
    teacher_inf = from_mysql_get_teacher_info(args.loadTeacherTable)
    write2csv("student_inf",student_inf)
    write2csv("teacher_inf", teacher_inf)

    # 将csv文件转化为字典, 并且初始化资源池
    teacherDict = initialSourceDict("data/teacher_inf.csv", period)
    studentDict = initialSourceDict("data/student_inf.csv", period)
    dict2csv(teacherDict,"TeacherSource.csv")
    dict2csv(studentDict,"StudentSource.csv")

main()