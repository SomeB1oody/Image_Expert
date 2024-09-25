import wx
import cv2
import numpy as np
global alpha, beta, gamma
alpha = 100
beta = 100
gamma = 100
global x, y, w, h
global img_without_crop, img

def crop(input_image, _x, _y, _w, _h):
    process_ = input_image.copy()
    # 确保矩形框的边界在图像内
    if _x + _w > input_image.shape[1]:
        _w = input_image.shape[1] - _x
    if _y + _h > input_image.shape[0]:
        _h = input_image.shape[0] - _y
    cv2.rectangle(process_, (_x, _y), (_x+_w, _y+_h), (0, 0, 255), 1)
    cv2.imshow("Crop", process_)

def mix_for_crop(input_image):
    global alpha, beta, gamma
    _process = cv2.convertScaleAbs(input_image, alpha=alpha / 100.0, beta=beta - 100)
    look_up_table = np.zeros((256,), dtype=np.uint8)
    for index in range(256):
        value = np.clip((index / 255.0) ** (gamma / 100.0) * 255.0, 0, 255)
        look_up_table[index] = np.uint8(value)
    output = cv2.LUT(input_image, look_up_table)
    return output

def mix_for_others(input_image, _alpha_, _beta_, _gamma_, window_name):
    look_up_table = np.zeros((256,), dtype=np.uint8)
    for index in range(256):
        value = np.clip((index / 255.0) ** (gamma / 100.0) * 255.0, 0, 255)
        look_up_table[index] = np.uint8(value)
    arg1 = cv2.LUT(input_image, look_up_table)
    arg2 = cv2.convertScaleAbs(arg1, alpha=_alpha_, beta=_beta_)
    cv2.imshow(window_name, arg2)

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

        # 输入图片路径
        vbox.Add(wx.StaticText(panel, label="Input image path:"), flag=wx.ALL, border=5)
        vbox.Add(wx.StaticText(panel, label="Example:C:\\Wallpaper\\02.png"), flag=wx.ALL, border=5)
        self.input_path = wx.TextCtrl(panel)
        vbox.Add(self.input_path, flag=wx.EXPAND | wx.ALL, border=5)
        #输入图片输出名称
        vbox.Add(wx.StaticText(panel, label="Output image name:(no file suffix)"), flag=wx.ALL, border=5)
        self.output_name = wx.TextCtrl(panel)
        vbox.Add(self.output_name, flag=wx.EXPAND | wx.ALL, border=5)
        #输入图片输出位置
        vbox.Add(wx.StaticText(panel, label="Output image path:"), flag=wx.ALL, border=5)
        vbox.Add(wx.StaticText(panel, label="Example:C:\\Wallpaper\\"), flag=wx.ALL, border=5)
        self.output_path = wx.TextCtrl(panel)
        vbox.Add(self.output_path, flag=wx.EXPAND | wx.ALL, border=5)

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
        #裁剪
        crop_button = wx.Button(panel, label="Crop")
        crop_button.Bind(wx.EVT_BUTTON, self._crop_)
        vbox.Add(crop_button, flag=wx.ALL, border=5)
        self.crop_choice = wx.RadioBox(panel, label="Crop", choices=['No crop', 'Save crop'])
        vbox.Add(self.crop_choice, flag=wx.ALL, border=1)
        # 色彩格式
        self.color_choice = wx.RadioBox(
            panel, label="Choose color format:", choices=[
                'Same', 'BGR(555)', 'BGR(565)','RGB', 'GRAY', 'HSV', 'HSV(Full)', 'HLS', 'HLS(Full)','YUV', 'LAB'
            ]
        )
        vbox.Add(self.color_choice, flag=wx.ALL, border=1)
        # 转换按钮
        convert_button = wx.Button(panel, label="Convert")
        convert_button.Bind(wx.EVT_BUTTON, self.on_convert)
        vbox.Add(convert_button, flag=wx.ALL, border=5)

        # 设置面板的布局管理器
        panel.SetSizer(vbox)

        # 触发布局更新
        panel.Layout()

    def brightness_and_contrast_adjustment(self, event):
        global gamma, alpha, beta, img
        load_image(self.input_path.GetValue())
        def alpha_track_bar(alpha_):
            global alpha, img
            alpha = alpha_
            mix_for_others(img, alpha / 100.0, beta - 100, gamma / 100.0,
            "Brightness and Contrast")

        def beta_track_bar(beta_):
            global beta, img
            beta = beta_
            mix_for_others(img, alpha / 100.0, beta - 100, gamma / 100.0,
            "Brightness and Contrast")

        cv2.namedWindow("Brightness and Contrast")
        cv2.createTrackbar("Contrast", "Brightness and Contrast",
        alpha, 200, alpha_track_bar)
        cv2.createTrackbar("Brightness", "Brightness and Contrast",
        beta, 200, beta_track_bar)

    def _gamma_correction_(self, event):
        global gamma, img
        load_image(self.input_path.GetValue())
        def gamma_track_bar(_gamma):
            global alpha, beta, gamma
            gamma = _gamma
            mix_for_others(img, alpha / 100.0, beta - 100, gamma / 100.0,
            "Gamma Correction")
        cv2.namedWindow("Gamma Correction")
        cv2.createTrackbar("Gamma", "Gamma Correction", gamma, 200, gamma_track_bar)

    def _crop_(self, event):
        load_image(self.input_path.GetValue())
        global x, y ,w ,h, img_without_crop, img
        img_without_crop = mix_for_crop(img)
        x = img_without_crop.shape[1] // 2
        y = img_without_crop.shape[0] // 2
        w = img_without_crop.shape[1] // 3
        h = img_without_crop.shape[0] // 3
        def x_track_bar(x_):
            global x, y, w, h
            x = x_
            crop(img_without_crop, x, y, w, h)
        def y_track_bar(y_):
            global x, y, w, h
            y = y_
            crop(img_without_crop, x, y, w, h)
        def h_track_bar(h_):
            global x, y, w, h
            h = h_
            crop(img_without_crop, x, y, w, h)
        def w_track_bar(w_):
            global x, y, h, w
            w = w_
            crop(img_without_crop, x, y, w, h)
        cv2.namedWindow("Crop")
        cv2.createTrackbar("X", "Crop", x, img_without_crop.shape[1], x_track_bar)
        cv2.createTrackbar("Y", "Crop", y, img_without_crop.shape[0], y_track_bar)
        cv2.createTrackbar("Width", "Crop", w, img_without_crop.shape[1], w_track_bar)
        cv2.createTrackbar("Height", "Crop", h, img_without_crop.shape[0], h_track_bar)

    def on_convert(self, event):
        global img, x, y ,w ,h
        #获取用户的选择
        load_image(self.input_path.GetValue())
        save_path = self.output_path.GetValue()
        save_name = self.output_name.GetValue()
        if not save_path or not save_name:
            wx.MessageBox('Please enter output path and name','Error', wx.OK | wx.ICON_ERROR)
            return
        selected_format = self.output_format.GetStringSelection()
        selected_color = self.color_choice.GetStringSelection()
        #裁剪
        if self.crop_choice.getValue() != 'No crop':    cropped_img = img[y:y + h, x:x + w]
        else:   cropped_img = img
        #Brightness Contrast Gamma
        mixed_img = mix_for_crop(cropped_img)
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
            'LAB': cv2.COLOR_BGR2LAB,
        }
        if selected_color != 'Same':
            output_img = cv2.cvtColor(mixed_img, color_format_dict[selected_color])
        else: output_img = mixed_img
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
    frame = ImageConverter(None)
    frame.SetTitle('Image Format Converter')
    frame.SetSize((1100, 700))
    frame.Show()
    app.MainLoop()
