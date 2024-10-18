#Author: Stan Yin
#GitHub Name: SomeB1oody
#This project is based on CC 4.0 BY, please mention my name if you use it.
#This project requires opencv, re, numpy and wxWidgets.
import wx
import cv2
import numpy as np
import re

translate_dict = {
    #BayerBG
    'BayerBG to BGR': cv2.COLOR_BayerBG2BGR,
    'BayerBG to BGR(VNG)': cv2.COLOR_BayerBG2BGR_VNG,
    'BayerBG to BGR(EA)': cv2.COLOR_BayerBG2BGR_EA,
    'BayerBG to RGB': cv2.COLOR_BayerBG2RGB,
    'BayerBG to RGB(VNG)': cv2.COLOR_BayerBG2RGB_VNG,
    'BayerBG to RGB(EA)': cv2.COLOR_BayerBG2RGB_EA,
    'BayerBG to BGRA': cv2.COLOR_BayerBG2BGRA,
    'BayerBG to RGBA': cv2.COLOR_BayerBG2RGBA,
    'BayerBG to GRAY': cv2.COLOR_BayerBG2GRAY,
    #BayerGB
    'BayerGB to BGR': cv2.COLOR_BayerGB2BGR,
    'BayerGB to BGR(VNG)': cv2.COLOR_BayerGB2BGR_VNG,
    'BayerGB to BGR(EA)': cv2.COLOR_BayerGB2BGR_EA,
    'BayerGB to RGB': cv2.COLOR_BayerGB2RGB,
    'BayerGB to RGB(VNG)': cv2.COLOR_BayerGB2RGB_VNG,
    'BayerGB to RGB(EA)': cv2.COLOR_BayerGB2RGB_EA,
    'BayerGB to BGRA': cv2.COLOR_BayerGB2BGRA,
    'BayerGB to RGBA': cv2.COLOR_BayerGB2RGBA,
    'BayerGB to GRAY': cv2.COLOR_BayerGB2GRAY,
    #BayerGR
    'BayerGR to BGR': cv2.COLOR_BayerGR2BGR,
    'BayerGR to BGR(VNG)': cv2.COLOR_BayerGR2BGR_VNG,
    'BayerGR to BGR(EA)': cv2.COLOR_BayerGR2BGR_EA,
    'BayerGR to RGB': cv2.COLOR_BayerGR2RGB,
    'BayerGR to RGB(VNG)': cv2.COLOR_BayerGR2RGB_VNG,
    'BayerGR to RGB(EA)': cv2.COLOR_BayerGR2RGB_EA,
    'BayerGR to BGRA': cv2.COLOR_BayerGR2BGRA,
    'BayerGR to RGBA': cv2.COLOR_BayerGR2RGBA,
    'BayerGR to GRAY': cv2.COLOR_BayerGR2GRAY,
    #BayerRG
    'BayerRG to BGR': cv2.COLOR_BayerRG2BGR,
    'BayerRG to BGR(VNG)': cv2.COLOR_BayerRG2BGR_VNG,
    'BayerRG to BGR(EA)': cv2.COLOR_BayerRG2BGR_EA,
    'BayerRG to RGB': cv2.COLOR_BayerRG2RGB,
    'BayerRG to RGB(VNG)': cv2.COLOR_BayerRG2RGB_VNG,
    'BayerRG to RGB(EA)': cv2.COLOR_BayerRG2RGB_EA,
    'BayerRG to BGRA': cv2.COLOR_BayerRG2BGRA,
    'BayerRG to RGBA': cv2.COLOR_BayerRG2RGBA,
    'BayerRG to GRAY': cv2.COLOR_BayerRG2GRAY,
    #BayerBGGR
    'BayerBGGR to BGR': cv2.COLOR_BayerBGGR2BGR,
    'BayerBGGR to BGR(VNG)': cv2.COLOR_BayerBGGR2BGR_VNG,
    'BayerBGGR to BGR(EA)': cv2.COLOR_BayerBGGR2BGR_EA,
    'BayerBGGR to RGB': cv2.COLOR_BayerBGGR2RGB,
    'BayerBGGR to RGB(VNG)': cv2.COLOR_BayerBGGR2RGB_VNG,
    'BayerBGGR to RGB(EA)': cv2.COLOR_BayerBGGR2RGB_EA,
    'BayerBGGR to BGRA': cv2.COLOR_BayerBGGR2BGRA,
    'BayerBGGR to RGBA': cv2.COLOR_BayerBGGR2RGBA,
    'BayerBGGR to GRAY': cv2.COLOR_BayerBGGR2GRAY,
}

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

def validate_and_convert_size(width_str: str, height_str: str):
    if width_str.isdigit() and height_str.isdigit():
        width = int(width_str)
        height = int(height_str)
        return width, height, True

    return None, None, False

