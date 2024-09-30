/*Author: Stan Yin
* GitHub Name: SomeB1oody
* This project is based on CC 4.0 BY, please mention my name if you use it.
* This project requires opencv.
*/
#include <wx/wx.h>
#include <wx/listbox.h>
#include <wx/radiobox.h>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <map>
#include <string>

using namespace cv;   // 使用OpenCV的命名空间
using namespace std;  // 使用标准库的命名空间
using namespace wx;   // 使用wxWidgets的命名空间

// 全局变量
int alpha = 100, beta = 100, gammaValue = 100;
int x = 0, y = 0, w = 0, h = 0;
Mat img_without_crop, img;
string selected_color = "";

// 裁剪图像函数
void crop(Mat input_image, int _x, int _y, int _w, int _h) {
    Mat process_ = input_image.clone();
    if (_x + _w > input_image.cols) {
        _w = input_image.cols - _x;
    }
    if (_y + _h > input_image.rows) {
        _h = input_image.rows - _y;
    }
    rectangle(process_, Point(_x, _y), Point(_x + _w, _y + _h), Scalar(0, 0, 255), 1);
    imshow("Crop", process_);
}

// 亮度、对比度、伽马调整函数
Mat mix_for_crop(Mat input_image) {
    Mat process_;
    input_image.convertTo(process_, -1, alpha / 100.0, beta - 100);

    vector<uchar> lookUpTable(256);
    for (int i = 0; i < 256; i++) {
        lookUpTable[i] = saturate_cast<uchar>(pow(i / 255.0, gammaValue / 100.0) * 255.0);
    }

    Mat output;
    LUT(input_image, lookUpTable, output);
    return output;
}

// 适用于其他窗口的调整函数
void mix_for_others(Mat input_image, double _alpha_, double _beta_, double _gamma_, string window_name) {
    vector<uchar> lookUpTable(256);
    for (int i = 0; i < 256; i++) {
        lookUpTable[i] = saturate_cast<uchar>(pow(i / 255.0, _gamma_ / 100.0) * 255.0);
    }

    Mat arg1, arg2;
    LUT(input_image, lookUpTable, arg1);
    arg1.convertTo(arg2, -1, _alpha_, _beta_);
    imshow(window_name, arg2);
}

// 加载图像函数
bool load_image(string path, Mat &img) {
    if (path.empty()) {
        MessageBox("Please enter image path", "Error", wxOK | wxICON_ERROR);
        return false;
    }

    img = imread(path);
    if (img.empty()) {
        MessageBox("Could not load the image", "Error", wxOK | wxICON_ERROR);
        return false;
    }

    return true;
}

// ImageConverter 类定义
class ImageConverter : public wxFrame {
public:
    ImageConverter(const wxString& title);

private:
    // GUI组件
    wxTextCtrl* input_path;
    wxTextCtrl* output_name;
    wxTextCtrl* output_path;
    wxRadioBox* output_format;
    wxRadioBox* crop_choice;

    // 事件处理函数
    void brightness_and_contrast_adjustment(wxCommandEvent& event);
    void _gamma_correction_(wxCommandEvent& event);
    void _crop_(wxCommandEvent& event);
    void color_format_lb(wxCommandEvent& event);
    void on_convert(wxCommandEvent& event);
};

