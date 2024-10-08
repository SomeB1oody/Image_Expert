#Author: Stan Yin
#GitHub Name: SomeB1oody
#This project is based on CC 4.0 BY, please mention my name if you use it.
#This project requires opencv.
import numpy as np
import cv2
import wx

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

def load_img(path):
    if not path:
        wx.MessageBox('Please enter image path first', 'Error', style=wx.OK | wx.ICON_ERROR)
        return
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        wx.MessageBox('Cannot load image', 'Error', style=wx.OK | wx.ICON_ERROR)
        return
    return img

def order_points(points):
    # 找到四个点的平均值（中心点）
    center = np.mean(points, axis=0)

    # 按照与中心点的相对位置进行排序
    sorted_points = sorted(points, key=lambda p: np.arctan2(p[1] - center[1], p[0] - center[0]))

    # 将排序后的点分成左半部分和右半部分
    left_points = sorted(sorted_points[:2], key=lambda p: p[0])  # x坐标最小的两个点
    right_points = sorted(sorted_points[2:], key=lambda p: p[0])  # x坐标最大的两个点

    # 返回左上、右上、右下、左下的顺序
    return np.array([left_points[0], right_points[0], right_points[1], left_points[1]])

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

def find_corners(img):
    img_contrast = cv2.convertScaleAbs(img, alpha = 1.8, beta = 30)
    img_gray = cv2.cvtColor(img_contrast, cv2.COLOR_BGR2GRAY)
    img_filter = cv2.bilateralFilter(img_gray, 13, 26, 6)
    img_binary = cv2.threshold(img_filter, 180, 255, cv2.THRESH_BINARY_INV)
    img_canny = cv2.Canny(img_binary, 10, 100, 3, False)
    hough_lines = cv2.HoughLines(img_canny, 5, np.pi / 180, 100)
    a = 50.0
    b = np.pi / 9
    remove_index = set()
    sign = False
    sign3 = True
    while sign3:
        new_line = []
        # Bubble
        for index1 in range(len(hough_lines)):
            for index2 in range(len(hough_lines[index1])-1):
                rho1, theta1 = hough_lines[index1]
                rho2, theta2 = hough_lines[index2]
                # 角度调整，确保比较的一致性
                if theta1 > np.pi: theta1 -= np.pi
                if theta2 > np.pi: theta2 -= np.pi
                # 判断是否为相似直线并标记删除
                sign1 = abs(theta1 - theta2) <= b
                sign2 = abs(rho1 - rho2) <= a

                if theta1 > np.pi / 2 > theta2 and np.pi - theta2 + theta1 < b: sign = True
                if theta2 > np.pi / 2 > theta1 and np.pi - theta1 + theta2 < b: sign = True

                if sign and sign1 and sign2: remove_index.add(index2)
        # 删除标记的直线
        for index4 in range(len(hough_lines)):
            if index4 not in remove_index: new_line.append(hough_lines[index4])
        # 直线数量达到目标值则终止循环
        hough_lines = np.array(new_line)
        if len(hough_lines) == 4: sign3 = False

    threshold_ = 0.2 * min(img.shape[0], img.shape[1])
    points = []

    # 分别计算宽度和高度的阈值
    width_threshold = 0.2 * img.shape[1]
    height_threshold = 0.2 * img.shape[0]
    points = []

    for index5 in range(len(new_line)):
        for index6 in range(index5 + 1, len(new_line)):
            rho3, theta3 = hough_lines[index5]
            rho4, theta4 = hough_lines[index6]

            # 调整θ值以处理斜率无穷大的情况
            if theta3 == 0: theta3 = 0.01
            if theta4 == 0: theta4 = 0.01

            # 计算直线交点
            a1 = np.cos(theta3)
            a2 = np.sin(theta3)
            b1 = np.cos(theta4)
            b2 = np.sin(theta4)

            x = (rho4 * b1 - rho3 * b2) / (a2 * b1 - a1 * b2)
            y = (rho3 - a1 * x) / b1

            # 保证交点在图像范围内
            pt = (int(round(x)), int(round(y)))

            # 使用不同的阈值来判断x和y是否在图像范围内
            if -width_threshold <= pt[0] <= img.shape[1] + width_threshold and \
                -height_threshold <= pt[1] <= img.shape[0] + height_threshold:
                points.append(pt)

    return points



