#Author: Stan Yin
#GitHub Name: SomeB1oody
#This project is based on CC 4.0 BY, please mention my name if you use it.
#This project requires opencv, os and wxWidgets.
import wx
import cv2
import numpy as np
import os

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
class DeBayer(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        panel = wx.Panel(self)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # 输入图片路径
        self.vbox.Add(wx.StaticText(panel, label="Input image path:"), flag=wx.ALL, border=5)
        self.vbox.Add(wx.StaticText(panel, label="Example:C:\\Wallpaper\\02.png"), flag=wx.ALL, border=5)
        self.input_path = wx.TextCtrl(panel)
        self.vbox.Add(self.input_path, flag=wx.EXPAND | wx.ALL, border=5)
        # 输入图片宽
        self.vbox.Add(wx.StaticText(panel, label="Please enter the image width："), flag=wx.ALL, border=5)
        self.img_width = wx.TextCtrl(panel)
        # 输入图片高
        self.vbox.Add(wx.StaticText(panel, label="Please enter the image height："), flag=wx.ALL, border=5)
        self.img_height = wx.TextCtrl(panel)
        # 输入图片位深度
        self.bit_depth = wx.RadioBox(panel, label="Choose bit depth:", choices=['8 bit', '16 bit'])
        self.vbox.Add(self.bit_depth, flag=wx.ALL, border=5)
        # 输入图片输出名称
        self.vbox.Add(wx.StaticText(panel, label="Output image name:(no file suffix)"), flag=wx.ALL, border=5)
        self.output_name = wx.TextCtrl(panel)
        self.vbox.Add(self.output_name, flag=wx.EXPAND | wx.ALL, border=5)
        # 输入图片输出位置
        self.vbox.Add(wx.StaticText(panel, label="Output image path:"), flag=wx.ALL, border=5)
        self.vbox.Add(wx.StaticText(panel, label="Example:C:\\Wallpaper\\"), flag=wx.ALL, border=5)
        self.output_path = wx.TextCtrl(panel)
        self.vbox.Add(self.output_path, flag=wx.EXPAND | wx.ALL, border=5)
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
        self.output_bayer_format = wx.RadioBox(panel, label="Choose input bayer format:", choices=[
            'BGR', 'BGR(EA)', 'BGR (VNG)', 'BGRA', 'RGB', 'RGB(EA)', 'RGB(VNG)', 'RGBA', 'GRAY'
        ])
        self.vbox.Add(self.output_bayer_format, flag=wx.ALL, border=5)
        # Tip
        self.vbox.Add(wx.StaticText(panel, label=
        "If you need other color formats, using ColorMixer.py is a good choice."), flag=wx.ALL, border=5)
        # 转换按钮
        self.convert_button = wx.Button(panel, label="Convert")
        self.convert_button.Bind(wx.EVT_BUTTON, self.on_convert)
        self.vbox.Add(self.convert_button, flag=wx.ALL, border=5)

        # 设置面板的布局管理器
        panel.SetSizer(self.vbox)
        panel.Layout()

    def on_convert(self, event):
        # 获取用户选择
        path = self.input_path.GetValue()
        save_path = self.output_path.GetValue()
        save_name = self.output_name.GetValue()
        img_width, img_height = self.img_width.GetValue(), self.img_height.GetValue()
        bit_depth = self.bit_depth.GetStringSelection()
        selected_format = self.output_format.GetStringSelection()
        input_bayer_format = self.input_bayer_format.GetStringSelection()
        output_bayer_format = self.output_bayer_format.GetStringSelection()
        # 判断输入是否有效
        if not path:
            wx.MessageBox("Please enter image path", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not save_path or not save_name:
            wx.MessageBox('Please enter output path and name','Error', wx.OK | wx.ICON_ERROR)
            return
        if not os.path.exists(path):
            wx.MessageBox(f"File path '{path}' does not exist",'Error', wx.OK | wx.ICON_ERROR)
            return
        if not os.path.isfile(path):
            wx.MessageBox(f"Cannot find file in path '{path}'",'Error', wx.OK | wx.ICON_ERROR)
            return
        if img_width.isdigit():
            if int(img_width) <= 0:
                wx.MessageBox("Width must be greater than 0",'Error', wx.OK | wx.ICON_ERROR)
                return
            else: img_width = int(img_width)
        else: wx.MessageBox("Width must be a digit",'Error', wx.OK | wx.ICON_ERROR)
        if img_height.isdigit():
            if int(img_height) <= 0:
                wx.MessageBox("Height must be greater than 0",'Error', wx.OK | wx.ICON_ERROR)
                return
            else: img_height = int(img_height)
        else: wx.MessageBox("Height must be a digit",'Error', wx.OK | wx.ICON_ERROR)
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
        output_ = f"{save_path}{save_name}{selected_format}"
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
    frame.SetSize((900, 600))
    frame.Show()
    app.MainLoop()