ImageConverter::ImageConverter(const wxString& title)
    : wxFrame(nullptr, wxID_ANY, title, wxDefaultPosition, wxSize(600, 600)) {

    wxPanel* panel = new wxPanel(this, wxID_ANY);

    wxBoxSizer* vbox = new wxBoxSizer(wxVERTICAL);

    // 输入图片路径
    vbox->Add(new wxStaticText(panel, wxID_ANY, "Input image path:"), 0, wxALL, 5);
    vbox->Add(new wxStaticText(panel, wxID_ANY, "Example: C:\\Wallpaper\\02.png"), 0, wxALL, 5);
    input_path = new wxTextCtrl(panel);
    vbox->Add(input_path, 0, wxEXPAND | wxALL, 5);

    // 输入图片输出名称
    vbox->Add(new wxStaticText(panel, wxID_ANY, "Output image name (no file suffix):"), 0, wxALL, 5);
    output_name = new wxTextCtrl(panel);
    vbox->Add(output_name, 0, wxEXPAND | wxALL, 5);

    // 输入图片输出位置
    vbox->Add(new wxStaticText(panel, wxID_ANY, "Output image path:"), 0, wxALL, 5);
    vbox->Add(new wxStaticText(panel, wxID_ANY, "Example: C:\\Wallpaper\\"), 0, wxALL, 5);
    output_path = new wxTextCtrl(panel);
    vbox->Add(output_path, 0, wxEXPAND | wxALL, 5);

    // 输出格式单选框
    wxString formats[] = { ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".ppm", ".pgm", ".pbm", ".webp" };
    output_format = new wxRadioBox(panel, wxID_ANY, "Choose output format:", wxDefaultPosition, wxDefaultSize, WXSIZEOF(formats), formats);
    vbox->Add(output_format, 0, wxALL, 5);

    // 亮度与对比度调整按钮
    wxButton* brightness_button = new wxButton(panel, wxID_ANY, "Contrast and Brightness Adjustment");
    vbox->Add(new wxStaticText(panel, wxID_ANY, "Close the window that pops out to save change in these button down HERE:"), 0, wxALL, 5);
    brightness_button->Bind(wxEVT_BUTTON, &ImageConverter::brightness_and_contrast_adjustment, this);
    vbox->Add(brightness_button, 0, wxALL, 5);

    // 伽马纠正按钮
    wxButton* gamma_button = new wxButton(panel, wxID_ANY, "Gamma Correction");
    gamma_button->Bind(wxEVT_BUTTON, &ImageConverter::_gamma_correction_, this);
    vbox->Add(gamma_button, 0, wxALL, 5);

    // 裁剪按钮
    wxButton* crop_button = new wxButton(panel, wxID_ANY, "Crop");
    crop_button->Bind(wxEVT_BUTTON, &ImageConverter::_crop_, this);
    vbox->Add(crop_button, 0, wxALL, 5);

    // 裁剪选项单选框
    wxString crop_choices[] = { "No crop", "Save crop" };
    crop_choice = new wxRadioBox(panel, wxID_ANY, "Crop", wxDefaultPosition, wxDefaultSize, WXSIZEOF(crop_choices), crop_choices);
    vbox->Add(crop_choice, 0, wxALL, 1);

    // 色彩格式列表框
    vbox->Add(new wxStaticText(panel, wxID_ANY, "Please choose a color format"), 0, wxALL, 5);
    wxString color_format_list[] = { "Same", "BGR(555)", "BGR(565)", "RGB", "GRAY", "HSV", "HSV(Full)", "HLS", "HLS(Full)", "YUV", "YUV(4:2:0)", "YUV(4:2:2)", "LAB" };
    wxListBox* lb = new wxListBox(panel, wxID_ANY, wxDefaultPosition, wxDefaultSize, WXSIZEOF(color_format_list), color_format_list, wxLB_SINGLE);
    lb->Bind(wxEVT_LISTBOX, &ImageConverter::color_format_lb, this);
    vbox->Add(lb, 0, wxALL, 5);

    // 转换按钮
    wxButton* convert_button = new wxButton(panel, wxID_ANY, "Convert");
    convert_button->Bind(wxEVT_BUTTON, &ImageConverter::on_convert, this);
    vbox->Add(convert_button, 0, wxALL, 5);

    // 设置面板的布局管理器
    panel->SetSizer(vbox);

    // 触发布局更新
    panel->Layout();
}

// 亮度与对比度调整函数
void ImageConverter::brightness_and_contrast_adjustment(wxCommandEvent& event) {
    load_image(std::string(input_path->GetValue().mb_str()), img);

    auto alpha_track_bar = [](int alpha_) {
        alpha = alpha_;
        mix_for_others(img, alpha / 100.0, beta - 100, gammaValue / 100.0, "Brightness and Contrast");
    };

    auto beta_track_bar = [](int beta_) {
        beta = beta_;
        mix_for_others(img, alpha / 100.0, beta - 100, gammaValue / 100.0, "Brightness and Contrast");
    };

    namedWindow("Brightness and Contrast", WINDOW_AUTOSIZE);
    createTrackbar("Contrast", "Brightness and Contrast", &alpha, 200, alpha_track_bar);
    createTrackbar("Brightness", "Brightness and Contrast", &beta, 200, beta_track_bar);
}

