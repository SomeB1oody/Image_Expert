import cv2
import numpy as np
from pyzbar import pyzbar

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

def detect_barcode(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 使用高斯模糊来减少噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 使用Sobel算子来计算图像的梯度
    gradX = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradY = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)

    # 计算梯度的绝对值，并相减以突出条形码的竖直部分
    gradient = cv2.subtract(gradX, gradY)
    gradient = cv2.convertScaleAbs(gradient)

    # 对梯度图像进行模糊和二值化处理
    blurred = cv2.GaussianBlur(gradient, (9, 9), 0)
    _, thresh = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)

    # 使用形态学操作关闭小的黑点并突出条形码区域
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # 对图像进行腐蚀和膨胀操作
    closed = cv2.erode(closed, None, iterations=4)
    closed = cv2.dilate(closed, None, iterations=4)

    # 找到轮廓
    contours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 如果找到任何轮廓，筛选出面积最大的轮廓
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)

        # 获取轮廓的边界框
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.array(box, dtype="int")

        # 对边界框点进行排序
        box = order_points(box)

        # 透视变换矫正图像
        warped = four_point_transform(image, box)

        # 使用 pyzbar 解码条形码
        barcodes = pyzbar.decode(warped)

        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type
            print(f"找到条形码： 类型={barcode_type}, 数据={barcode_data}")
            return warped, barcode_data

    return None, None

# 用户输入示例
if __name__ == "__main__":
    # 加载图像
    image_path = input("请输入图像文件路径：")
    image = cv2.imread(image_path)

    # 检测条形码
    warped_image, barcode_data = detect_barcode(image)

    if warped_image is not None:
        # 显示矫正后的条形码图像
        cv2.imshow("Warped Barcode", warped_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("未检测到条形码。")