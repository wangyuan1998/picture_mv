import json
from subprocess import Popen, PIPE, STDOUT
import os
from multiprocessing import Process

def run_bat(track_bat_path):
    p = Popen("cmd.exe /c"+track_bat_path, stdout=PIPE, stderr=STDOUT)
    curline= p.stdout.readline()
    while(curline!=b''):
        curline = p.stdout.readline()
    p.wait()

def track_19(video_path, data_type, x1, y1, w, h):
    template_json_path = "./test_data/template_tracking.json"
    json_path = "F:/Tracking/Scripts/tracking/tracking.json"
    result_txt_path = ""
    result_jpg_path = ""

    # 加载模板json
    json_file = open(template_json_path, 'r', encoding='utf-8')
    json_data = json.load(json_file)
    json_file.close()

    # set ReturnCode to 0
    json_data["OutputParameter"]["ProgramStatus"][0]["value"] = 0

    # 设置InputFileName，DataType，initRect
    json_data["InputParameter"]["InputFilePath"][0]["value"] = video_path
    json_data["InputParameter"]["DataType"]["value"] = data_type
    json_data["InputParameter"]["initRect"]["x1"] = x1
    json_data["InputParameter"]["initRect"]["y1"] = y1
    json_data["InputParameter"]["initRect"]["w"] = w
    json_data["InputParameter"]["initRect"]["h"] = h

    # 优化输出
    json_data['OutputParameter']['OutputResult'][0]['x1'] = x1
    json_data['OutputParameter']['OutputResult'][0]['y1'] = y1
    json_data['OutputParameter']['OutputResult'][0]['w'] = w
    json_data['OutputParameter']['OutputResult'][0]['h'] = h

    # 储存json
    json_file = open(json_path, 'w', encoding='utf-8')
    # print(json_data)
    json.dump(json_data, json_file, indent=4, ensure_ascii=False)
    json_file.close()

    # 启动跟踪脚本
    track_bat_path = "F:/Tracking/Scripts/tracking/tracking.bat"
    new_process = Process(target=run_bat, args=(track_bat_path,))
    new_process.start()



if __name__ == '__main__':
    video_path = "F:/ODER_dataset/Track/1_Car_02"
    data_type = "RemoteSensing"
    x1 = 607.5038226064668
    y1 = 945.4969367514609
    w = 20.4387933927495
    h = 14.06057090509093

    track_19(video_path, data_type, x1, y1, w, h)