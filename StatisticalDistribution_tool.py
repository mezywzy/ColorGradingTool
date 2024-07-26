from PIL import Image, ImageEnhance
import numpy as np
import numpy as np

def segment_histogram_average(hist, bins, cdf, g):
    # 总样本数
    total_samples = cdf[-1]

    # 每段应该拥有的样本数（取整）
    samples_per_segment = total_samples // g

    # 初始化段的平均值数组
    segment_averages = []

    # 初始化段样本计数和样本值累加器
    segment_sample_count = 0
    segment_value_sum = 0

    # 记录第几段
    segment_index = 0
    current_segment_start = 0

    # 遍历每个 bin
    for i in range(len(hist)):
        # 当前 bin 中的样本数
        bin_sample_count = hist[i]

        # 如果当前段样本数加上当前 bin 的样本数超过了每段的预期样本数
        while segment_sample_count + bin_sample_count > samples_per_segment:
            # 计算当前段还差多少样本可以达到预期样本数
            remaining_samples = samples_per_segment - segment_sample_count

            # 当前段累加来自 bin 的样本值
            segment_value_sum += bins[i] * remaining_samples

            # 计算当前段的平均值并保存
            segment_averages.append(segment_value_sum / samples_per_segment)

            # 更新当前 bin 样本计数，减少已被当前段使用的样本数
            bin_sample_count -= remaining_samples

            # 重置段样本计数和样本值累加器，开始新的一段
            segment_sample_count = 0
            segment_value_sum = 0

            # 更新段索引
            segment_index += 1

            # 更新当前段的起始位置
            current_segment_start = i

        # 当前 bin 的样本数不足以填满新的段，累加到当前段
        segment_sample_count += bin_sample_count
        segment_value_sum += bins[i] * bin_sample_count

    # 如果还有剩余的段没有满，计算剩余样本的平均值
    if segment_sample_count > 0:
        segment_averages.append(segment_value_sum / segment_sample_count)
    return segment_averages

def histogram_equalization(channel, gradation):
    # 计算通道的直方图
    hist, bins = np.histogram(channel.flatten(), bins=256, range=[0, 256])
    
    # 计算累积分布函数（CDF）
    cdf = hist.cumsum()
    #得到分段的平均值
    segment_averages = segment_histogram_average(hist, bins, cdf, gradation)
    
    # 将结果转换为图像的形状
    adjusted_channel = np.zeros_like(channel) 
    # 使用 nditer 遍历二维数组
    for idx, value in np.ndenumerate(channel):
        if value < segment_averages[0]:
            adjusted_channel[idx] = segment_averages[0]
        elif value > segment_averages[-1]:
            adjusted_channel[idx] = segment_averages[-1]
        else:
            for i in range(len(segment_averages) - 1):
                if segment_averages[i] <= value < segment_averages[i + 1]:
                    adjusted_channel[idx] = segment_averages[i]
                    break
    return adjusted_channel

def process_image(input_path, output_path, grayscale=False, gradation=256):
    # 打开图片
    image = Image.open(input_path)
    
    # 将图片转为RGB模式（如果不是的话）
    image = image.convert('RGB')
    
    # 拆分通道
    r, g, b = image.split()
    
    # 将通道转换为numpy数组
    r = np.array(r)
    g = np.array(g)
    b = np.array(b)
    
    # 可选的灰度处理
    if grayscale:
        gray = (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)
        r = gray
        g = gray
        b = gray
    
    # 对每个通道进行直方图均衡化
    r = histogram_equalization(r, gradation)
    g = histogram_equalization(g, gradation)
    b = histogram_equalization(b, gradation)
    
    # 将通道转换回图像
    r = Image.fromarray(r)
    g = Image.fromarray(g)
    b = Image.fromarray(b)
    
    # 合并通道
    new_image = Image.merge('RGB', (r, g, b))
    
    # 保存处理后的图像
    new_image.save(output_path, format='PNG')
def adjust_contrast(input_path, contrast, output_path):
    image = Image.open(input_path)
    image = image.convert('RGB')
    enhancer = ImageEnhance.Contrast(image)
    new_image = enhancer.enhance(contrast)
    new_image.save(output_path, format='PNG')

