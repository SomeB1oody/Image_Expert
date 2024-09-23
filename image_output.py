import wx
import cv2


class ImageConverter(wx.Frame):
    def __init__(self, *args, **kw):
        super(ImageConverter, self).__init__(*args, **kw)

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        # 输入图片路径
        vbox.Add(wx.StaticText(panel, label="Input image path:"), flag=wx.ALL, border=5)
        self.input_path = wx.TextCtrl(panel)
        self.output_name = wx.TextCtrl(panel)

        # 输出格式单选框
        self.output_format = wx.RadioBox(
            panel, label="Choose output format:", choices=[
                '.jpg', '.jpeg', '.png', '.tiff',
                '.tif', '.bmp', '.ppm', '.pgm', '.pbm', '.webp'
            ]
        )

        # 转换按钮
        convert_button = wx.Button(panel, label="Convert")
        convert_button.Bind(wx.EVT_BUTTON, self.on_convert)

        # 布局
        vbox.Add(self.input_path, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(wx.StaticText(panel, label="Output image name and path:"), flag=wx.ALL, border=5)
        vbox.Add(self.output_name, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.output_format, flag=wx.ALL, border=5)
        vbox.Add(convert_button, flag=wx.ALL, border=5)

        panel.SetSizer(vbox)

    def on_convert(self, event):
        input_path = self.input_path.GetValue()
        output_name = self.output_name.GetValue()
        selected_format = self.output_format.GetStringSelection()

        if not input_path or not output_name:
            wx.MessageBox('Please provide both input path and output name.', 'Error', wx.OK | wx.ICON_ERROR)
            return

        # 确定输出路径
        output_path = f"{output_name}{selected_format}"

        # 读取输入图片
        try:
            img = cv2.imread(input_path)
            if img is None:
                raise ValueError("Image not found or could not be opened.")
        except Exception as e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)
            return

        # 保存输出图片
        try:
            cv2.imwrite(output_path, img)
            wx.MessageBox(f'Image converted and saved as {output_path}', 'Success', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)


if __name__ == "__main__":
    app = wx.App()
    frame = ImageConverter(None)
    frame.SetTitle('Image Format Converter')
    frame.SetSize((400, 300))
    frame.Show()
    app.MainLoop()
