#Author: Stan Yin
#GitHub Name: SomeB1oody
#This project is based on CC 4.0 BY, please mention my name if you use it.
#This project requires opencv, numpy, re and wxWidgets.
import cv2
import numpy as np
import wx
import re

global alpha, beta, gamma
alpha = 100
beta = 100
gamma = 100
global img_without_crop, img, selected_color
selected_color = None

def is_valid_windows_filename(filename: str) -> bool:
    # 检查是否包含非法字符
    invalid_chars = r'[<>:"/\\|?*]'
    if re.search(invalid_chars, filename):
        return False
    # 检查是否是保留名称
    reserved_names = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    if filename.upper() in reserved_names:
        return False
    # 检查是否以空格或点结尾
    if filename.endswith(' ') or filename.endswith('.'):
        return False
    # 检查文件名长度
    if len(filename) > 255:
        return False
    # 如果所有检查都通过，返回True
    return True

def mixer(input_image, _alpha_, _beta_, _gamma_, window_name, flag):
    look_up_table = np.zeros((256,), dtype=np.uint8)
    for index in range(256):
        value = np.clip((index / 255.0) ** (gamma / 100.0) * 255.0, 0, 255)
        look_up_table[index] = np.uint8(value)
    arg1 = cv2.LUT(input_image, look_up_table)
    arg2 = cv2.convertScaleAbs(arg1, alpha=_alpha_, beta=_beta_)
    if flag: cv2.imshow(window_name, arg2)
    else: return arg2

def load_image(path):
    global img
    if not path:
        wx.MessageBox("Please enter image path", "Error", wx.OK | wx.ICON_ERROR)
        return
    img = cv2.imread(path)
    if img is None:
        wx.MessageBox('Could not load the image', 'Error', wx.OK | wx.ICON_ERROR)
        return

