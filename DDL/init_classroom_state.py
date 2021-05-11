import function as fn
import argparse
import os
os.chdir("/root/NCUTest/")
parser = argparse.ArgumentParser()

parser.add_argument("--building",
                    default="教学主楼,外经楼,法学楼,人文楼,建工楼,机电楼,信工楼,材料楼,环境楼,理生楼",
                    type=str,
                    required=False,
                    help='''输入要重置楼栋资源名称(例如：教学主楼,外经楼,法学楼,人文楼,
                    建工楼,机电楼,信工楼,材料楼,环境楼,理生楼),支持多资源输入(例如: 教学主楼,外经楼 )''')

args = parser.parse_args()

def main(args):
    fn.init_classroomState(args.building)
    print(args.building,"init_ok")
    #print("请确保输入的楼栋名称和下面的一致，例如：'人文'这种输入是无效的。")
    #print("教学主楼,外经楼,法学楼,人文楼,建工楼,机电楼,信工楼,材料楼,环境楼,理生楼")

if __name__ == "__main__":
    main(args)