// 伽马校正函数
void ImageConverter::_gamma_correction_(wxCommandEvent& event) {
    load_image(std::string(input_path->GetValue().mb_str()), img);

    auto gamma_track_bar = [](int _gamma) {
        gammaValue = _gamma;
        mix_for_others(img, alpha / 100.0, beta - 100, gammaValue / 100.0, "Gamma Correction");
    };

    namedWindow("Gamma Correction", WINDOW_AUTOSIZE);
    createTrackbar("Gamma", "Gamma Correction", &gammaValue, 200, gamma_track_bar);
}

// 裁剪功能
void ImageConverter::_crop_(wxCommandEvent& event) {
    load_image(std::string(input_path->GetValue().mb_str()), img);

    img_without_crop = mix_for_crop(img);
    x = img_without_crop.cols / 2;
    y = img_without_crop.rows / 2;
    w = img_without_crop.cols / 3;
    h = img_without_crop.rows / 3;

    auto x_track_bar = [](int x_) { crop(img_without_crop, x_, y, w, h); };
    auto y_track_bar = [](int y_) { crop(img_without_crop, x, y_, w, h); };
    auto w_track_bar = [](int w_) { crop(img_without_crop, x, y, w_, h); };
    auto h_track_bar = [](int h_) { crop(img_without_crop, x, y, w, h_); };

    namedWindow("Crop", WINDOW_AUTOSIZE);
    createTrackbar("X", "Crop", &x, img_without_crop.cols, x_track_bar);
    createTrackbar("Y", "Crop", &y, img_without_crop.rows, y_track_bar);
    createTrackbar("Width", "Crop", &w, img_without_crop.cols, w_track_bar);
    createTrackbar("Height", "Crop", &h, img_without_crop.rows, h_track_bar);
}

// 色彩格式选择
void ImageConverter::color_format_lb(wxCommandEvent& event) {
    selected_color = event.GetString().ToStdString();
    if (selected_color == "Same") {
        selected_color = "";
    }
}

// 转换功能
void ImageConverter::on_convert(wxCommandEvent& event) {
    load_image(std::string(input_path->GetValue().mb_str()), img);
    std::string save_path = std::string(output_path->GetValue().mb_str());
    std::string save_name = std::string(output_name->GetValue().mb_str());

    if (save_path.empty() || save_name.empty()) {
        wxMessageBox("Please enter output path and name", "Error", wxOK | wxICON_ERROR);
        return;
    }

    std::string selected_format = output_format->GetStringSelection().ToStdString();

    Mat cropped_img = (crop_choice->GetStringSelection() != "No crop") ? img(Rect(x, y, w, h)) : img;
    Mat mixed_img = mix_for_crop(cropped_img);

    std::map<std::string, int> color_format_dict = {
        {"BGR(555)", COLOR_BGR2BGR555}, {"BGR(565)", COLOR_BGR2BGR565}, {"RGB", COLOR_BGR2RGB},
        {"GRAY", COLOR_BGR2GRAY}, {"HSV", COLOR_BGR2HSV}, {"HSV(Full)", COLOR_BGR2HSV_FULL},
        {"HLS", COLOR_BGR2HLS}, {"HLS(Full)", COLOR_BGR2HLS_FULL}, {"YUV", COLOR_BGR2YUV},
        {"YUV(4:2:0)", COLOR_BGR2YUV_I420}, {"YUV(4:2:2)", COLOR_BGR2YUV_Y422}, {"LAB", COLOR_BGR2LAB}
    };

    Mat output_img = (!selected_color.empty()) ? cvtColor(mixed_img, color_format_dict[selected_color]) : mixed_img;

    std::string output_ = save_path + save_name + selected_format;

    try {
        imwrite(output_, output_img);
        wxMessageBox("Image saved as " + output_, "Success", wxOK | wxICON_INFORMATION);
    } catch (const std::exception& e) {
        wxMessageBox(e.what(), "Error", wxOK | wxICON_ERROR);
    }
}

// 主函数启动应用
class MyApp : public wxApp {
public:
    virtual bool OnInit();
};

wxIMPLEMENT_APP(MyApp);

bool MyApp::OnInit() {
    // 创建 ImageConverter 窗口实例
    ImageConverter* frame = new ImageConverter("Image Format Converter");

    // 设置窗口大小
    frame->SetSize(wxSize(1100, 700));

    // 显示窗口
    frame->Show(true);

    return true;
}

