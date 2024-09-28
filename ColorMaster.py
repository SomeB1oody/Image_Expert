import wx
import cv2 as cv

global input_format, output_format_basic, input_color_format_list_additional, input_format_additional
global output_color_format_list_basic
unchanged_list = []

translate_dict = {  # BGR
        'BGR to BGR555': cv.COLOR_BGR2BGR555,
        'BGR to BGR565': cv.COLOR_BGR2BGR565,
        'BGR to BGRA': cv.COLOR_BGR2BGRA,
        'BGR to RGBA': cv.COLOR_BGR2RGBA,
        'BGR to HSV': cv.COLOR_BGR2HSV,
        'BGR to HSV_Full': cv.COLOR_BGR2HSV_FULL,
        'BGR to HLS': cv.COLOR_BGR2HLS,
        'BGR to HLS_Full': cv.COLOR_BGR2HLS_FULL,
        'BGR to YUV_I420': cv.COLOR_BGR2YUV_I420,
        'BGR to YUV_YV12': cv.COLOR_BGR2YUV_YV12,
        'BGR to YUV_Y422': cv.COLOR_BGR2YUV_Y422,
        'BGR to YUV_UYNV': cv.COLOR_BGR2YUV_UYNV,
        'BGR to YUV_IYUV': cv.COLOR_BGR2YUV_IYUV,
        'BGR to YUV_UYVY': cv.COLOR_BGR2YUV_UYVY,
        'BGR to YUV_YUNV': cv.COLOR_BGR2YUV_YUNV,
        'BGR to YUV_YVY2': cv.COLOR_BGR2YUV_YUY2,
        'BGR to YUV_YVYU': cv.COLOR_BGR2YUV_YVYU,
        'BGR to YUV': cv.COLOR_BGR2YUV,
        'BGR to YCrCb': cv.COLOR_BGR2YCrCb,
        'BGR to GRAY': cv.COLOR_BGR2GRAY,
        # BGR555
        'BGR555 to BGR': cv.COLOR_BGR5552BGR,
        'BGR555 to RGB': cv.COLOR_BGR5552RGB,
        'BGR555 to BGRA': cv.COLOR_BGR5552BGRA,
        'BGR555 to GRAY': cv.COLOR_BGR5552GRAY,
        'BGR555 to RGBA': cv.COLOR_BGR5552RGBA,
        # BGR565
        'BGR565 to BGR': cv.COLOR_BGR5652BGR,
        'BGR565 to RGB': cv.COLOR_BGR5652RGB,
        'BGR565 to BGRA': cv.COLOR_BGR5652BGRA,
        'BGR565 to GRAY': cv.COLOR_BGR5652GRAY,
        'BGR565 to RGBA': cv.COLOR_BGR5652RGBA,
        # RGB
        'RGB to BGR': cv.COLOR_RGB2BGR,
        'RGB to BGR565': cv.COLOR_RGB2BGR565,
        'RGB to BGR555': cv.COLOR_RGB2BGR555,
        'RGB to BGRA': cv.COLOR_RGB2BGRA,
        'RGB to RGBA': cv.COLOR_RGB2RGBA,
        'RGB to HSV': cv.COLOR_RGB2HSV,
        'RGB to HSV_Full': cv.COLOR_RGB2HSV_FULL,
        'RGB to HLS': cv.COLOR_RGB2HLS,
        'RGB to HLS_Full': cv.COLOR_RGB2HLS_FULL,
        'RGB to YUV_I420': cv.COLOR_RGB2YUV_I420,
        'RGB to YUV_YV12': cv.COLOR_RGB2YUV_YV12,
        'RGB to YUV_Y422': cv.COLOR_RGB2YUV_Y422,
        'RGB to YUV_UYNV': cv.COLOR_RGB2YUV_UYNV,
        'RGB to YUV_IYUV': cv.COLOR_RGB2YUV_IYUV,
        'RGB to YUV_UYVY': cv.COLOR_RGB2YUV_UYVY,
        'RGB to YUV_YUNV': cv.COLOR_RGB2YUV_YUNV,
        'RGB to YUV_YUY2': cv.COLOR_RGB2YUV_YUY2,
        'RGB to YUV_YVYU': cv.COLOR_RGB2YUV_YVYU,
        'RGB to YUV': cv.COLOR_RGB2YUV,
        'RGB to YCrCb': cv.COLOR_RGB2YCrCb,
        'RGB to GRAY': cv.COLOR_RGB2GRAY,
        # BGRA
        'BGRA to BGR': cv.COLOR_BGRA2BGR,
        'BGRA to BGR565': cv.COLOR_BGRA2BGR565,
        'BGRA to BGR555': cv.COLOR_BGRA2BGR555,
        'BGRA to RGB': cv.COLOR_BGRA2RGB,
        'BGRA to RGBA': cv.COLOR_BGRA2RGBA,
        'BGRA to GRAY': cv.COLOR_BGRA2GRAY,
        'BGRA to YUV_I420': cv.COLOR_BGRA2YUV_I420,
        'BGRA to YUV_YV12': cv.COLOR_BGRA2YUV_YV12,
        'BGRA to YUV_Y422': cv.COLOR_BGRA2YUV_Y422,
        'BGRA to YUV_UYNV': cv.COLOR_BGRA2YUV_UYNV,
        'BGRA to YUV_IYUV': cv.COLOR_BGRA2YUV_IYUV,
        'BGRA to YUV_UYVY': cv.COLOR_BGRA2YUV_UYVY,
        'BGRA to YUV_YUNV': cv.COLOR_BGRA2YUV_YUNV,
        'BGRA to YUV_YUY2': cv.COLOR_BGRA2YUV_YUY2,
        'BGRA to YUV_YVYU': cv.COLOR_BGRA2YUV_YVYU,
        # RGBA
        'RGBA to BGR': cv.COLOR_BGRA2BGR,
        'RGBA to BGR555': cv.COLOR_BGRA2BGR555,
        'RGBA to BGR565': cv.COLOR_BGRA2BGR565,
        'RGBA to RGB': cv.COLOR_BGRA2RGB,
        'RGBA to BGRA': cv.COLOR_RGBA2BGRA,
        'RGBA to MRGBA': cv.COLOR_RGBA2mRGBA,
        'RGBA to GRAY': cv.COLOR_RGBA2GRAY,
        'RGBA to YUV_I420': cv.COLOR_RGBA2YUV_I420,
        'RGBA to YUV_YV12': cv.COLOR_RGBA2YUV_YV12,
        'RGBA to YUV_Y422': cv.COLOR_RGBA2YUV_Y422,
        'RGBA to YUV_UYNV': cv.COLOR_RGBA2YUV_UYNV,
        'RGBA to YUV_IYUV': cv.COLOR_RGBA2YUV_IYUV,
        'RGBA to YUV_UYVY': cv.COLOR_RGBA2YUV_UYVY,
        'RGBA to YUV_YUNV': cv.COLOR_RGBA2YUV_YUNV,
        'RGBA to YUV_YUY2': cv.COLOR_RGBA2YUV_YUY2,
        'RGBA to YUV_YVYU': cv.COLOR_RGBA2YUV_YVYU,
        # MRGBA
        'MRGBA to RGBA': cv.COLOR_M_RGBA2RGBA,
        # GRAY
        'GRAY to BGR': cv.COLOR_GRAY2BGR,
        'GRAY to BGR555': cv.COLOR_GRAY2BGR555,
        'GRAY to BGR565': cv.COLOR_GRAY2BGR565,
        'GRAY to RGB': cv.COLOR_GRAY2RGB,
        'GRAY to BGRA': cv.COLOR_GRAY2BGRA,
        'GRAY to RGBA': cv.COLOR_GRAY2RGBA,
        # HSV
        'HSV to BGR': cv.COLOR_HSV2BGR,
        'HSV to RGB': cv.COLOR_HSV2RGB,
        # HSV_Full
        'HSV_Full to BGR': cv.COLOR_HSV2BGR_FULL,
        'HSV_Full to RGB': cv.COLOR_HSV2RGB_FULL,
        # HLS
        'HLS to BGR': cv.COLOR_HLS2BGR,
        'HLS to RGB': cv.COLOR_HLS2RGB,
        # HSV_Full
        'HLS_Full to BGR': cv.COLOR_HLS2BGR_FULL,
        'HLS_Full to RGB': cv.COLOR_HLS2RGB_FULL,
        # YUV
        'YUV to BGR': cv.COLOR_YUV2BGR,
        'YUV_I420 to BGR': cv.COLOR_YUV2BGR_I420,
        'YUV_YV12 to BGR': cv.COLOR_YUV2BGR_YV12,
        'YUV_Y422 to BGR': cv.COLOR_YUV2BGR_Y422,
        'YUV_UYNV to BGR': cv.COLOR_YUV2BGR_UYNV,
        'YUV_IYUV to BGR': cv.COLOR_YUV2BGR_IYUV,
        'YUV_UYVY to BGR': cv.COLOR_YUV2BGR_UYVY,
        'YUV_YUNV to BGR': cv.COLOR_YUV2BGR_YUNV,
        'YUV_YUY2 to BGR': cv.COLOR_YUV2BGR_YUY2,
        'YUV_YVYU to BGR': cv.COLOR_YUV2BGR_YVYU,
        'YUV to RGB': cv.COLOR_YUV2RGB,
        'YUV_I420 to RGB': cv.COLOR_YUV2RGB_I420,
        'YUV_YV12 to RGB': cv.COLOR_YUV2RGB_YV12,
        'YUV_Y422 to RGB': cv.COLOR_YUV2RGB_Y422,
        'YUV_UYNV to RGB': cv.COLOR_YUV2RGB_UYNV,
        'YUV_IYUV to RGB': cv.COLOR_YUV2RGB_IYUV,
        'YUV_UYVY to RGB': cv.COLOR_YUV2RGB_UYVY,
        'YUV_YUNV to RGB': cv.COLOR_YUV2RGB_YUNV,
        'YUV_YUY2 to RGB': cv.COLOR_YUV2RGB_YUY2,
        'YUV_YVYU to RGB': cv.COLOR_YUV2RGB_YVYU,
        'YUV_I420 to RGBA': cv.COLOR_YUV2RGBA_I420,
        'YUV_YV12 to RGBA': cv.COLOR_YUV2RGBA_YV12,
        'YUV_Y422 to RGBA': cv.COLOR_YUV2RGBA_Y422,
        'YUV_UYNV to RGBA': cv.COLOR_YUV2RGBA_UYNV,
        'YUV_IYUV to RGBA': cv.COLOR_YUV2RGBA_IYUV,
        'YUV_UYVY to RGBA': cv.COLOR_YUV2RGBA_UYVY,
        'YUV_YUNV to RGBA': cv.COLOR_YUV2RGBA_YUNV,
        'YUV_YUY2 to RGBA': cv.COLOR_YUV2RGBA_YUY2,
        'YUV_YVYU to RGBA': cv.COLOR_YUV2RGBA_YVYU,
        'YUV_I420 to BGRA': cv.COLOR_YUV2BGRA_I420,
        'YUV_YV12 to BGRA': cv.COLOR_YUV2BGRA_YV12,
        'YUV_Y422 to BGRA': cv.COLOR_YUV2BGRA_Y422,
        'YUV_UYNV to BGRA': cv.COLOR_YUV2BGRA_UYNV,
        'YUV_IYUV to BGRA': cv.COLOR_YUV2BGRA_IYUV,
        'YUV_UYVY to BGRA': cv.COLOR_YUV2BGRA_UYVY,
        'YUV_YUNV to BGRA': cv.COLOR_YUV2BGRA_YUNV,
        'YUV_YUY2 to BGRA': cv.COLOR_YUV2BGRA_YUY2,
        'YUV_YVYU to BGRA': cv.COLOR_YUV2BGRA_YVYU,
        # YCrCb
        'YCrCb to BGR': cv.COLOR_YCrCb2BGR,
        'YCrCb to RGB': cv.COLOR_YCrCb2RGB
}

