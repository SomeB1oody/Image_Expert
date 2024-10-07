#Author: Stan Yin
#GitHub Name: SomeB1oody
#This project is based on CC 4.0 BY, please mention my name if you use it.
#This project requires opencv and wxWidgets.
import cv2
import wx

global img, x ,y, w, h

def crop(input_image, _x, _y, _w, _h):
    process_ = input_image.copy()
    # 确保矩形框的边界在图像内
    if _x + _w > input_image.shape[1]:
        _w = input_image.shape[1] - _x
    if _y + _h > input_image.shape[0]:
        _h = input_image.shape[0] - _y
    cv2.rectangle(process_, (_x, _y), (_x+_w, _y+_h), (0, 0, 255), 1)
    cv2.imshow("Crop", process_)

def load_image(path):
    global img
    if not path:
        wx.MessageBox("Please enter image path", "Error", wx.OK | wx.ICON_ERROR)
        return
    img = cv2.imread(path)
    if img is None:
        wx.MessageBox('Could not load the image', 'Error', wx.OK | wx.ICON_ERROR)
        return

class CropPlanter(wx.Frame):
    def __init__(self, *args, **kw):
        super(CropPlanter, self).__init__(*args, **kw)

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
        #裁剪
        crop_button = wx.Button(panel, label="Crop")
        crop_button.Bind(wx.EVT_BUTTON, self._crop_)
        vbox.Add(crop_button, flag=wx.ALL, border=5)
        # 转换按钮
        convert_button = wx.Button(panel, label="Convert")
        convert_button.Bind(wx.EVT_BUTTON, self.on_convert)
        vbox.Add(convert_button, flag=wx.ALL, border=5)

        # 设置面板的布局管理器
        panel.SetSizer(vbox)

        # 触发布局更新
        panel.Layout()

    def _crop_(self, event):
        load_image(self.input_path.GetValue())
        global x, y ,w ,h, img
        x = img.shape[1] // 2
        y = img.shape[0] // 2
        w = img.shape[1] // 3
        h = img.shape[0] // 3
        def x_track_bar(x_):
            global x, y, w, h
            x = x_
            crop(img, x, y, w, h)
        def y_track_bar(y_):
            global x, y, w, h
            y = y_
            crop(img, x, y, w, h)
        def h_track_bar(h_):
            global x, y, w, h
            h = h_
            crop(img, x, y, w, h)
        def w_track_bar(w_):
            global x, y, h, w
            w = w_
            crop(img, x, y, w, h)
        cv2.namedWindow("Crop")
        cv2.createTrackbar("X", "Crop", x, img.shape[1], x_track_bar)
        cv2.createTrackbar("Y", "Crop", y, img.shape[0], y_track_bar)
        cv2.createTrackbar("Width", "Crop", w, img.shape[1], w_track_bar)
        cv2.createTrackbar("Height", "Crop", h, img.shape[0], h_track_bar)

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
        #裁剪
        cropped_img = img[y:y + h, x:x + w]
        # 确定输出路径
        output_ = f"{save_path}{save_name}{selected_format}"
        # 保存输出图片
        try:
            cv2.imwrite(output_, cropped_img)
            wx.MessageBox(f'Image saved as {output_}', 'Success',
                          wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)

if __name__ == "__main__":
    app = wx.App()
    frame = CropPlanter(None)
    frame.SetTitle('Crop Planter')
    frame.SetSize((700, 500))
    frame.Show()
    app.MainLoop()
