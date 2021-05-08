import csv
import re
import pandas as pd
import numpy as np
import pymysql

from contextlib import contextmanager
from config import Config as cf
from sqlalchemy import create_engine

period = cf.get_period
host = cf.get_host()
port = cf.get_port()
user = cf.get_user()
password = cf.get_password()
db = cf.get_db()
connURL = 'mysql+pymysql://' + user + ":" + password + '@' + host + ':' + port + '/' + db

# 按照每门课程的考试班级数目进行排序
'''def SamplingCourse1(file):
    with open(file,"r",encoding="UTF-8") as f:
        reader = csv.reader(f)
        column = [row[0] for row in reader]
    hashmapClass = {}
    for i in range(len(column)):
        hashmapClass[column[i]] = hashmapClass.get(column[i],0) + 1
    sortedCourse = sorted(hashmapClass.items(), key=lambda d:d[1], reverse = True)
    return sortedCourse[15:500]'''


def SamplingCourse(column):
    hashmapClass = {}
    for i in column["ci_course_no"]:
        hashmapClass[i] = hashmapClass.get(i, 0) + 1
    sortedCourse = sorted(hashmapClass.items(),
                          key=lambda d: d[1],
                          reverse=True)
    return sortedCourse


# 找出共同能考试的时间
def findCommonTime(temp, listClass):
    commonTime = []
    for i in range(len(temp)):
        commonTime.append(temp[i] & listClass[i])
    return commonTime


