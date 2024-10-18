#Author: Stan Yin
#GitHub Name: SomeB1oody
#This project is based on CC 4.0 BY, please mention my name if you use it.
#This project requires opencv, numpy, wxWidgets and re.
import numpy as np
import wx
import cv2
import re

def average_downsample(image, factor):
    h, w, _ = image.shape
    # INTER_AREA 是专为缩小图像设计的插值方法
    image_resized = cv2.resize(image, (w // factor, h // factor), interpolation=cv2.INTER_AREA)
    return image_resized

def max_pooling(image, factor):
    h, w, _ = image.shape
    pooled_image = np.zeros((h // factor, w // factor, 3), dtype=np.uint8)
    # 遍历每个 factor x factor 的像素块
    for i in range(0, h, factor):
        for j in range(0, w, factor):
            # 取出当前的像素块
            block = image[i:i+factor, j:j+factor]
            pooled_image[i//factor, j//factor] = np.max(block, axis=(0, 1))
    return pooled_image

def bilinear_interpolation(image, factor):
    h, w, _ = image.shape
    # INTER_LINEAR 是用于缩放图像的双线性插值方法
    image_resized = cv2.resize(image, (w // factor, h // factor), interpolation=cv2.INTER_LINEAR)
    return image_resized

def bicubic_interpolation(image, factor):
    h, w, _ = image.shape
    # INTER_CUBIC 是用于缩放图像的双三次插值方法
    image_resized = cv2.resize(image, (w // factor, h // factor), interpolation=cv2.INTER_CUBIC)
    return image_resized

def lanczos_resampling(image, factor):
    h, w, _ = image.shape
    # INTER_LANCZOS4 是用于缩放图像的 Lanczos 插值方法
    image_resized = cv2.resize(image, (w // factor, h // factor), interpolation=cv2.INTER_LANCZOS4)
    return image_resized

def nearest_neighbor(image, factor):
    h, w, _ = image.shape
    # INTER_NEAREST 是用于缩放图像的邻近插值方法
    image_resized = cv2.resize(image, (w // factor, h // factor), interpolation=cv2.INTER_NEAREST)
    return image_resized

def gaussian_downsampling(image, factor):
    # pyrDown 每次将图像宽度和高度缩小为原来的一半，同时进行高斯平滑，减少细节和噪声
    for i in range(factor):
        image = cv2.pyrDown(image)
    return image

def adaptive_downsampling(image, factor):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 使用自适应阈值处理，将灰度图像转换为二值图像
    # 该方法根据图像局部区域的亮度自适应地调整阈值
    adaptive_thresh = (
    cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    )
    return cv2.resize(adaptive_thresh, (adaptive_thresh.shape[1] // factor, adaptive_thresh.shape[0] // factor))

def method_choice(method, img, factor):
    match method:
        case 'Average downsample':
            resized_img = average_downsample(img, factor=factor)
        case 'Max pooling':
            resized_img = max_pooling(img, factor=factor)
        case 'Bilinear Interpolation':
            resized_img = bilinear_interpolation(img, factor=factor)
        case 'Bicubic Interpolation':
            resized_img = bicubic_interpolation(img, factor=factor)
        case 'Lanczos Resampling':
            resized_img = lanczos_resampling(img, factor=factor)
        case 'Nearest Neighbor':
            resized_img = nearest_neighbor(img, factor=factor)
        case 'Gaussian Downsampling':
            resized_img = gaussian_downsampling(img, factor=factor)
        case 'Adaptive Downsampling':
            resized_img = adaptive_downsampling(img, factor=factor)
        case _:
            resized_img = None

    return resized_img

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

def input_process(input_path, output_path, output_name, format_choice, factor, method):
    # 输入&读取
    if input_path is None: return False, 'Please provide input path', None, None, None, None
    img = cv2.imread(input_path)
    if img is None: return False, 'Cannot load image', None, None, None, None

    # 输出名称
    if output_name is None: return False, 'Please provide output name', None, None, None, None
    if not is_valid_windows_filename(output_name): return False, 'Invalid output filename', None, None, None, None

    # 输出路径与名称的合成
    if output_path is None: return False, 'Please provide output path', None, None, None, None
    save_path = f'{output_path}{output_name}{format_choice}'

    # factor输入
    if factor is None: return False, 'Please provide factor', None, None, None, None, None
    if not factor.isdigit(): return False, 'Factor must be an Non-zero real number', None, None, None, None
    if int(factor) >= min(img.shape[:2]):
        return False, 'factor cannot be greater than image\'s actual size', None, None, None, None
    if int(factor) == 0:
        return False, 'factor cannot be zero', None, None, None, None

    # method输入
    if not method:
        return False, 'Please choose the method of sampling', None, None, None, None

    return True, None, img, save_path, int(factor), method

class ImageReducer(wx.Frame):
    def __init__(self, *args, **kw):
        super(ImageReducer, self).__init__(*args, **kw)

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

        # 输入图片输出名称
        self.vbox.Add(wx.StaticText(panel, label=
        "Output image name:(no file suffix)"), flag=wx.ALL, border=5)
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

        # 输入factor
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.StaticText(panel, label=
        "Enter factor(Non-zero natural number):"), flag=wx.ALL, border=5)
        self.factor = wx.TextCtrl(panel)
        hbox.Add(self.factor, flag=wx.ALL, border=5)
        self.vbox.Add(hbox, flag=wx.ALL, border=5)

        # 选择采样方法
        self.lb_method = wx.ListBox(panel, choices=[
            'Average downsample', 'Max pooling', 'Bilinear Interpolation', 'Bicubic Interpolation',
            'Lanczos Resampling', 'Nearest Neighbor', 'Gaussian Downsampling', 'Adaptive Downsampling',
            'Quadtree Decomposition'
        ], style=wx.LB_SINGLE)
        self.vbox.Add(self.lb_method, flag=wx.ALL, border=5)

        # 预览按钮
        self.preview_button = wx.Button(panel, label="Convert")
        self.preview_button.Bind(wx.EVT_BUTTON, self.on_preview)
        self.vbox.Add(self.preview_button, flag=wx.ALL, border=5)

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

    def on_preview(self, event):
        flag, error_message, img, _, factor, method = input_process(
            self.selected_file, self.selected_folder, self.output_name.GetValue(),
        self.output_format.GetStringSelection(),self.factor.GetValue(), self.lb_method.GetStringSelection()
        )
        if not flag:
            wx.MessageBox(error_message,'Error', wx.OK | wx.ICON_ERROR)
            return

        resized_img = method_choice(method, img, factor)
        cv2.imshow("Preview", resized_img)

    def on_convert(self, event):
        flag, error_message, img, save_path, factor, method = input_process(
            self.selected_file, self.selected_folder, self.output_name.GetValue(),
            self.output_format.GetStringSelection(), self.factor.GetValue(), self.lb_method.GetStringSelection()
        )
        if not flag:
            wx.MessageBox(error_message,'Error', wx.OK | wx.ICON_ERROR)
            return

        resized_img = method_choice(method, img, factor)

        try:
            cv2.imwrite(save_path, resized_img)
            wx.MessageBox(f"Image saved as {save_path}", 'Success', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f'{e}', 'Error', wx.OK | wx.ICON_ERROR)
            return

if __name__ == "__main__":
    app = wx.App()
    frame = ImageReducer(None)
    frame.SetTitle('Color Master')
    frame.SetSize((800, 525))
    frame.Show()
    app.MainLoop()
