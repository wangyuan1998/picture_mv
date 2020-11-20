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
from PyQt5.QtCore import QRect, Qt
import datetime

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

    #鼠标点击事件
    def mousePressEvent(self,event):
        self.flag = True
        self.x0 = event.x()
        self.y0 = event.y()

    #鼠标释放事件
    def mouseReleaseEvent(self,event):
        self.flag = False

    #鼠标移动事件
    def mouseMoveEvent(self,event):
        if self.flag:
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()

    #绘制事件
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_paint:
            rect =QRect(self.x0, self.y0, abs(self.x1-self.x0), abs(self.y1-self.y0))
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red,2,Qt.SolidLine))
            painter.drawRect(rect)


class WindowDemo(QWidget):

    def __init__(self):
        super(WindowDemo, self).__init__()
        #设置窗口标题
        self.setWindowTitle('共性项目软件开发')
        self.desktop = QApplication.desktop()
        self.screen_width = self.desktop.width()
        self.screen_height = self.desktop.height()

        self.window_width = int(self.screen_width/4*3)
        self.window_height = int(self.screen_height/4*3)

        self.resize(self.window_width, self.window_height)

        # 初始变量
        self.video = None
        self.video_cnt = 0
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
            "目标检测",         #0
            "车辆目标检测",     #1
            "道路提取",         #2
            "目标识别",         #3
            "跟踪目标",         #4
            "定位建图",         #5

            "加载图象",         #6
            "选则视频",         #7
            "模型参数",         #8
            "结果保存",         #9
            "目标框选",         #10
        ]

        self.Static_to_Function = [
            [6, 8, 0, 9],
            [6, 8, 1, 9],
            [6, 8, 2, 9],
            [6, 8, 3, 9],

            [7, 10, 8, 4, 9],
            [7, 8, 5, 9],
        ]

        self.Function_Button_image_paths = [
            "./icon/目标检测.png",
            "./icon/车辆目标检测.png",
            "./icon/道路提取.png",
            "./icon/目标识别.png",
            "./icon/跟踪目标.png",
            "./icon/定位建图.png",

            "./icon/加载图象.png",
            "./icon/选则视频.png",
            "./icon/模型参数.png",
            "./icon/结果保存.png",
            "./icon/目标框选.png",
        ]

        self.Radio_Button_Names_For_Target_Track = [
                "遥感光学目标跟踪",
                "对空无人机跟踪"
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

        for i in range(self.function_buttons_number):
            self.function_button_dock_layout.addWidget(self.function_buttons[i])

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
        # 创建功能按钮
        self.function_buttons = []
        for i in range(self.function_buttons_number):
            self.function_buttons.append(QPushButton())
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(self.Function_Button_image_paths[i]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.function_buttons[-1].setIcon(icon)
            self.function_buttons[-1].setIconSize(QtCore.QSize(50, 80))
            self.function_buttons[-1].setText(self.Function_Buttons_Name[i])
            self.function_buttons[-1].clicked.connect(self.Function_Button_Click)
        # 刷新到第一个状态
        self.Refresh_Function_Button(0)

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
        if type==0:
            dockwidget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        if type==1:
            dockwidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        return dockwidget

    def Static_Button_Click(self):
        sender = self.sender()
        id = 0
        for i in range(len(self.Static_Buttons_Name)):
            if self.Static_Buttons_Name[i]==sender.text():
                id = i
                break
        self.select_button_id = id
        self.Refresh_Function_Button(id)

    def Refresh_Function_Button(self, id):
        select_funcs = self.Static_to_Function[id]
        for i in range(self.function_buttons_number):
            self.function_buttons[i].setVisible(False)
        for i in range(len(select_funcs)):
            self.function_buttons[select_funcs[i]].setVisible(True)

    def Function_Button_Click(self):
        sender = self.sender()
        id = 0
        for i in range(len(self.Function_Buttons_Name)):
            if self.Function_Buttons_Name[i] == sender.text():
                id = i
                break
        # 0 "目标检测",
        # 1 "车辆目标检测",
        # 2 "道路提取",
        # 3 "目标识别",
        # 4 "跟踪目标",
        if id == 4:
            # 收集数据，生成json文件，数据补全，messagebox提示

            # 运行程序，读取图片并显示
            pass
        
        # 5 "定位建图",

        # 6 "加载图象",
        if id == 6:
            self.imageName, self.imageType = QFileDialog.getOpenFileName(self, "打开图片", "", "Image Files(*.jpg *.png)")
            if len(self.imageName)>0:
                self.image = QtGui.QPixmap(self.imageName)
                self.old_image_width = self.image.width()
                self.old_image_height = self.image.height()
                self.now_image_width = self.image_video_label.width()
                self.now_image_height = self.image_video_label.height()
                self.image = self.image.scaled(self.now_image_width, self.now_image_height)
                self.image_video_label.setPixmap(self.image)
        # 7 "选则视频",
        if id == 7:
            self.VideoName, self.VideoType = QFileDialog.getOpenFileName(self, "打开图片", "", "Video Files(*.mp4)")
            if len(self.VideoName)>0:
                self.video = cv2.VideoCapture(self.VideoName)
                self.video_cnt = 0
                self.Play_A_Frame()
        # 8 "模型参数",
        if id==8:
            # self.Print_To_Text_Edit()
            # self.Refresh_Map()
            self.Select_Model_Parameter()
        # 9 "结果保存",
        if id==9:
            self.Save_Ans()
        # 10 "目标框选",
        if id==10:
            self.Select_Target()

    def Play_A_Frame(self):
        success, frame = self.video.read()
        if success:
            self.video_cnt+=1
            # <class 'PyQt5.QtGui.QImage'> -> <class 'PyQt5.QtGui.QPixmap'>
            self.image = QPixmap.fromImage(cvimg_to_qtimg(frame))
            self.old_image_width = self.image.width()
            self.old_image_height = self.image.height()
            self.now_image_width = self.image_video_label.width()
            self.now_image_height = self.image_video_label.height()
            self.image = self.image.scaled(self.now_image_width, self.now_image_height)
            self.image_video_label.setPixmap(self.image)

    def Create_Ans_Folder(self):
        if os.path.exists(self.save_ans_folder_path)==False:
            os.mkdir(self.save_ans_folder_path)

    def Save_Ans(self):
        self.Create_Ans_Folder()
        self.ans = [
            "ship 1.0 360.0952453613281 322.86016845703125 1029.7333984375 574.6747436523438 968.770263671875 736.7910766601562 299.1321105957031 484.97650146484375",
            "car 0.9998446702957153 433.01072692871094 257.82505798339844 492.43284606933594 282.04649353027344 479.03627014160156 314.9121551513672 419.61415100097656 290.6907196044922",
        ]
        def f(c):
            s = {'-', ':', ' ', '.'}
            if c in s:
                return '_'
            return c

        time_now = datetime.datetime.now()
        time_now = ''.join(list(map(f, str(time_now))))
        ans_name = self.Static_Buttons_Name[self.select_button_id]+time_now+".txt"
        ans_path = self.save_ans_folder_path+"/"+ans_name
        ans_file = open(ans_path, 'w')
        for i in range(len(self.ans)):
            ans_file.write(self.ans[i]+"\n")
        ans_file.close()
        QMessageBox.about(self, "保存结果", "保存已完成！ {}".format(ans_path))

    def Select_Target(self):
        self.image_video_label.is_paint = ~(self.image_video_label.is_paint)

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
            w = x1-x0
            h = y1-y0
            # self.area = [x0, y0, x1, y1]
            self.area = [x0, y0, w, h]

    def Print_To_Text_Edit(self, info=''):
        old_info = self.textEdit.toPlainText()
        if len(old_info) > 0:
            old_info = old_info+"\n"
        info = old_info+"hello"
        self.textEdit.setPlainText(info)

    def Refresh_Map(self):
        self.map_image = QtGui.QPixmap("../test1.png")
        self.now_map_image_width = self.map_image_label.width()
        self.now_map_image_height = self.map_image_label.height()
        self.map_image = self.map_image.scaled(self.now_map_image_width, self.now_map_image_height)
        self.map_image_label.setPixmap(self.map_image)

    def Select_Model_Parameter(self):
        # 4 "跟踪目标",
        if self.select_button_id==4:
            model_parameter_radio_button_box_dialog = QDialog()
            dialog_layout = QVBoxLayout()
            radio_buttons = []
            n = len(self.Radio_Button_Names_For_Target_Track)
            target_track_radio_button_group = QButtonGroup()
            for i in range(n):
                radio_buttons.append(QRadioButton(self.Radio_Button_Names_For_Target_Track[i]))
                dialog_layout.addWidget(radio_buttons[-1])
                target_track_radio_button_group.addButton(radio_buttons[-1])
                # radio_buttons[-1].toggled.connect(self.Toggle_Event_Of_Target_Track_Radio_Button)
                radio_buttons[-1].clicked.connect(self.Toggle_Event_Of_Target_Track_Radio_Button)

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
            if self.Radio_Button_Names_For_Target_Track[i]==sender.text():
                id = i
                break
        self.target_track_parameter = self.Radio_Button_Names_For_Target_Track[id]
        # print(self.target_track_parameter)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = WindowDemo()
    win.show()
    sys.exit(app.exec_())


