import csv
import re
import os
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

os.chdir("/root/NCUTest/")

st_time = ti.time()
period = cf.get_period()
limited = cf.get_limited()
threshold = cf.get_threshold()

parser = argparse.ArgumentParser()
'''
parser.add_argument(
    "--loadCourseFile", default="class.csv", type=str, required=False, help="输入待排课表位置"
    )'''
#, default="classs_inf" ,default="排考最终结果.csv"
parser.add_argument("--class_inf",
                    type=str,
                    required=True,
                    help="待输入排考表名, 例如：classs_inf")
'''
parser.add_argument("--outputFile",
                    type=str,
                    required=True,
                    help="输入输出文件名，例如：排考最终结果.csv")'''

parser.add_argument("--building",
                    default="",
                    type=str,
                    required=False,
                    help="输入指定楼栋资源名称(例如：教学主楼，外经楼，法学楼，人文楼，建工楼，机电楼，信工楼，材料楼，环境楼，理生楼)")

args = parser.parse_args()


res_name = args.class_inf + "_res"
cannt_name = args.class_inf + "_cannt"

print(res_name)
print(cannt_name)