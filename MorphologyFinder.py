import cv2
import wx
from navigator_updater.widgets.dialogs import MessageBox


def convert_to_double(str1, str2):
    # 初始化返回的值
    double1, double2 = None, None
    error_message = None
    success = True

    # 转换第一个字符串
    try:
        if str1 != "":  # 空字符串跳过转换，直接赋值 None
            double1 = float(str1)
            if double1 < 0:  # 检查是否为负数
                success = False
                error_message = f"Error: First input is negative: {str1}"
        # 空字符串情况算作成功转换
    except ValueError:
        success = False
        error_message = f"Error: First input is not a valid number: {str1}"

    # 转换第二个字符串
    try:
        if str2 != "":  # 空字符串跳过转换，直接赋值 None
            double2 = float(str2)
            if double2 < 0:  # 检查是否为负数
                success = False
                error_message = f"Error: Second input is negative: {str2}"
    except ValueError:
        success = False
        error_message = f"Error: Second input is not a valid number: {str2}"

    return success, double1, double2, error_message

def detect_rectangles(img, min_area, aspect_ratio_range_min, aspect_ratio_range_max):

    # 1. 转换为灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. 高斯模糊去噪
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Canny 边缘检测
    edged = cv2.Canny(blurred, 50, 150)

    # 4. 形态学膨胀操作
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edged, kernel, iterations=2)

    # 5. 找到轮廓
    contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 6. 遍历所有轮廓，筛选矩形
    rectangles = []
    for contour in contours:
        # 使用多边形逼近轮廓
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # 如果多边形有 4 个顶点，并且是凸的，则认为是矩形
        if len(approx) == 4 and cv2.isContourConvex(approx):
            # 计算矩形的面积
            area = cv2.contourArea(approx)
            if min_area:
                if area < min_area:
                    continue  # 忽略面积太小的矩形

            # 计算矩形的宽高比
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)

            if aspect_ratio_range_min or aspect_ratio_range_max:

                if aspect_ratio_range_min and aspect_ratio_range_max:
                    if aspect_ratio_range_min <= aspect_ratio <= aspect_ratio_range_max:
                        rectangles.append(approx)

                elif aspect_ratio_range_min:
                    if aspect_ratio_range_min <= aspect_ratio:
                        rectangles.append(approx)

                elif aspect_ratio_range_max:
                    if aspect_ratio <= aspect_ratio_range_max:
                        rectangles.append(approx)

    # 7. 在图像上绘制矩形
    img_with_rectangles = img.copy()
    for rect in rectangles:
        cv2.drawContours(img_with_rectangles, [rect], -1, (0, 255, 0), 3)

    return img_with_rectangles

class MorphologyRectangle(wx.Frame):
    def __init__(self, *args, **kw):
        super(MorphologyRectangle, self).__init__(*args, **kw)

        panel = wx.Panel(self)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # 输入图片路径
        self.vbox.Add(wx.StaticText(panel, label="Input image path:"), flag=wx.ALL, border=5)
        self.vbox.Add(wx.StaticText(panel, label="Example:C:\\Wallpaper\\02.png"), flag=wx.ALL, border=5)
        self.input_path = wx.TextCtrl(panel)
        self.vbox.Add(self.input_path, flag=wx.EXPAND | wx.ALL, border=5)
        # 最小面积
        self.vbox.Add(wx.StaticText(panel, label=
        "Specify the minimum area(pixel^2) to look for(not specified if left blank)："
        ), flag=wx.ALL, border=5)
        self.vbox.Add(wx.StaticText(panel, label="Digit only"), flag=wx.ALL, border=5)
        self.minimum_area = wx.TextCtrl(panel)
        self.vbox.Add(self.minimum_area, flag=wx.ALL, border=5)
        # 长宽比
        self.vbox.Add(wx.StaticText(panel, label=
        "Specify the aspect ratio range to look for(not specified if left blank)"
        ), flag=wx.ALL, border=5)
        self.vbox.Add(wx.StaticText(panel, label=
        "Digit only     Example: 0.9 ~ 1.1"
        ), flag=wx.ALL, border=5)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.range_min = wx.TextCtrl(panel)
        self.range_max = wx.TextCtrl(panel)
        self.hbox.Add(self.range_min, flag=wx.ALL, border=2)
        self.hbox.Add(wx.StaticText(panel, label="~"), flag=wx.ALL, border=5)
        self.hbox.Add(self.range_max, flag=wx.ALL, border=2)
        self.vbox.Add(self.hbox, flag=wx.ALL, border=5)
        # 查找按钮
        self.find_button = wx.Button(panel, label="Find")
        self.find_button.Bind(wx.EVT_BUTTON, self.on_find_button)
        self.vbox.Add(self.find_button, flag=wx.ALL, border=5)
        # 设置面板的布局管理器
        panel.SetSizer(self.vbox)
        panel.Layout()

    def on_find_button(self, event):
        #获取输入
        path = self.input_path.GetValue()
        min_area = self.minimum_area.GetValue()
        rmin = self.range_min.GetValue()
        rmax = self.range_max.GetValue()

        if path:
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is None:
                wx,MessageBox("Fail to load image", "Error", wx.OK, wx.ICON_ERROR)
                return
        else:
            wx.MessageBox("Please enter input path first", 'Error', wx.OK | wx.ICON_ERROR)
            return

        if min_area:
            if min_area.isdigit():
               min_area = int(min_area)
               if min_area == 0:
                   wx.MessageBox(
                       "input should be a nonnegative integer", "Error", wx.OK | wx.ICON_ERROR)
               return
            else:
                wx.MessageBox(
                "input should be a nonnegative integer", "Error", wx.OK | wx.ICON_ERROR)
                return

        flag, range_min, range_max, error_message = convert_to_double(rmin, rmax)
        if not flag:
            wx.MessageBox(error_message, "Error", wx.OK | wx.ICON_ERROR)
            return

        img_with_rectangles = detect_rectangles(img, min_area, range_min, range_max)
        cv2.imshow("Morphology", img_with_rectangles)
        cv2.waitKey(0)


if __name__ == "__main__":
    app = wx.App()
    frame = MorphologyRectangle(None)
    frame.SetTitle('Morphology Transformer')
    frame.SetSize((500, 325))
    frame.Show()
    app.MainLoop()