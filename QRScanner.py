#Author: Stan Yin
#GitHub Name: SomeB1oody
#This project is based on CC 4.0 BY, please mention my name if you use it.
#This project requires opencv and wxWidgets.
import cv2
import wx

def cv2_to_wx_image(cv_img):
    # OpenCV 图像是 BGR 形式的，先将其转换为 RGB
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

    # 获取图像的尺寸（高度、宽度、通道数）
    height, width = cv_img_rgb.shape[:2]

    # 将 NumPy 数组转换为 wx.Image
    wx_img = wx.Image(width, height)

    # 将 NumPy 数据复制到 wx.Image
    wx_img.SetData(cv_img_rgb.tobytes())

    return wx_img


class QRDecoder(wx.Frame):
    def __init__(self, *args, **kw):
        super(QRDecoder, self).__init__(*args, **kw)

        panel = wx.Panel(self)

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # 输入图片路径
        self.vbox.Add(wx.StaticText(panel, label="Input image path:"), flag=wx.ALL, border=5)
        self.vbox.Add(wx.StaticText(panel, label="Example:C:\\Wallpaper\\02.png"), flag=wx.ALL, border=5)
        self.input_path = wx.TextCtrl(panel)
        self.vbox.Add(self.input_path, flag=wx.EXPAND | wx.ALL, border=5)
        # 解码按钮
        self.decode_button = wx.Button(panel, label="Decode")
        self.decode_button.Bind(wx.EVT_BUTTON, self.on_decode_button)
        self.vbox.Add(self.decode_button, flag=wx.ALL, border=5)
        # 解码内容
        self.result_text = wx.StaticText(panel, label="Click \"Decode\" first to get QR text.")
        self.vbox.Add(self.result_text, flag=wx.ALL, border=5)
        # 展示图片
        empty_image = wx.Image(300, 300)  # 创建一个空白的 wx.Image
        empty_image.Replace(0, 0, 0, 255, 255, 255)  # 将所有像素设为白色
        empty_bitmap = wx.Bitmap(empty_image)  # 将 wx.Image 转换为 wx.Bitmap
        self.img_show = wx.StaticBitmap(panel, bitmap=empty_bitmap)
        self.vbox.Add(self.img_show, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        # 设置面板的布局管理器
        panel.SetSizer(self.vbox)
        panel.Layout()

    def on_decode_button(self, event):
        path = self.input_path.GetValue()
        if not path:
            wx.MessageBox("Please enter image path.", "Error", wx.OK | wx.ICON_ERROR)
            return
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if img is None:
            wx.MessageBox("Cannot load image.", "Error", wx.OK | wx.ICON_ERROR)
            return
        qr_text, points, straight_qrcode = cv2.QRCodeDetector.detectAndDecode(img_gray)
        if straight_qrcode is None:
            wx.MessageBox("Cannot find QR code.", "Error", wx.OK | wx.ICON_ERROR)
            return
        else:
            self.result_text.SetLabel(f"QR text is: {qr_text}")
            # 带mask的图片
            try:
                img_mask = img.copy()
                for index in range(4):
                    cv2.circle(img_mask, points[index], 3, (0, 0, 255), -1)
                cv2.polylines(img_mask, points, True, (0, 255, 0))
                img_ = cv2_to_wx_image(img_mask)
                width_ = img_.GetWidth() * (300 // img_.GetHeight())
                img_ = img_.Scale(width_, 300, wx.IMAGE_QUALITY_HIGH)
                bitmap = wx.Bitmap(img_)
                self.img_show.SetBitmap(bitmap)
            except Exception as e:
                wx.MessageBox(f"Fail to show image: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            self.Refresh()


if __name__ == "__main__":
    app = wx.App()
    frame = QRDecoder(None)
    frame.SetTitle('SimilarityFinder')
    frame.SetSize((500, 450))
    frame.Show()
    app.MainLoop()