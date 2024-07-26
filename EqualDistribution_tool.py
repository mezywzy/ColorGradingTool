from PIL import Image
import numpy as np

from PIL import Image, ImageOps
import numpy as np

def process_image(input_path, output_path, grayscale=False, gradation=256):
    # 打开图片
    image = Image.open(input_path)
    
    # 如果需要，转为灰度图像
    if grayscale:
        image = ImageOps.grayscale(image)

    # 获取图像像素值
    pixels = np.array(image)
    
    # 将像素值映射到指定的色阶
    if gradation < 256:
        factor = 256 // gradation
        pixels = (pixels // factor) * factor
    
    # 创建新的图片并保存
    new_image = Image.fromarray(pixels)
    new_image.save(output_path, format='PNG')