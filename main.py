import StatisticalDistribution_tool
import EqualDistribution_tool
import sys

def main(input_path):
    print("This a demo for image processing")
    # 示例用法
    if input_path == '':
        input_path = 'orange.png'  # 输入图片路径
    output_path1 = 'output1.png'  # 输出图片路径
    output_path2 = 'output2.png'  # 输出图片路径
    output_path3 = 'output3.png'  # 输出图片路径
    StatisticalDistribution_tool.process_image(input_path, output_path1, grayscale=False, gradation=3)
    EqualDistribution_tool.process_image(input_path, output_path2, grayscale=False, gradation=3)
    StatisticalDistribution_tool.adjust_contrast(output_path1, 3,output_path3)
    print("Done, please check the output images")

if __name__ == "__main__":
    # 获取命令行参数
    if len(sys.argv) <2:
        print("Parameter error")
        sys.exit(1)
    
    arg1 = sys.argv[1]
    
    main(arg1)