class RectangleTransformer(wx.Frame):
    def __init__(self, *args, **kw):
        super(RectangleTransformer, self).__init__(*args, **kw)

        panel = wx.Panel(self)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # 输入图片路径
        self.vbox.Add(wx.StaticText(panel, label=
        "Input image path:"), flag=wx.ALL, border=5)
        self.vbox.Add(wx.StaticText(panel, label=
        "Example:C:\\Wallpaper\\02.png"), flag=wx.ALL, border=5)
        self.input_path = wx.TextCtrl(panel)
        self.vbox.Add(self.input_path, flag=wx.EXPAND | wx.ALL, border=5)

        # 输入图片输出名称
        self.vbox.Add(wx.StaticText(panel, label=
        "Output image name:(no file suffix)"), flag=wx.ALL, border=5)
        self.output_name = wx.TextCtrl(panel)
        self.vbox.Add(self.output_name, flag=wx.EXPAND | wx.ALL, border=5)

        # 输入图片输出位置
        self.vbox.Add(wx.StaticText(panel, label=
        "Output image path:"), flag=wx.ALL, border=5)
        self.vbox.Add(wx.StaticText(panel, label=
        "Example:C:\\Wallpaper\\"), flag=wx.ALL, border=5)
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
        # 转换后的图像大小
        self.vbox.Add(wx.StaticText(panel, label=
        "Type in image size you want after transformation: (width X height)"
                                    ), flag=wx.ALL, border=5)
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.width = wx.TextCtrl(panel)
        self.hbox5.Add(self.width, flag=wx.ALL, border=5)
        self.hbox5.Add(wx.StaticText(panel, label="X"), flag=wx.ALL, border=2)
        self.height = wx.TextCtrl(panel)
        self.hbox5.Add(self.height, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox5, flag=wx.ALL, border=5)
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

    def on_preview(self, event):
        # 获取用户输入
        input_path = self.input_path.GetValue()
        manual_or_auto = self.manual_or_auto.GetStringSelection()
        width, height = self.width.GetValue(), self.height.GetValue()
        # 图片输入
        img = load_img(input_path)

        flag, error_text = width_and_height(width, height, img.shape[1], img.shape[0])
        if not flag:
            wx.MessageBox(error_text, "Error", wx.OK)
            return
        else: width_, height_ = int(width), int(height)

        points = []
        if manual_or_auto == 'Auto': points = find_corners(img)
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
        change = np.array([[0, 0], [width_, 0], [width_, height_], [0, height_]], dtype=np.float32)
        sorted_pts = order_points(current)
        transfer_matrix = cv2.getPerspectiveTransform(sorted_pts, change)

        img_perspective = cv2.warpPerspective(img, transfer_matrix, (width_, height_))

        # 带Mask的原图生成
        img_ = img.copy()
        for i in range(4):
            cv2.circle(img_, points[i], 3, (0, 0, 255), -1)

        cv2.polylines(img_, sorted_pts, True, (0, 0, 255), thickness=2)

        cv2.imshow('Box', img_)
        cv2.imshow('Transformed', img_perspective)
        cv2.waitKey(0)

    def on_transform(self, event):
        # 获取用户输入
        input_path = self.input_path.GetValue()
        output_path = self.output_path.GetValue()
        output_name = self.output_name.GetValue()
        output_format = self.output_format.GetStringSelection()
        manual_or_auto = self.manual_or_auto.GetStringSelection()
        width, height = self.width.GetValue(), self.height.GetValue()
        interpolation = self.interpolation.GetStringSelection()
        border = self.border.GetStringSelection()
        # 图片输入
        img = load_img(input_path)

        flag, error_text = width_and_height(width, height, img.shape[1], img.shape[0])
        if not flag:
            wx.MessageBox(error_text, "Error", wx.OK)
            return
        else: width_, height_ = int(width), int(height)

        points = []
        if manual_or_auto == 'Auto': points = find_corners(img)
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
        change = np.array([[0, 0], [width_, 0], [width_, height_], [0, height_]], dtype=np.float32)
        sorted_pts = order_points(current)
        transfer_matrix = cv2.getPerspectiveTransform(sorted_pts, change)

        img_perspective = cv2.warpPerspective(
        img, transfer_matrix, (img.shape[1], img.shape[0]),
        interpolation_dict[interpolation], border_dict[border])
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
    frame.SetSize((825, 775))
    frame.Show()
    app.MainLoop()