format_dict = {
        'BGR(888)': 'BGR',
        'BGR(555)': 'BGR555',
        'BGR(565)': 'BGR565',
        'BGRA': 'BGRA',
        'RGB': 'RGB',
        'RGBA': 'RGBA',
        'M_RGBA': 'MRGBA',
        'HSV': 'HSV',
        'HSV(Full Range)': 'HSV_Full',
        'HLS(Full Range)': 'HLS_Full',
        '4:2:0 I420': 'YUV_I420',
        '4:2:0 YV12': 'YUV_YV12',
        '4:2:2 Y422': 'YUV_Y422',
        '4:2:2 UYNV': 'YUV_UYNV',
        '4:4:4': 'YUV',
        '4:2:0 IYUV': 'YUV_IYUV',
        '4:2:2 UYVY': 'YUV_UYVY',
        'YUNV': 'YUV_YUNV',
        '4:2:2 YUY2': 'YUV_YUY2',
        '4:2:2 YVYU': 'YUV_YVYU',
        'YCrCb':'YCrCb',
        'GrayScale': 'GRAY'
}

class ColorMaster(wx.Frame):
    def __init__(self, *args, **kw):
        super(ColorMaster, self).__init__(*args, **kw)

        panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        global input_color_format_list_additional, output_color_format_list_basic

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

        # 输入色彩选择框
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox.Add(wx.StaticText(panel, label=
        "Please choose an input color format"), flag=wx.ALL, border=5)
        input_color_format_list = ['BGR', 'BGRA', 'RGB', 'RGBA', 'M_RGBA', 'HSV', 'HLS', 'YUV', 'YCrCb', 'GrayScale']
        self.lb_input = wx.ListBox(panel, choices=input_color_format_list, style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.color_format_lb_input, self.lb_input)
        hbox1.Add(self.lb_input, flag=wx.EXPAND | wx.ALL, border=5)

        # 拓展输入色彩格式选择框
        input_color_format_list_additional = []
        self.lb_related_input = wx.ListBox(panel, choices=input_color_format_list_additional, style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.color_format_input_additional, self.lb_related_input)
        hbox1.Add(self.lb_related_input, flag=wx.EXPAND | wx.ALL, border=5)

        # 添加水平布局（两个选择框）到垂直布局中
        self.vbox.Add(hbox1, flag=wx.EXPAND | wx.ALL, border=5)

        # 是否先进行转换（初始化时显示，但不提供选择）
        self.if_accept_trans = wx.RadioBox(
            panel, label="Accept translate to BGR(888) first", choices=[
                'No', 'Yes'
            ]
        )
        self.if_accept_trans.Show()  # 初始化时显示
        self.if_accept_trans.Enable(False)  # 禁用选择
        self.Bind(wx.EVT_RADIOBOX, self.update_output_format, self.if_accept_trans)  # 绑定事件
        self.vbox.Add(self.if_accept_trans, flag=wx.ALL, border=5)

        self.warning_text = wx.StaticText(panel, label="No loss of image information")
        self.vbox.Add(self.warning_text, flag=wx.ALL, border=5)

        # 输出色彩选择框和新的选择框
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.vbox.Add(wx.StaticText(panel, label=
        "Please choose a color format for output"), flag=wx.ALL, border=5)
        output_color_format_list_basic = []
        self.lb_output = wx.ListBox(panel, choices= output_color_format_list_basic, style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.color_format_lb_output, self.lb_output)
        hbox2.Add(self.lb_output, flag=wx.EXPAND | wx.ALL, border=5)

        # 拓展选择框
        self.lb_additional_output = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE)
        hbox2.Add(self.lb_additional_output, flag=wx.EXPAND | wx.ALL, border=5)

        # 将水平布局（两个选择框）添加到垂直布局中
        self.vbox.Add(hbox2, flag=wx.EXPAND | wx.ALL, border=5)

        # 转换按钮
        self.convert_button = wx.Button(panel, label="Convert")
        self.convert_button.Bind(wx.EVT_BUTTON, self.on_convert)
        self.vbox.Add(self.convert_button, flag=wx.ALL, border=5)

        # 设置面板的布局管理器
        panel.SetSizer(self.vbox)
        panel.Layout()

    def color_format_lb_input(self, event):
        global input_format, input_color_format_list_additional
        input_format = event.GetEventObject().GetStringSelection()

        # 如果选择的是BGR，更新拓展输入格式选择框
        if input_format == 'BGR':   input_color_format_list_additional = ['BGR(888)', 'BGR(555)', 'BGR(565)']
        elif input_format == 'BGRA':    input_color_format_list_additional = ['BGRA']
        elif input_format == 'RGB':     input_color_format_list_additional = ['RGB']
        elif input_format == 'M_RGBA':    input_color_format_list_additional = ['M_RGBA']
        elif input_format == 'RGBA':    input_color_format_list_additional = ['RGBA']
        elif input_format == 'HSV':     input_color_format_list_additional = ['HSV', 'HSV(Full Range)']
        elif input_format == 'HLS':     input_color_format_list_additional = ['HLS', 'HLS(Full Range)']
        elif input_format == 'YUV':
            input_color_format_list_additional = [
                '4:2:0', '4:2:0 I420', '4:2:0 NV12', '4:2:0 NV21', '4:2:0 YV12','4:2:0 Planar',
                '4:2:0 SP', '4:2:2 Y422', '4:2:2 UYNV', '4:4:4'
            ]
        elif input_format == 'YCrCb':   input_color_format_list_additional = ['YCrCb']
        elif input_format == 'Grayscale':   input_color_format_list_additional = ['Grayscale']
        else:   input_color_format_list_additional = []
        self.lb_related_input.Set(input_color_format_list_additional)

        # 更新输出色彩格式列表
        self.update_output_format(None)

    def update_output_format(self, event):
        global input_color_format_list_additional, output_color_format_list_basic, unchanged_list
        if input_format == 'RGB':
            self.if_accept_trans.Enable(False)  # 禁用选择
            self.if_accept_trans.SetSelection(0)  # 重置选择为 'No'
            self.warning_text.SetLabel("No loss of image information")
        else:
            self.if_accept_trans.Enable(True)  # 启用选择
            self.warning_text.SetLabel(
                "Attention: Translating to BGR first has more choices on output color format, but there is a loss of image information")
        # 如果选择了“先转换”，可以添加更多输出格式
        if self.if_accept_trans.GetStringSelection() == 'Yes':
            output_color_format_list_basic = [
                'BGR', 'BGRA','RGB', 'RGBA', 'GrayScale', 'HSV', 'HLS', 'YUV', 'LAB', 'YCrCb'
            ]
        else:
            output_color_format_list_basic = unchanged_list
        self.lb_output.Set(output_color_format_list_basic)

    def color_format_input_additional(self, event):
        global input_format_additional, output_color_format_list_basic, unchanged_list
        input_format_additional = event.GetEventObject().GetStringSelection()
        additional_format_list = [
            '4:2:0 I420', '4:2:0 YV12', '4:2:0 IYUV', '4:2:2 Y422', '4:2:2 UYNV', '4:2:2 YUY2', '4:2:2 YVYU',
            '4:2:2 YVYU', '4:4:4', 'YUNV'
        ]
        # 根据输入色彩格式更新输出色彩格式列表
        if input_format_additional == 'BGR(888)':
            self.if_accept_trans.Enable(False)  # 禁用选择
            self.if_accept_trans.SetSelection(0)  # 重置选择为 'No'
            self.warning_text.SetLabel("No loss of image information")
            output_color_format_list_basic = [
                'BGR', 'BGRA', 'RGB', 'RGBA', 'GrayScale', 'HSV', 'HLS', 'YUV', 'LAB', 'YCrCb'
            ]
            self.lb_output.Set(output_color_format_list_basic)
        else:
            self.if_accept_trans.Enable(True)  # 启用选择
            self.warning_text.SetLabel(
                "Attention: Translating to BGR first has more choices on output color format, but there is a loss of image information")

            if input_format_additional == 'BGR(555)' or input_format_additional == 'BGR(565)':
                output_color_format_list_basic = ['BGR', 'RGB', 'BGRA', 'RGBA', 'GrayScale']
            elif input_format_additional == 'BGRA':
                output_color_format_list_basic = ['BGR', 'RGB', 'GrayScale', 'RGBA', 'YUV']
            elif input_format_additional == 'RGB':
                output_color_format_list_basic = ['BGR', 'RGB', 'GrayScale', 'HSV', 'HLS', 'YUV', 'LAB']
            elif input_format_additional == 'RGBA':
                output_color_format_list_basic = ['BGR', 'RGB', 'GrayScale', 'M_RGBA', 'YUV', 'BGRA']
            elif input_format_additional == 'M_RGBA':
                output_color_format_list_basic = ['RGBA']
            elif input_format_additional == 'GrayScale':
                output_color_format_list_basic = ['BGR', 'RGB', 'BGRA', 'RGBA']
            elif input_format_additional == 'HSV' or input_format_additional == 'HSV(Full Range)':
                output_color_format_list_basic = ['BGR', 'RGB']
            elif input_format_additional == 'HLS' or input_format_additional == 'HLS(Full Range)':
                output_color_format_list_basic = ['BGR', 'RGB']
            elif input_format_additional in additional_format_list:
                output_color_format_list_basic = ['BGR', 'RGB', 'BGRA', 'RGBA', 'GrayScale']
                if input_format_additional == '4:4:4':
                    output_color_format_list_basic.remove('BGRA')
                    output_color_format_list_basic.remove('RGBA')
            elif input_format_additional == 'YCrCb':
                output_color_format_list_basic = ['BGR', 'RGB']
            else:
                output_color_format_list_basic = []
        self.lb_output.Set(output_color_format_list_basic)
        unchanged_list = output_color_format_list_basic


    def color_format_lb_output(self, event):
        global output_format_basic, input_format_additional
        output_format_basic = event.GetEventObject().GetStringSelection()

        # 根据左侧选择框的选择更新拓展选择框的内容
        if output_format_basic == 'BGR':    additional_format_list = ['BGR(888)', 'BGR(565)', 'BGR(555)']
        elif output_format_basic == 'RGB':  additional_format_list = ['RGB']
        elif output_format_basic == 'LAB':  additional_format_list = ['LAB']
        elif output_format_basic == 'HSV':  additional_format_list = ['HSV', 'HSV(Full Range)']
        elif output_format_basic == 'HLS':  additional_format_list = ['HLS', 'HLS(Full Range)']
        elif output_format_basic == 'RGBA': additional_format_list = ['RGBA']
        elif output_format_basic == 'M_RGBA': additional_format_list = ['M_RGBA']
        elif output_format_basic == 'BGRA': additional_format_list = ['BGRA']
        elif output_format_basic == 'YCrCb':additional_format_list = ['YCrCb']
        elif output_format_basic == 'YUV':
            additional_format_list = [
                '4:2:0 I420', '4:2:0 YV12', '4:2:0 IYUV', '4:2:2 Y422', '4:2:2 UYNV', '4:2:2 YUY2', '4:2:2 YVYU',
                '4:2:2 YVYU', '4:4:4', 'YUNV'
            ]
            if input_format_additional == 'RGBA': additional_format_list.remove('4:4:4')
            if input_format_additional == 'BGRA': additional_format_list.remove('4:4:4')
        elif output_format_basic == 'GrayScale':    additional_format_list = ['GrayScale']
        else:   additional_format_list = []
        if input_format_additional in additional_format_list:
            additional_format_list.remove(input_format_additional)
        # 更新拓展选择框
        self.lb_additional_output.Set(additional_format_list)

    def on_convert(self, event):
        # 获取用户输入
        global input_format, output_format_basic, input_format_additional
        selected_img_format = self.output_format.GetStringSelection()
        save_path = self.output_path.GetValue()
        save_name = self.output_name.GetValue()
        output_format_additional = self.lb_additional_output.GetStringSelection()
        if_accept_trans = self.if_accept_trans.GetSelection()
        input_path = self.input_path.GetValue()


        input_format_expression = format_dict[input_format_additional]
        output_format_expression = format_dict[output_format_additional]


        # 没有输入路径
        if not input_path:
            wx.MessageBox('Please enter input path and name', 'Error', wx.OK | wx.ICON_ERROR)
            return
        # 是否先转换
        if if_accept_trans == 'Yes':
            input_img = cv.imread(input_path, cv.IMREAD_COLOR)
            input_format_expression = format_dict['BGR']
        else:
            input_img = cv.imread(input_path, cv.IMREAD_UNCHANGED)
        # 是否读取成功
        if input_img is None:
            wx.MessageBox('Cannot load image', 'Error', wx.OK | wx.ICON_ERROR)
            return
        # 没有输出路径和名字
        if not save_path or not save_name:
            wx.MessageBox('Please enter output path and name', 'Error', wx.OK | wx.ICON_ERROR)
            return
        # 没有输入路径
        if not input_path:
            wx.MessageBox('Please enter input path and name','Error', wx.OK | wx.ICON_ERROR)
            return
        # 是否先转换
        if if_accept_trans == 'Yes':    input_img = cv.imread(input_path, cv.IMREAD_COLOR)
        else:   input_img = cv.imread(input_path, cv.IMREAD_UNCHANGED)
        # 是否读取成功
        if input_img is None:
            wx.MessageBox('Cannot load image', 'Error', wx.OK | wx.ICON_ERROR)
            return
        # 没有输出路径和名字
        if not save_path or not save_name:
            wx.MessageBox('Please enter output path and name','Error', wx.OK | wx.ICON_ERROR)
            return
        # 转换
        in_n_out = f'{input_format_expression} to {output_format_expression}'
        output_img = cv.cvtColor(input_img, translate_dict[in_n_out])

        # 确定输出路径
        output_ = f"{save_path}{save_name}{selected_img_format}"

        # 保存图片
        cv.imwrite(output_, output_img)


if __name__ == "__main__":
    app = wx.App()
    frame = ColorMaster(None)
    frame.SetTitle('Image Format Converter')
    frame.SetSize((800, 800))
    frame.Show()
    app.MainLoop()