class DeBayer(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        panel = wx.Panel(self)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # 输入路径
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.file_button = wx.Button(panel, label="Select image")
        self.Bind(wx.EVT_BUTTON, self.on_select_file, self.file_button)
        self.hbox.Add(self.file_button,flag=wx.ALL, border=5)
        self.input_path_text = wx.StaticText(panel, label="Click \"Select image\" first")
        self.hbox.Add(self.input_path_text, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox, flag=wx.EXPAND)
        # 输入图片宽
        self.vbox.Add(wx.StaticText(panel, label="Please enter the image width："), flag=wx.ALL, border=5)
        self.img_width = wx.TextCtrl(panel)
        self.vbox.Add(self.img_width, flag=wx.ALL, border=5)
        # 输入图片高
        self.vbox.Add(wx.StaticText(panel, label="Please enter the image height："), flag=wx.ALL, border=5)
        self.img_height = wx.TextCtrl(panel)
        self.vbox.Add(self.img_height, flag=wx.ALL, border=5)
        # 输入图片位深度
        self.bit_depth = wx.RadioBox(panel, label="Choose bit depth:", choices=['8 bit', '16 bit'])
        self.vbox.Add(self.bit_depth, flag=wx.ALL, border=5)
        # 输入图片输出名称
        self.vbox.Add(wx.StaticText(panel, label="Output image name:(no file suffix)"), flag=wx.ALL, border=5)
        self.output_name = wx.TextCtrl(panel)
        self.vbox.Add(self.output_name, flag=wx.EXPAND | wx.ALL, border=5)
        # 输出路径
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.folder_button = wx.Button(panel, label="Select output folder")
        self.Bind(wx.EVT_BUTTON, self.on_select_folder, self.folder_button)
        self.hbox2.Add(self.folder_button, flag=wx.ALL, border=5)
        self.output_path_text = wx.StaticText(panel, label="Click \"Select output folder\" first")
        self.hbox2.Add(self.output_path_text, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox2, flag=wx.EXPAND)
        # 输出格式单选框
        self.output_format = wx.RadioBox(
            panel, label="Choose output format:", choices=[
                '.jpg', '.jpeg', '.png', '.tiff',
                '.tif', '.bmp', '.ppm', '.pgm', '.pbm', '.webp'
            ]
        )
        self.vbox.Add(self.output_format, flag=wx.ALL, border=5)
        # 输入拜耳阵列类型单选框
        self.input_bayer_format = wx.RadioBox(panel, label="Choose input bayer format:", choices=[
            'BayerBG', 'BayerGB', 'BayerGR', 'BayerRG', 'BayerBGGR'
        ])
        self.vbox.Add(self.input_bayer_format, flag=wx.ALL, border=5)
        # 输出颜色格式选择框
        self.output_bayer_format = wx.RadioBox(panel, label="Choose output color format:", choices=[
            'BGR', 'BGR(EA)', 'BGR (VNG)', 'BGRA', 'RGB', 'RGB(EA)', 'RGB(VNG)', 'RGBA', 'GRAY'
        ])
        self.vbox.Add(self.output_bayer_format, flag=wx.ALL, border=5)
        # Tip
        self.vbox.Add(wx.StaticText(panel, label=
        "If you need other color formats, using ColorMaster.py is a good choice."), flag=wx.ALL, border=5)
        # 转换按钮
        self.convert_button = wx.Button(panel, label="Convert")
        self.convert_button.Bind(wx.EVT_BUTTON, self.on_convert)
        self.vbox.Add(self.convert_button, flag=wx.ALL, border=5)

        # 设置面板的布局管理器
        panel.SetSizer(self.vbox)
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

    def on_convert(self, event):
        # 获取用户选择
        path = self.selected_file
        save_path = self.selected_folder
        save_name = self.output_name.GetValue()
        img_width, img_height = self.img_width.GetValue(), self.img_height.GetValue()
        bit_depth = self.bit_depth.GetStringSelection()
        selected_format = self.output_format.GetStringSelection()
        input_bayer_format = self.input_bayer_format.GetStringSelection()
        output_bayer_format = self.output_bayer_format.GetStringSelection()
        # 判断输入是否有效
        if not path:
            wx.MessageBox("Please select input file", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not save_path:
            wx.MessageBox('Please select output path','Error', wx.OK | wx.ICON_ERROR)
            return
        if not save_name:
            wx.MessageBox('Please enter output name','Error', wx.OK | wx.ICON_ERROR)
            return
        else:
            if not is_valid_windows_filename(save_name):
                wx.MessageBox('Output name is invalid', 'Error', wx.OK | wx.ICON_ERROR)
                return

        img_width, img_height, flag = validate_and_convert_size(img_width, img_height)

        if not flag:
            wx.MessageBox("Input number invalid", "Error", wx.OK | wx.ICON_ERROR)
            return

        # 位深度判断
        if bit_depth == '8 bit': dtype = np.uint8
        else: dtype = np.uint16
        # 图像读取
        with open(path, 'rb') as file:
            img = np.fromfile(file, dtype=dtype)
            img = img.reshape((img_height, img_width))
        # 转换
        trans_sentence = f'{input_bayer_format} to {output_bayer_format}'
        output_img = cv2.cvtColor(img, translate_dict[trans_sentence])
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
    frame = DeBayer(None)
    frame.SetTitle('Raw DeBayer')
    frame.SetSize((900, 650))
    frame.Show()
    app.MainLoop()
