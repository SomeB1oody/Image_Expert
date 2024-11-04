#Author: Stan Yin
#GitHub Name: SomeB1oody
#This project is based on CC 4.0 BY, please mention my name if you use it.
#This project requires opencv, numpy, wxWidgets and re.
import numpy as np
import cv2
import wx
import re

border_dict = {
    'Constant': cv2.BORDER_CONSTANT,
    'Replicated': cv2.BORDER_REPLICATE,
    'Reflected': cv2.BORDER_REFLECT,
    'Reflected (Symmetry)': cv2.BORDER_REFLECT_101,
    'Wrapped': cv2.BORDER_WRAP,
}

interpolation_dict = {
    'Nearest Neighbor': cv2.INTER_NEAREST,
    'Bilinear': cv2.INTER_LINEAR,
    'Bicubic': cv2.INTER_CUBIC,
    'Lanczos': cv2.INTER_LANCZOS4,
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


def load_img(path):
    if not path:
        wx.MessageBox('Please enter image path first', 'Error', style=wx.OK | wx.ICON_ERROR)
        return
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        wx.MessageBox('Cannot load image', 'Error', style=wx.OK | wx.ICON_ERROR)
        return
    return img

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect

def four_point_transform(pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    return maxWidth, maxHeight

def validate_points(pt_values, img_shape):
    # 检查输入的点是否有效
    for pt in pt_values:
        if not pt:
            return False, 'Please enter position first'
        if not pt.isdigit():
            return False, 'Input must be a number that is greater than zero.'
    for pt_x, pt_y in zip(pt_values[::2], pt_values[1::2]):
        if int(pt_x) > img_shape[1]:
            return False, 'X position cannot be greater than actual image width.'
        if int(pt_y) > img_shape[0]:
            return False, 'Y position cannot be greater than actual image height.'
    return True, None


def get_points(x1, y1, x2, y2, x3, y3, x4, y4):
    # 从输入框获取点坐标
    pt_values = [
        x1, y1,
        x2, y2,
        x3, y3,
        x4, y4
    ]
    return pt_values

def width_and_height(width, height, max_width, max_height):
    if not width and not height: return False, 'Please enter width or height first.'

    if width.isdigit() and height.isdigit(): width_, height_ = int(width), int(height)
    else: return False, 'Input should be a number that is greater than zero.'

    min_ = width_ > 0 and height_ > 0
    max_ = width_ <= max_width and height_ <= max_height

    if min_ and max_: return True, None
    elif not min_: return False, 'Input should be greater than zero.'
    elif not max_: return False, 'Input cannot be greater than actual image size.'
    else: return False, 'Input should be greater than zero and cannot be greater than actual image size.'

def correct_perspective(img):
    # 调整对比度和亮度
    contrast_image = cv2.convertScaleAbs(img, alpha=1.8, beta=-30)

    # 将图像转换为灰度图
    gray_image = cv2.cvtColor(contrast_image, cv2.COLOR_BGR2GRAY)

    # 使用双边滤波以保留边缘并减少噪声
    filter_image = cv2.bilateralFilter(gray_image, 13, 26, 6)

    # 使用二值化处理（阈值210，最大值255）
    _, binary = cv2.threshold(filter_image, 210, 255, cv2.THRESH_BINARY_INV)

    # Canny
    edges = cv2.Canny(binary, 100, 200)

    # 膨胀
    kernel = np.ones((16, 16), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=5)

    # 查找轮廓
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 按轮廓面积从大到小排序，选择最大的轮廓
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    if len(contours) == 0:
        raise ValueError("No outline was found in the image.")

    # 将最大的轮廓逼近为多边形
    epsilon = 0.02 * cv2.arcLength(contours[0], True)
    approx = cv2.approxPolyDP(contours[0], epsilon, True)

    # 确保逼近后的多边形有 4 个点（即四边形）
    if len(approx) != 4:
        raise ValueError("The quadrilateral outline for perspective transformation could not be found.")

    # 获取四个角点
    pts = approx.reshape(4, 2)

    # 对角点进行排序：左上、右上、右下、左下
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # 左上角
    rect[2] = pts[np.argmax(s)]  # 右下角
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # 右上角
    rect[3] = pts[np.argmax(diff)]  # 左下角

    # 计算新图像的宽度和高度
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    # 目标图像的四个点位置（透视变换后的位置）
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    # 计算透视变换矩阵
    M = cv2.getPerspectiveTransform(rect, dst)

    # 应用透视变换
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    return warped, rect

class RectangleTransformer(wx.Frame):
    def __init__(self, *args, **kw):
        super(RectangleTransformer, self).__init__(*args, **kw)

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
        # 选择手动还是自动
        self.manual_or_auto = wx.RadioBox(
            panel, label="Recognize 4 corners", choices=[
                'Auto', 'Manual'
            ]
        )
        self.vbox.Add(self.manual_or_auto, flag=wx.ALL, border=5)
        # 手动输入点坐标
        self.vbox.Add(wx.StaticText(panel, label=
        "Manually enter positions of 4 corners:"
        ), flag=wx.ALL, border=5)
        # pt1
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(wx.StaticText(panel, label="Point1:(x,y)"), flag=wx.ALL, border=5)
        self.pt1_x = wx.TextCtrl(panel)
        self.hbox1.Add(self.pt1_x, flag=wx.EXPAND, border=5)
        self.hbox1.Add(wx.StaticText(panel, label=","), flag=wx.ALL, border=2)
        self.pt1_y = wx.TextCtrl(panel)
        self.hbox1.Add(self.pt1_y, flag=wx.EXPAND, border=5)
        self.vbox.Add(self.hbox1, flag=wx.ALL, border=5)
        # pt2
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(wx.StaticText(panel, label="Point2:(x,y)"), flag=wx.ALL, border=5)
        self.pt2_x = wx.TextCtrl(panel)
        self.hbox2.Add(self.pt2_x, flag=wx.EXPAND, border=5)
        self.hbox2.Add(wx.StaticText(panel, label=","), flag=wx.ALL, border=2)
        self.pt2_y = wx.TextCtrl(panel)
        self.hbox2.Add(self.pt2_y, flag=wx.EXPAND, border=5)
        self.vbox.Add(self.hbox2, flag=wx.ALL, border=5)
        # pt3
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(wx.StaticText(panel, label="Point3:(x,y)"), flag=wx.ALL, border=5)
        self.pt3_x = wx.TextCtrl(panel)
        self.hbox3.Add(self.pt3_x, flag=wx.EXPAND, border=5)
        self.hbox3.Add(wx.StaticText(panel, label=","), flag=wx.ALL, border=2)
        self.pt3_y = wx.TextCtrl(panel)
        self.hbox3.Add(self.pt3_y, flag=wx.EXPAND, border=5)
        self.vbox.Add(self.hbox3, flag=wx.ALL, border=5)
        # pt4
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(wx.StaticText(panel, label="Point4:(x,y)"), flag=wx.ALL, border=5)
        self.pt4_x = wx.TextCtrl(panel)
        self.hbox4.Add(self.pt4_x, flag=wx.EXPAND, border=5)
        self.hbox4.Add(wx.StaticText(panel, label=","), flag=wx.ALL, border=2)
        self.pt4_y = wx.TextCtrl(panel)
        self.hbox4.Add(self.pt4_y, flag=wx.EXPAND, border=5)
        self.vbox.Add(self.hbox4, flag=wx.ALL, border=5)
        # 插值算法选择
        self.interpolation = wx.RadioBox(
            panel, label="Choose interpolation algorithm:", choices=[
                'Nearest Neighbor', 'Bilinear', 'Bicubic', 'Lanczos'
            ]
        )
        self.vbox.Add(self.interpolation, flag=wx.ALL, border=5)
        # 边界像素算法选择
        self.border = wx.RadioBox(
            panel, label="Choose border handling method:", choices=[
                'Constant', 'Replicated', 'Reflected', 'Reflected (Symmetry)', 'Wrapped'
            ]
        )
        self.vbox.Add(self.border, flag=wx.ALL, border=2)
        # Preview Button
        self.preview_button = wx.Button(panel, label="Preview")
        self.preview_button.Bind(wx.EVT_BUTTON, self.on_preview)
        self.vbox.Add(self.preview_button, flag=wx.ALL, border=5)
        # 转换按钮
        self.transform_button = wx.Button(panel, label="Transform")
        self.transform_button.Bind(wx.EVT_BUTTON, self.on_transform)
        self.vbox.Add(self.transform_button, flag=wx.ALL, border=5)
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
        # 获取用户输入
        input_path = self.selected_file
        manual_or_auto = self.manual_or_auto.GetStringSelection()
        if not input_path:
            wx.MessageBox('Please select an input image', 'Error', wx.OK | wx.ICON_ERROR)
            return
        # 图片输入
        img = load_img(input_path)

        if manual_or_auto == 'Auto': img_perspective, sorted_pts = correct_perspective(img)
        else:
            pt1_x, pt1_y = self.pt1_x.GetValue(), self.pt1_y.GetValue()
            pt2_x, pt2_y = self.pt2_x.GetValue(), self.pt2_y.GetValue()
            pt3_x, pt3_y = self.pt3_x.GetValue(), self.pt3_y.GetValue()
            pt4_x, pt4_y = self.pt4_x.GetValue(), self.pt4_y.GetValue()
            pt_values = get_points(pt1_x, pt1_y, pt2_x, pt2_y, pt3_x, pt3_y, pt4_x, pt4_y)
            valid, error_message = validate_points(pt_values, img.shape)
            if not valid:
                wx.MessageBox(error_message, 'Error', wx.OK | wx.ICON_ERROR)
                return

            points = [(int(pt_values[i]) - 1, int(pt_values[i + 1]) - 1) for i in range(0, len(pt_values), 2)]
            # 变换后图片生成
            current = np.array(points[:4], dtype=np.float32)
            width_, height_ = four_point_transform(current)
            change = np.array([[0, 0], [width_, 0], [width_, height_], [0, height_]], dtype=np.float32)
            sorted_pts = order_points(current)
            transfer_matrix = cv2.getPerspectiveTransform(sorted_pts, change)

            img_perspective = cv2.warpPerspective(img, transfer_matrix, (width_, height_))

        # 带Mask的原图生成
        img_ = img.copy()
        for i in range(4):
            cv2.circle(img_, sorted_pts[i], 3, (0, 0, 255), -1)

        cv2.polylines(img_, sorted_pts, True, (0, 0, 255), thickness=2)

        cv2.imshow('Box', img_)
        cv2.imshow('Transformed', img_perspective)
        cv2.waitKey(0)

    def on_transform(self, event):
        # 获取用户输入
        input_path = self.selected_file
        output_path = self.selected_folder
        output_name = self.output_name.GetValue()
        output_format = self.output_format.GetStringSelection()
        manual_or_auto = self.manual_or_auto.GetStringSelection()
        interpolation = self.interpolation.GetStringSelection()
        border = self.border.GetStringSelection()
        if not input_path:
            wx.MessageBox('Please select an input image', 'Error', wx.OK | wx.ICON_ERROR)
            return
        if not output_path:
            wx.MessageBox('Please select an output path', 'Error', wx.OK | wx.ICON_ERROR)
            return
        if not output_name:
            wx.MessageBox('Please enter output name', 'Error', wx.OK | wx.ICON_ERROR)
            return
        else:
            if is_valid_windows_filename(output_name):
                wx.MessageBox('Output name invalid, please try again', wx.OK | wx.ICON_ERROR)
                return
        # 图片输入
        img = load_img(input_path)

        if manual_or_auto == 'Auto': img_perspective, sorted_pts = correct_perspective(img)
        # 手动输入
        else:
            pt1_x, pt1_y = self.pt1_x.GetValue(), self.pt1_y.GetValue()
            pt2_x, pt2_y = self.pt2_x.GetValue(), self.pt2_y.GetValue()
            pt3_x, pt3_y = self.pt3_x.GetValue(), self.pt3_y.GetValue()
            pt4_x, pt4_y = self.pt4_x.GetValue(), self.pt4_y.GetValue()
            pt_values = get_points(pt1_x, pt1_y, pt2_x, pt2_y, pt3_x, pt3_y, pt4_x, pt4_y)
            valid, error_message = validate_points(pt_values, img.shape)
            if not valid:
                wx.MessageBox(error_message, 'Error', wx.OK | wx.ICON_ERROR)
                return

            points = [(int(pt_values[i]) - 1, int(pt_values[i + 1]) - 1) for i in range(0, len(pt_values), 2)]
            # 变换后图片生成
            current = np.array(points[:4], dtype=np.float32)
            width_, height_ = four_point_transform(current)
            change = np.array([[0, 0], [width_, 0], [width_, height_], [0, height_]], dtype=np.float32)
            sorted_pts = order_points(current)
            transfer_matrix = cv2.getPerspectiveTransform(sorted_pts, change)

            img_perspective = cv2.warpPerspective(
                img, transfer_matrix, (img.shape[1], img.shape[0]),
                interpolation_dict[interpolation], border_dict[border]
            )

        #图片保存
        path_ = f'{output_path}{output_name}{output_format}'
        try:
            cv2.imwrite(path_, img_perspective)
            wx.MessageBox(f'Image saved as {path_}', 'Success', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)

if __name__ == "__main__":
    app = wx.App()
    frame = RectangleTransformer(None)
    frame.SetTitle('Perspective Transformer')
    frame.SetSize((800, 680))
    frame.Show()
    app.MainLoop()
