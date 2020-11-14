import tkinter as tk
import tkinter.messagebox
from PIL import Image, ImageTk
import cv2

movie_path = "1.mp4"
video_play_interval = 100

def button_image_click():
    global label_image, image, continue_play
    continue_play=False
    # image = tk.PhotoImage(Image.open('1.jpg'))
    image = tk.PhotoImage(file='pic.gif')
    # image = ImageTk.PhotoImage(Image.fromarray(cv2.imread("1.jpg")))
    # success, image = cv2.VideoCapture("1.mp4").read()
    #
    # image = ImageTk.PhotoImage(Image.fromarray(image))
    label_image.configure(image=image)

def button_video_read_click():
    global window, video, video_cnt
    video = cv2.VideoCapture("1.mp4")
    video_cnt = 0
    if video.isOpened():
        tkinter.messagebox.showinfo(title='读取成功', message='读取成功！')  # 提示信息对话窗
    else:
        tkinter.messagebox.showinfo(title='读取失败', message='读取失败！')  # 提示信息对话窗

def video_play():
    global label_image, image, video, video_cnt, continue_play, video_play_interval
    if continue_play==False:
        return
    success, frame = video.read()
    if success==True:
        image = ImageTk.PhotoImage(Image.fromarray(frame))
        label_image.configure(image=image)
        video_cnt += 1
    else:
        continue_play = False
    if continue_play:
        window.after(video_play_interval, video_play)

def button_video_play_click():
    global label_image, video, video_cnt, continue_play
    if video!=None and video.isOpened():
        continue_play = True
        video_play()
    else:
        tkinter.messagebox.showinfo(title='播放失败', message='请先读取视频！')  # 提示信息对话窗

def button_video_next_frame_click():
    global window, image, video, video_cnt, video_play_interval, continue_play
    if video!=None and video.isOpened():
        continue_play = False
        success, frame = video.read()
        if success:
            image = ImageTk.PhotoImage(Image.fromarray(frame))
            label_image.configure(image=image)
            video_cnt += 1
        else:
            continue_play = False
            tk.messagebox.showinfo(title='播放已结束', message='播放已结束！')  # 提示信息对话窗
    else:
        tkinter.messagebox.showinfo(title='播放失败', message='请先读取视频！')  # 提示信息对话窗

def create_button():
    global window
    button_image = tk.Button(window, text="image", command=button_image_click)
    button_video_read = tk.Button(window, text="read video", command=button_video_read_click)
    button_video_play = tk.Button(window, text="video play", command=button_video_play_click)
    button_video_next_frame = tk.Button(window, text="video next frame", command=button_video_next_frame_click)

    button_image.pack()
    button_video_read.pack()
    button_video_play.pack()
    button_video_next_frame.pack()

def create_label():
    global window, label_image, image
    image = tk.PhotoImage(file='pic2.gif')
    label_image = tk.Label(window, image=image)
    label_image.pack()

def init_variable():
    global video
    video = None

def main():
    global window, image, label_image
    window = tk.Tk()
    window.title("play")
    # window.iconbitmap("1.jpg")
    windows_width = int(window.winfo_screenwidth() / 2)
    windows_height = int(window.winfo_screenheight() / 2)
    window.resizable(True, True)
    window.geometry("{}x{}".format(windows_width, windows_height))

    create_button()
    create_label()
    init_variable()

    window.mainloop()

if __name__ == '__main__':
    main()