# 尽可能使考试平均分布，优先每天安排一场，其次一天两场，最后没办法一天三场。
def optimalTime(temp):
    temp_list_hfday = [temp[i:i + 2] for i in range(0, len(temp), 2)]
    temp_list_oneday = [temp[i:i + 4] for i in range(0, len(temp), 4)]
    for inx, val in enumerate(temp_list_oneday):
        if sum(val) < 4:
            continue
        else:
            return inx * 4 + np.random.randint(0, 4)
    rd = np.random.choice(len(temp) // 2, len(temp) // 2, replace=False)
    for i in rd:
        if sum(temp_list_hfday[i]) < 2:
            continue
        elif len(temp) % 2 == 0:
            return i * 2 + np.random.randint(0, 2)
        else:
            return i * 2
    k = np.random.choice(len(temp), len(temp), replace=False)
    for i in k:
        if temp[i] == 1:
            return i


''' 

    for inx,val in enumerate(temp_list_hfday):
        if sum(val) < 2:
            continue
        else:
            return inx * 2 + np.random.randint(0,2)
    k = np.random.randint(0,len(temp))
    while True:
        if temp[k] == 1:
            return k
        else:
            k = np.random.randint(0,len(temp))
       
def optimalTime(temp):        
    pt1 = 0
    pt2 = len(temp)
    while pt1 != pt2-1:
        mid = ( pt1 + pt2 ) // 2 
        if sum(temp[pt1:mid]) < sum(temp[mid:pt2]):
            pt1 = mid
        else:
            pt2 = mid
        #if pt2 - pt1 <
    if sum(temp[pt1: pt1+2]) <= 1:
        return temp.index(1)
    else:
        return pt1'''


# 将结果写入表中
def writeToCsv(time, course, classes, number, teacher, college):
    course = [course] * len(classes)
    time = [time] * len(classes)
    college = [college[0]] * len(classes)
    test = pd.DataFrame({
        '课程': course,
        "考试时间": time,
        "班级": classes,
        "班级人数": number,
        "监考老师": teacher,
        "开课学院": college
    })
    test.to_csv("temp.csv",
                encoding="utf-8",
                mode="a",
                index=None,
                header=False)


# 讲已经排考成功的1修改成0, 如[1,1,1,1]->[0,1,1,1] 维护表
def updateClassTime(dict, listclass, index):
    for classes in listclass:
        dict[classes][index] = 0
    return dict


def updateTeacherTime(dict, listclass, index, di):
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
            lastClassNum = int(classes[middleIndex + 1:lastIndex])
            firstClassNum = int(classes[middleIndex - 1])
            if lastClassNum > 100:
                lastClassNum = int(str(lastClassNum)[2:])
                for i in range(firstClassNum, lastClassNum + 1):
                    splitClassList.append(classes[0:firstIndex] +
                                        classes[firstIndex + 1:middleIndex - 1] +
                                        str(i) + "班")
            else:
                for i in range(firstClassNum, lastClassNum + 1):
                    splitClassList.append(classes[0:firstIndex] +
                                        classes[firstIndex + 1:middleIndex - 1] +
                                        str(i) + "班")
        else:
            splitClassList.append(classes)
    return splitClassList


# 数据预处理，输入排课表,根据规则拆分班级
# '土木工程（建筑工程方向）[181-3]班,土木工程（地下工程方向）181班' ——>
# '土木工程（建筑工程方向）181班,土木工程（建筑工程方向）182班,土木工程（建筑工程方向）183班,土木工程（地下工程方向）181班'
def pre_split_class(data):
    #print(data)
    st = ''
    for s in unitedClass(str(data)):
        st = st + s + ","
    return st[:-1]


# 这里是在定义拆分规则
# 可以人数超出阈值, 则拆分班级, 如果人数没有超过, 就不拆
# 可以避免合班的问题


def splitClass(classWhoTakeCourse, classCourseNumber):
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
                    newClassCourseNumber.append(classCourseNumber[i] //
                                                len(classes))
        else:
            newClassCourseNumber.append(classCourseNumber[i])
            newClassWhoTakeCourse.append(classWhoTakeCourse[i])
    return newClassWhoTakeCourse, newClassCourseNumber


# 建立每个key和value的联系
# 比如 课程 和 老师
def buildConnectionDict(data, key, value):
    dictKeyValue = {}
    for key, val in zip(data[key], data[value]):
        #for i in range(len(data)):
        keyName = key
        #keyName = data.loc[i][key]
        dictKeyValue[keyName] = dictKeyValue.get(keyName, [])
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
    for key, value in dictKeyValue.items():
        value = list(set(value))
        dictKeyValue[key] = value
    return dictKeyValue

def buildConnectionDict_Class(data, key, value):
    dictKeyValue = {}
    for key, val in zip(data[key], data[value]):
        #for i in range(len(data)):
        keyName = key
        #keyName = data.loc[i][key]
        dictKeyValue[keyName] = dictKeyValue.get(keyName, [])
        #valueName = data.loc[i][value]
        valueName = val
        if valueName is np.nan:
            continue
        else:
            dictKeyValue[keyName].append(valueName)
    for key, value in dictKeyValue.items():
        value = list(set(value))
        dictKeyValue[key] = value
    return dictKeyValue

# 记录不完美情况
def writeImperfect(index, TeacherList, data):
    rows = []
    for i in range(len(index)):
        if TeacherList[i] not in data.iloc[index[i]]["ci_teacher_name"]:
            writeUnitRow = []
            writeUnitRow.append(index[i])
            for unit in range(len(data.iloc[0])):
                writeUnitRow.append(data.iloc[index[i]][unit])
            rows.append(writeUnitRow)
    with open("monitorNotTeacher.csv", "a", encoding="utf-8",
              newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def initialSourceDict(file, period):
    dict = {}
    data = pd.read_csv(file, usecols=[1], header=None)
    for unit in data[1]:
        dict[unit] = [1] * period
    return dict


def csv2dict(file):
    dict_club = {}
    with open(file, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            dict_club[row[0]] = eval(row[1])
    return dict_club


# def csv2dict(in_file,key,value):
#     new_dict = {}
#     with open(in_file, 'rb') as f:
#         reader = csv.reader(f, delimiter=',')
#         fieldnames = next(reader)
#         reader = csv.DictReader(f, fieldnames=fieldnames, delimiter=',')
#         for row in reader:
#             new_dict[row[key]] = row[value]
#     return new_dict


def dict2csv(dict, file):
    with open(file, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerows(dict.items())


# def dict2csv(dict,file):
#     with open(file,'w',encoding = "utf-8",newline = "") as f:
#         w=csv.writer(f)
#         # write all keys on one row and all values on the next
#         w.writerow(dict.keys())
#         w.writerow(dict.values())


def getDF(sql):  # 'mysql+pymysql://root:123456@123.60.8.234:3306/examArrange1'
    engin = create_engine(connURL)
    df = pd.read_sql_query(sql, engin)
    engin.dispose()
    return df


def uploadCsv(file):
    engine = create_engine(connURL)
    df = pd.read_csv(file, sep=',')
    df.to_sql(file[:-4], con=engine, if_exists='replace', index=False)
    engine.dispose()

# def uploadCsv(file):
#     # 连接MySQL数据库（注意：charset参数是utf8而不是utf-8）
#     conn = pymysql.connect(host='123.60.11.177', user='root', password='ncu@jw114', db='examArrange1', charset='utf8')
#     # 创建游标对象
#     cursor = conn.cursor()
#     # 读取csv文件
#     with open(file, 'r', encoding='utf-8') as f:
#         read = csv.reader(f)
#         # 一行一行地存，除去第一行和第一列
#         for each in list(read)[1:]:
#             #i = tuple(each[1:])
#             # 使用SQL语句添加数据
#             sql = "INSERT INTO TeacherSource VALUES"  + str(each)  # db_top100是表的名称
#             cursor.execute(sql) #执行SQL语句
#         conn.commit() # 提交数据
#         cursor.close() # 关闭游标
#         conn.close() # 关闭数据库


def get_columns(info_COLUMNS):
    lst = []
    for i in info_COLUMNS:
        lst.append(i[0])
    return lst


def get_dm_classroom_state_new(res):
    cr_building = []
    cr_name = []
    cr_testseat = []
    for i in np.array(res)[:, 0]:
        cr_building.append(i[0])
        cr_name.append(i[1])
        cr_testseat.append(i[2])
    dm_classroom_state_new = np.c_[cr_building, cr_name, cr_testseat,
                                   np.array(res)[:, 1]]
    dm_classroom_state_new = pd.DataFrame(
        dm_classroom_state_new,
        columns=["cr_building", "cr_name", "cr_testseat", "mti_no"])
    dm_classroom_state_new["cr_state"] = 1
    return dm_classroom_state_new.reset_index().rename(
        columns={"index": "state_id"})




def fill_bz(new_D, room_name, test_time):
    new_D.loc[(new_D.cr_name == room_name) & (new_D.mti_no == test_time), "cr_state"] = 0
    return 0


# 当前的教室对应的班级index
def change_state_id(new_D, room_name, test_time, i):
    new_D.loc[(new_D.cr_name == room_name) & (new_D.mti_no == test_time), "state_id"] = i
    return 0


# 判断当前考场是否安排
def classroom_isbz(new_D, cr_name, time_no):
    return (new_D[(new_D.cr_name == cr_name)
                  & (new_D.mti_no == time_no)].cr_state == 0).values == False


# 判断当前时段的教室是否符合当前的课程
def student_num_fit(new_D, cr_names, cl_num):
    cr_num = int(new_D[new_D.cr_name == cr_names].cr_testseat.values[0]) // cf.get_crEffective()
    if (cr_num >= cl_num and cl_num / cr_num >= cf.get_crRatio()):
        return True
    else:
        return False

# 根据时间段找到所有可用教室        
def get_test_time_room(new_D, test_time):
    test_time_room = new_D[(new_D.mti_no == test_time)
                           & (new_D.cr_state == 1)].cr_name.values
    return test_time_room


def schedule_algorithm(D, temp, dict_tmp_c):
    cannt_find_class_id = []
    preList = list(dict_tmp_c)
    for preCourse in preList:
        idx_list = dict_tmp_c[preCourse]
        cou_len = len(idx_list)
        tmp_room = []
        for i, cl_num, test_time in zip(dict_tmp_c[preCourse], temp["ci_student_number"][idx_list[0] : idx_list[-1] + 1], temp["test_time"][idx_list[0] : idx_list[-1] + 1]):
            flag = 1
            test_time_room = sorted(get_test_time_room(D, test_time))
            com_res = []
            pri_res = []
            for res in test_time_room:
                if re.match('教',res):
                    com_res.append(res)
                else:
                    pri_res.append(res)
            if len(com_res) >= cou_len:
                for room_name in com_res:
                    if classroom_isbz(D, room_name, test_time) and student_num_fit(D, room_name, cl_num) and room_name not in tmp_room:
                        fill_bz(D, room_name, test_time)
                        change_state_id(D, room_name, test_time, i)
                        flag = 0
                        tmp_room.append(room_name)
                        break
            elif len(pri_res) >= cou_len:
                for room_name in pri_res:
                    if classroom_isbz(D, room_name, test_time) and student_num_fit(D, room_name, cl_num) and room_name not in tmp_room:
                        fill_bz(D, room_name, test_time)
                        change_state_id(D, room_name, test_time, i)
                        flag = 0
                        tmp_room.append(room_name)
                        break
            if flag == 1:
                cannt_find_class_id.append(i)
    return D, cannt_find_class_id

@contextmanager
def get_connection():
    connection = pymysql.connect(host=cf.get_host(),
                        port=int(cf.get_port()),
                        user=cf.get_user(),
                        password=cf.get_password(),
                        db=cf.get_db(),
                        charset='utf8mb4')
    try:
        yield connection
    finally:
        connection.close()
        
def SyncBuildingState(dfSyncdata):
    list_df = []
    for name, mti in zip(dfSyncdata["cr_name"],dfSyncdata["mti_no"]):
        list_df.append((name,mti))
    sql_Sync = "update dm_classroom_state_new set cr_state = '0' where cr_name = %s and mti_no = '%s'"
    with get_connection() as con:
        with con.cursor() as cursor:
            cursor.executemany(sql_Sync,list_df)
        con.commit()

def init_classroomState(building):
    list_b = []
    list_b.extend(building.split(","))
    sql_init = "UPDATE dm_classroom_state_new SET cr_state = 1 WHERE cr_building in " + str(tuple(list_b))
    with get_connection() as con:
        with con.cursor() as cursor:
            cursor.execute(sql_init)
        con.commit()