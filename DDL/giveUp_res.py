import csv

import pandas as pd
import argparse
import warnings

warnings.filterwarnings("ignore")
import function as fn

from config import Config as cf


parser = argparse.ArgumentParser()

parser.add_argument("--giveup",
                    type=str,
                    required=True,
                    help="输入要放弃的排考结果表名，例如：commonClass_res")

args = parser.parse_args()

def main(args):
    sql = "select test_time,ci_class_name,ci_teacher_name,cr_name from " + args.giveup
    fn.giveUpCourseRange(sql)

if __name__ == "__main__":
    try:
        main(args)
    except:
        print("请检查输入的文件名是否正确，放弃排考结果失败。")
    else:
        sql_truncate_res = "TRUNCATE TABLE " + args.giveup
        sql_truncate_cannt = "TRUNCATE TABLE " + args.giveup[:-3] + "cannt"
        fn.executeSQL(sql_truncate_res)
        fn.executeSQL(sql_truncate_cannt)
        print("成功放弃指定排考结果，已释放对应资源。")
    