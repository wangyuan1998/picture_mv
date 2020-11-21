import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
import sys
from PyQt5.QtWidgets import QDockWidget
import cv2
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import QRect, Qt, QTimer
import datetime
from function_buttons_event import *
import json
from shutil import copyfile

def qtpixmap_to_cvimg(qtpixmap):
    qimg = qtpixmap.toImage()
    temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
    temp_shape += (4,)
    ptr = qimg.bits()
    ptr.setsize(qimg.byteCount())
    result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
    result = result[..., :3]

    return result


def cvimg_to_qtimg(cvimg):
    height, width, depth = cvimg.shape
    cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
    cvimg = QImage(cvimg.data, width, height, width * depth, QImage.Format_RGB888)

    return cvimg


class MyPaintAbleLabel(QLabel):
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0
    flag = False
    is_paint = False

    # 鼠标点击事件
    def mousePressEvent(self, event):
        self.flag = True
        self.x0 = event.x()
        self.y0 = event.y()

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        self.flag = False

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        if self.flag:
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()

    # 绘制事件
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_paint:
            rect = QRect(self.x0, self.y0, abs(self.x1 - self.x0), abs(self.y1 - self.y0))
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawRect(rect)


class WindowDemo(QWidget):

    def __init__(self):
        super(WindowDemo, self).__init__()
        # 设置窗口标题
        self.setWindowTitle('共性项目软件开发')
        self.desktop = QApplication.desktop()
        self.screen_width = self.desktop.width()
        self.screen_height = self.desktop.height()

        self.window_width = int(self.screen_width / 4 * 3)
        self.window_height = int(self.screen_height / 4 * 3)

        self.resize(self.window_width, self.window_height)

        # 初始变量
        self.Selected_Video_path = ""
        self.area = []
        self.is_selecting = False
        self.image = None
        self.map_image = None
        self.old_image_width = 0
        self.old_image_height = 0
        self.now_image_width = 0
        self.now_image_height = 0
        self.now_map_image_width = 0
        self.now_map_image_height = 0
        self.function_buttons = []
        self.target_track_parameter = "RemoteSensing"
        self.target_track_ans_save_path = ""
        self.track_json_path = "F:/Tracking/Scripts/tracking/tracking.json"
        self.track_result_txt_path = "F:/Tracking/Scripts/tracking/result.txt"
        self.track_result_jpg_path = "F:/Tracking/Scripts/tracking/result.jpg"
        self.frame_index = 0

        # 重复利用的静态数据
        self.static_buttons_number = 6
        self.function_buttons_number = 11

        self.Static_Buttons_Name = [
            '目标检测',
            '车辆目标检测',
            '道路提取',
            '目标识别',
            '视频跟踪',
            '定位'
        ]

        self.Function_Buttons_Name = [
            "加载图象",  # 0
            "模型参数",  # 1
            "目标检测",  # 2
            "结果保存",  # 3

            "加载图象",  # 4
            "模型参数",  # 5
            "车辆目标检测",  # 6
            "结果保存",  # 7

            "加载图象",  # 8
            "模型参数",  # 9
            "道路提取",  # 10
            "结果保存",  # 11

            "加载图象",  # 12
            "模型参数",  # 13
            "目标识别",  # 14
            "结果保存",  # 15

            "选则视频",  # 16
            "目标框选",  # 17
            "模型参数",  # 18
            "跟踪目标",  # 19
            "结果保存",  # 20

            "选则视频",  # 21
            "模型参数",  # 22
            "定位建图",  # 23
            "结果保存",  # 24
        ]

        self.Funtion_Buttons_Groups = [
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [8, 9, 10, 11],
            [12, 13, 14, 15],
            [16, 17, 18, 19, 20],
            [21, 22, 23, 24]
        ]

        self.Function_Button_image_paths = [
            "./icon/加载图象.png",
            "./icon/模型参数.png",
            "./icon/目标检测.png",
            "./icon/结果保存.png",
            "./icon/加载图象.png",
            "./icon/模型参数.png",
            "./icon/车辆目标检测.png",
            "./icon/结果保存.png",
            "./icon/加载图象.png",
            "./icon/模型参数.png",
            "./icon/道路提取.png",
            "./icon/结果保存.png",
            "./icon/加载图象.png",
            "./icon/模型参数.png",
            "./icon/目标识别.png",
            "./icon/结果保存.png",
            "./icon/选则视频.png",
            "./icon/目标框选.png",
            "./icon/模型参数.png",
            "./icon/跟踪目标.png",
            "./icon/结果保存.png",
            "./icon/选则视频.png",
            "./icon/模型参数.png",
            "./icon/定位建图.png",
            "./icon/结果保存.png",
        ]

        self.Radio_Button_Names_For_Target_Track = [
            "遥感光学目标跟踪",
            "对空无人机跟踪"
        ]
        self.Track_Type_Name = [
                "RemoteSensing",
                "UAV",
        ]

        self.save_ans_folder_path = "./ans"

        # 窗口要记录的状态数据
        self.select_button_id = 0
        self.target_track_parameter = ""

        # 窗口初始化
        self.Create_Static_Button_Dock_Layout()
        self.Create_Function_Button_Layout()
        self.Create_Work_Space_Layout()

        self.final_layout = QVBoxLayout()

        self.final_layout.addLayout(self.static_button_dock_layout)
        self.final_layout.addLayout(self.function_button_dock_layout)
        self.final_layout.addLayout(self.work_space_layout)
        self.final_layout.setStretchFactor(self.static_button_dock_layout, 1)
        self.final_layout.setStretchFactor(self.function_button_dock_layout, 1)
        self.final_layout.setStretchFactor(self.work_space_layout, 18)

        self.setLayout(self.final_layout)

    def Create_Static_Button_Dock_Layout(self):
        self.Create_Static_Button()

        self.static_button_dock_layout = QHBoxLayout()

        for i in range(self.static_buttons_number):
            self.static_button_dock_layout.addWidget(self.static_buttons[i])

    def Create_Function_Button_Layout(self):
        self.Create_Function_Button()
        self.function_button_dock_layout = QHBoxLayout()
        for i in range(len(self.function_buttons)):
            self.function_button_dock_layout.addWidget(self.function_buttons[i])
        self.Refresh_Function_Buttons_Visable()

    def Create_Work_Space_Layout(self):
        self.Create_Work_Space_Image_Label_Text_Edit()

        self.work_space_dock_right_up = self.Create_QDockWidget(self.map_image_label, "地图", 0)
        self.work_space_dock_right_down = self.Create_QDockWidget(self.textEdit, "工作区", 0)

        self.work_space_left_layout = QHBoxLayout()
        self.work_space_left_layout.addWidget(self.image_video_label)

        self.work_space_right_layout = QVBoxLayout()
        self.work_space_right_layout.addWidget(self.work_space_dock_right_up)
        self.work_space_right_layout.addWidget(self.work_space_dock_right_down)
        self.work_space_right_layout.setStretchFactor(self.work_space_dock_right_up, 5)
        self.work_space_right_layout.setStretchFactor(self.work_space_dock_right_down, 5)

        self.work_space_layout = QHBoxLayout()

        self.work_space_layout.addLayout(self.work_space_left_layout)
        self.work_space_layout.addLayout(self.work_space_right_layout)
        self.work_space_layout.setStretchFactor(self.work_space_left_layout, 8)
        self.work_space_layout.setStretchFactor(self.work_space_right_layout, 2)

    def Create_Static_Button(self):
        # 创建button
        self.static_buttons = []
        for i in range(self.static_buttons_number):
            self.static_buttons.append(QPushButton())
            self.static_buttons[-1].setProperty("name", "b{}".format(i))
            self.static_buttons[-1].setText(self.Static_Buttons_Name[i])

            self.static_buttons[-1].clicked.connect(self.Static_Button_Click)

    def Create_Function_Button(self):
        for i in range(len(self.Function_Buttons_Name)):
            self.function_buttons.append(QPushButton())
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(self.Function_Button_image_paths[i]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.function_buttons[-1].setIcon(icon)
            self.function_buttons[-1].setIconSize(QtCore.QSize(50, 80))
            self.function_buttons[-1].setText(self.Function_Buttons_Name[i])
            self.function_buttons[-1].clicked.connect(self.Function_Button_Click)

    def Create_Work_Space_Image_Label_Text_Edit(self):
        self.image_video_label = MyPaintAbleLabel()
        # self.image_video_label.setFixedSize(300, 300)
        self.image_video_label.setStyleSheet(
            "QLabel{background:white;}"
            "QLabel{color:rgb(300,300,300,120);font-size:10px;font-weight:bold;font-family:宋体;}"
        )

        self.map_image_label = QLabel()
        self.map_image_label.setStyleSheet(
            "QLabel{background:white;}"
            "QLabel{color:rgb(300,300,300,120);font-size:10px;font-weight:bold;font-family:宋体;}"
        )

        self.textEdit = QtWidgets.QTextEdit()
        # self.textEdit.setGeometry(QtCore.QRect(70, 90, 171, 391))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setReadOnly(True)  # 设置为只读，即可以在代码中向textEdit里面输入，但不能从界面上输入,没有这行代码即可以从界面输入

    def Create_QDockWidget(self, widget, name, type):
        dockwidget = QtWidgets.QDockWidget(name)  # 实例化dockwidget类
        dockwidget.setProperty('name', name)
        dockwidget.setWidget(widget)  # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        dockwidget.setObjectName(name)
        if type == 0:
            dockwidget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        if type == 1:
            dockwidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        return dockwidget

    def Static_Button_Click(self):
        sender = self.sender()
        id = 0
        for i in range(len(self.Static_Buttons_Name)):
            if self.Static_Buttons_Name[i] == sender.text():
                id = i
                break
        self.select_button_id = id
        self.Refresh_Function_Buttons_Visable()

    def Refresh_Function_Buttons_Visable(self):
        id = self.select_button_id
        for i in range(len(self.function_buttons)):
            self.function_buttons[i].setVisible(False)
        for i in range(len(self.Funtion_Buttons_Groups[id])):
            no = self.Funtion_Buttons_Groups[id][i]
            self.function_buttons[no].setVisible(True)

    def Function_Button_Click(self):
        sender = self.sender()
        id = 0
        for i in range(self.select_button_id):
            id+=len(self.Funtion_Buttons_Groups[i])
        for i in range(len(self.Funtion_Buttons_Groups[self.select_button_id])):
            if self.Function_Buttons_Name[id] == sender.text():
                break
            else:
                id+=1
        # print(id)

        # 每次切换功能都关闭框选
        self.Close_Select_Traget()

        # '目标检测',  #2
        # '车辆目标检测', #6
        # '道路提取',  #10
        # '目标识别',  #14
        # '视频跟踪',  #19
        # '定位'       #23

        # "加载图象",  # 0 4 8 12
        # "选则视频",  # 16 21
        # "目标框选",  # 17
        # "模型参数",  # 1 5 9 13 18 22
        # "结果保存",  # 3 7 11 15 20 24

        # '目标检测',  #2
        if id==2:
            pass
        # '车辆目标检测', #6
        if id==6:
            pass
        # '道路提取',  #10
        if id==10:
            pass
        # '目标识别',  #14
        if id==14:
            pass
        # '视频跟踪',  #19
        if id==19:
            # 读取设置的参数
            video_path = self.Selected_Video_path
            data_type = self.target_track_parameter
            self.Get_Select_Area()
            # print(self.area)
            x1, y1, w, h = self.area
            # 写入json，调用脚本
            track_19(video_path, data_type, x1, y1, w, h)
            # 显示tracking
            self.frame_index = 0
            self.Show_Tracking()
        # '定位'       #23
        if id==23:
            pass

        # 0 4 8 12 "加载图象",
        if id in [0, 4, 8, 12]:
            self.imageName, self.imageType = QFileDialog.getOpenFileName(self, "打开图片", "", "Image Files(*.jpg *.png)")
            if len(self.imageName) > 0:
                self.image = QtGui.QPixmap(self.imageName)
                self.old_image_width = self.image.width()
                self.old_image_height = self.image.height()
                self.now_image_width = self.image_video_label.width()
                self.now_image_height = self.image_video_label.height()
                self.image = self.image.scaled(self.now_image_width, self.now_image_height)
                self.image_video_label.setPixmap(self.image)
        # 16, 21 "选则视频",
        if id in [16, 21]:
            if id==16:
                self.Selected_Video_path = QFileDialog.getExistingDirectory(self, "选择视频", "F:/ODER_dataset/Track")
                if len(self.Selected_Video_path) > 0:
                    self.Play_First_Frame()
        # "目标框选",  # 17
        if id in [17]:
            self.Select_Target()
        # "模型参数",  # 1 5 9 13 18 22
        if id in [1, 5, 9, 13, 18, 22]:
            if id==18:
                self.Select_Model_Parameter_For_Target_Track()
        # "结果保存",  # 3 7 11 15 20 24
        if id in [3, 7, 11, 15, 20, 24]:
            if id == 20:
                self.Select_Save_Path_For_Target_Track()

    def Play_First_Frame(self):
        self.imageName = self.Selected_Video_path+"/img/0001.jpg"
        self.image = QtGui.QPixmap(self.imageName)
        self.old_image_width = self.image.width()
        self.old_image_height = self.image.height()
        self.now_image_width = self.image_video_label.width()
        self.now_image_height = self.image_video_label.height()
        self.image = self.image.scaled(self.now_image_width, self.now_image_height)
        self.image_video_label.setPixmap(self.image)

    def Create_Ans_Folder(self):
        if os.path.exists(self.save_ans_folder_path) == False:
            os.mkdir(self.save_ans_folder_path)

    def Select_Target(self):
        self.image_video_label.is_paint = True

    def Close_Select_Traget(self):
        self.image_video_label.is_paint = False

    def Get_Select_Area(self):
        samll_number = 0.0000001
        if self.now_image_width < samll_number or self.now_image_height < samll_number:
            self.area = [0, 0, 0, 0]
        else:
            x0, y0, x1, y1 = self.image_video_label.x0, self.image_video_label.y0, self.image_video_label.x1, self.image_video_label.y1
            # self.area = [x0, y0, x1, y1]
            x0, y0, x1, y1 = x0 / self.now_image_width, y0 / self.now_image_height, x1 / self.now_image_width, y1 / self.now_image_height
            x0, y0, x1, y1 = x0 * self.old_image_width, y0 * self.old_image_height, x1 * self.old_image_width, y1 * self.old_image_height
            # x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
            w = x1 - x0
            h = y1 - y0
            # self.area = [x0, y0, x1, y1]
            self.area = [x0, y0, w, h]

    def Print_To_Text_Edit(self, info=''):
        # old_info = self.textEdit.toPlainText()
        # if len(old_info) > 0:
        #     old_info = old_info + "\n"
        # info = old_info + "hello"
        self.textEdit.setPlainText(info)

    def Refresh_Map(self):
        self.map_image = QtGui.QPixmap("../test1.png")
        self.now_map_image_width = self.map_image_label.width()
        self.now_map_image_height = self.map_image_label.height()
        self.map_image = self.map_image.scaled(self.now_map_image_width, self.now_map_image_height)
        self.map_image_label.setPixmap(self.map_image)

    def Select_Model_Parameter_For_Target_Track(self):
        model_parameter_radio_button_box_dialog = QDialog()
        dialog_layout = QVBoxLayout()
        radio_buttons = []
        n = len(self.Radio_Button_Names_For_Target_Track)
        target_track_radio_button_group = QButtonGroup()
        for i in range(n):
            radio_buttons.append(QRadioButton(self.Radio_Button_Names_For_Target_Track[i]))
            dialog_layout.addWidget(radio_buttons[-1])
            target_track_radio_button_group.addButton(radio_buttons[-1])
            radio_buttons[-1].clicked.connect(self.Toggle_Event_Of_Target_Track_Radio_Button)

        radio_buttons[0].click()
        model_parameter_radio_button_box_dialog.setLayout(dialog_layout)
        model_parameter_radio_button_box_dialog.resize(300, 100)
        model_parameter_radio_button_box_dialog.setWindowTitle("模型参数选择")
        # 设置窗口的属性为ApplicationModal模态，用户只有关闭弹窗后，才能关闭主界面
        model_parameter_radio_button_box_dialog.setWindowModality(Qt.ApplicationModal)
        model_parameter_radio_button_box_dialog.exec_()

    def Toggle_Event_Of_Target_Track_Radio_Button(self):
        sender = self.sender()
        id = 0
        for i in range(len(self.Radio_Button_Names_For_Target_Track)):
            if self.Radio_Button_Names_For_Target_Track[i] == sender.text():
                id = i
                break
        self.target_track_parameter = self.Track_Type_Name[id]
        # print(self.target_track_parameter)

    def Select_Save_Path_For_Target_Track(self):
        self.target_track_ans_save_path = QFileDialog.getExistingDirectory(self, "跟踪结果保存位置", "./ans")
        self.target_track_ans_save_path = self.target_track_ans_save_path+"/result.txt"
        try:
            # print(self.track_result_txt_path)
            # print(self.target_track_ans_save_path)
            copyfile(self.track_result_txt_path, self.target_track_ans_save_path)
            QMessageBox.about(self, "保存结果", "保存已完成！ {}".format(self.target_track_ans_save_path))
        except:
            QMessageBox.about(self, "保存结果", "保存失败！")

    def Show_Tracking(self):
        self.timer_for_tracking = QTimer()
        self.timer_for_tracking.setInterval(200)
        self.timer_for_tracking.timeout.connect(self.Tracking_Timer_TimerOut)
        self.timer_for_tracking.start()

    def Tracking_Timer_TimerOut(self):
        # 首先检测是否已经跟踪完了
        try:
            json_file = open(self.track_json_path, 'r', encoding='utf-8')
            json_data = json.load(json_file)
            json_file.close()
            # print(json_data["OutputParameter"]["ProgramStatus"][0]["value"])
            frame_index = json_data['OutputParameter']['OutputResult'][1]['value']
            self.frame_index = frame_index
            x1 = json_data['OutputParameter']['OutputResult'][0]['x1']
            y1 = json_data['OutputParameter']['OutputResult'][0]['y1']
            w = json_data['OutputParameter']['OutputResult'][0]['w']
            h = json_data['OutputParameter']['OutputResult'][0]['h']
            info = "frame: {}\nx1 {}\ny1 {}\nw {}\nh {}\n".format(frame_index, x1, y1, w, h)
            self.Print_To_Text_Edit(info)
            if json_data["OutputParameter"]["ProgramStatus"][0]["value"] ==1:
                self.timer_for_tracking.stop()
        except:
            pass
        # 为确保能显示到最后一帧，每次进来都读取一下
        if self.frame_index > 0:
            try:
                self.imageName = self.track_result_jpg_path
                self.image = QtGui.QPixmap(self.imageName)
                self.old_image_width = self.image.width()
                self.old_image_height = self.image.height()
                self.now_image_width = self.image_video_label.width()
                self.now_image_height = self.image_video_label.height()
                self.image = self.image.scaled(self.now_image_width, self.now_image_height)
                self.image_video_label.setPixmap(self.image)
            except:
                # 正常情况下是产生读写竞争错误
                pass
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = WindowDemo()
    win.show()
    sys.exit(app.exec_())