class ImageConverter(wx.Frame):
    def __init__(self, *args, **kw):
        super(ImageConverter, self).__init__(*args, **kw)

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        # 输入路径
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.file_button = wx.Button(panel, label="Select image")
        self.Bind(wx.EVT_BUTTON, self.on_select_file, self.file_button)
        self.hbox.Add(self.file_button,flag=wx.ALL, border=5)
        self.input_path_text = wx.StaticText(panel, label="Click \"Select image\" first")
        self.hbox.Add(self.input_path_text, flag=wx.ALL, border=5)
        vbox.Add(self.hbox, flag=wx.EXPAND)
        #输入图片输出名称
        vbox.Add(wx.StaticText(panel, label="Output image name:(no file suffix)"), flag=wx.ALL, border=5)
        self.output_name = wx.TextCtrl(panel)
        vbox.Add(self.output_name, flag=wx.EXPAND | wx.ALL, border=5)
        # 输出路径
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.folder_button = wx.Button(panel, label="Select output folder")
        self.Bind(wx.EVT_BUTTON, self.on_select_folder, self.folder_button)
        self.hbox2.Add(self.folder_button, flag=wx.ALL, border=5)
        self.output_path_text = wx.StaticText(panel, label="Click \"Select output folder\" first")
        self.hbox2.Add(self.output_path_text, flag=wx.ALL, border=5)
        vbox.Add(self.hbox2, flag=wx.EXPAND)

        # 输出格式单选框
        self.output_format = wx.RadioBox(
            panel, label="Choose output format:", choices=[
                '.jpg', '.jpeg', '.png', '.tiff',
                '.tif', '.bmp', '.ppm', '.pgm', '.pbm', '.webp'
            ]
        )
        vbox.Add(self.output_format, flag=wx.ALL, border=5)
        #亮度与对比度调整
        brightness_button = wx.Button(panel, label="Contrast and Brightness Adjustment")
        vbox.Add(wx.StaticText(panel,
        label="Close the window that pops out to save change in these button down HERE:"), flag=wx.ALL, border=5)
        brightness_button.Bind(wx.EVT_BUTTON, self.brightness_and_contrast_adjustment)
        vbox.Add(brightness_button, flag=wx.ALL, border=5)
        #伽马纠正
        gamma_button = wx.Button(panel, label="Gamma Correction")
        gamma_button.Bind(wx.EVT_BUTTON, self._gamma_correction_)
        vbox.Add(gamma_button, flag=wx.ALL, border=5)
        # 色彩格式
        vbox.Add(wx.StaticText(panel, label="Please choose a color format"), flag=wx.ALL, border=5)
        color_format_list = [
            'Same', 'BGR(555)', 'BGR(565)','RGB', 'GRAY', 'HSV', 'HSV(Full)', 'HLS', 'HLS(Full)','YUV','YUV(4:2:0)',
            'YUV(4:2:2)','LAB'
        ]
        lb = wx.ListBox(panel, choices=color_format_list, style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.color_format_lb, lb)
        vbox.Add(lb, flag=wx.ALL, border=5)
        # 转换按钮
        convert_button = wx.Button(panel, label="Convert")
        convert_button.Bind(wx.EVT_BUTTON, self.on_convert)
        vbox.Add(convert_button, flag=wx.ALL, border=5)

        # 设置面板的布局管理器
        panel.SetSizer(vbox)

        # 触发布局更新
        panel.Layout()

    def on_select_file(self, event):
        with wx.FileDialog(None, "Select a image", wildcard="所有文件 (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.input_path_text.SetLabel(f"{dialog.GetPath()}")
                self.selected_file = dialog.GetPath()

    def on_select_folder(self, event):
        with wx.DirDialog(None, "Select a folder for output", "",
                          style=wx.DD_DEFAULT_STYLE) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.output_path_text.SetLabel(f"{dialog.GetPath()}")
                self.selected_folder = dialog.GetPath()

    def brightness_and_contrast_adjustment(self, event):
        global gamma, alpha, beta, img
        load_image(self.selected_file)
        def alpha_track_bar(alpha_):
            global alpha, img
            alpha = alpha_
            mixer(img, alpha / 100.0, beta - 100, gamma / 100.0,
            "Brightness and Contrast", True)

        def beta_track_bar(beta_):
            global beta, img
            beta = beta_
            mixer(img, alpha / 100.0, beta - 100, gamma / 100.0,
            "Brightness and Contrast", True)

        cv2.namedWindow("Brightness and Contrast")
        cv2.createTrackbar("Contrast", "Brightness and Contrast",
        alpha, 200, alpha_track_bar)
        cv2.createTrackbar("Brightness", "Brightness and Contrast",
        beta, 200, beta_track_bar)

    def _gamma_correction_(self, event):
        global gamma, img
        load_image(self.selected_file)
        def gamma_track_bar(_gamma):
            global alpha, beta, gamma
            gamma = _gamma
            mixer(img, alpha / 100.0, beta - 100, gamma / 100.0,
            "Gamma Correction")
        cv2.namedWindow("Gamma Correction")
        cv2.createTrackbar("Gamma", "Gamma Correction", gamma, 200, gamma_track_bar)

    def color_format_lb(self, event):
        global selected_color
        selected_color = event.GetEventObject()
        if selected_color == 'Same':
            selected_color = None

    def on_convert(self, event):
        global img, selected_color, alpha, beta, gamma
        #获取用户的选择
        load_image(self.selected_file)
        save_path = self.selected_folder
        save_name = self.output_name.GetValue()
        if not save_path:
            wx.MessageBox('Please select output path','Error', wx.OK | wx.ICON_ERROR)
            return
        if not save_name:
            wx.MessageBox('Please enter output name','Error', wx.OK | wx.ICON_ERROR)
            return
        else:
            if not is_valid_windows_filename(save_name):
                wx.MessageBox('Output name invalid, please try again','Error', wx.OK | wx.ICON_ERROR)
                return

        selected_format = self.output_format.GetStringSelection()
        #Brightness Contrast Gamma
        mixed_img = mixer(img, alpha / 100.0, beta - 100, gamma / 100.0, "", False)
        #转换色彩格式
        color_format_dict = {
            'BGR(555)': cv2.COLOR_BGR2BGR555,
            'BGR(565)': cv2.COLOR_BGR2BGR565,
            'RGB': cv2.COLOR_BGR2RGB,
            'GRAY': cv2.COLOR_BGR2GRAY,
            'HSV': cv2.COLOR_BGR2HSV,
            'HSV(Full)': cv2.COLOR_BGR2HSV_FULL,
            'HLS': cv2.COLOR_BGR2HLS,
            'HLS(Full)': cv2.COLOR_BGR2HLS_FULL,
            'YUV': cv2.COLOR_BGR2YUV,
            'YUV(4:2:0)': cv2.COLOR_BGR2YUV_I420,
            'YUV(4:2:2)': cv2.COLOR_BGR2YUV_Y422,
            'LAB': cv2.COLOR_BGR2LAB,
        }
        if selected_color is not None:
            output_img = cv2.cvtColor(mixed_img, color_format_dict[selected_color])
        else: output_img = mixed_img
        # 确定输出路径
        output_ = f"{save_path}/{save_name}{selected_format}"

        # 保存输出图片
        try:
            cv2.imwrite(output_, output_img)
            wx.MessageBox(f'Image saved as {output_}', 'Success',
            wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)


if __name__ == "__main__":
    app = wx.App()
    frame = ImageConverter(None)
    frame.SetTitle('Image Mixer')
    frame.SetSize((800, 600))
    frame.Show()
    app.MainLoop()
