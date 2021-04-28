import pandas as pd
import csv
import argparse
from config import Config as cf

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


period = cf.get_period()

# 初始化 教师, 班级 两张资源大表 
# teacherDict = initialSource("data/teacher_inf.csv", period)
# studentDict = initialSource("data/student_inf.csv", period)
# dict2csv(teacherDict,"TeacherSource.csv")
# dict2csv(studentDict,"StudentSource.csv")

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--loadTeacherFile", default=None, type=str, required=True, help="输入教师总表位置"
        )
    parser.add_argument(
        "--loadStudentFile", default=None, type=str, required=True, help="输入班级总表位置"
    )

    args = parser.parse_args()
    
    teacherDict = initialSourceDict(args.loadTeacherFile, period)
    studentDict = initialSourceDict(args.loadStudentFile, period)
    dict2csv(teacherDict,"TeacherSource.csv")
    dict2csv(studentDict,"StudentSource.csv")

main()