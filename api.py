import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import datetime
import uuid
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# 配置文件上传路径
app.config['FILE_ROOT'] = 'files'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER_1'] = 'results_1'
app.config['RESULT_FOLDER_2'] = 'results_2'
app.config['RESULT_FOLDER_3'] = 'results_3'

def generate_file_name(ext):
    return f"{uuid.uuid4().hex}.{ext}"

# =============== 上传图片接口 ===============

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# 检查文件扩展名
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 创建文件夹
def create_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

# 上传图片接口
@app.route('/upload', methods=['POST'])
def upload_file():
    '''
    上传图片接口
    :param file: 图片文件
    :return: {'file_path': 'uploads/2024-07-01/xxx.png'}
    '''
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = generate_file_name(ext)
        date_folder = datetime.datetime.now().strftime('%Y-%m-%d')
        save_folder = os.path.join(app.config['FILE_ROOT'], app.config['UPLOAD_FOLDER'], date_folder)
        create_folder_if_not_exists(save_folder)
        file.save(os.path.join(save_folder, unique_filename))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], date_folder, unique_filename)
        return jsonify({'file_path': file_path}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

# =============== 下载图片接口 ===============
import io
import zipfile
from flask import send_file

@app.route('/download', methods=['POST'])
def download_files():
    '''
    下载文件接口
    :param file_path_list: 文件路径列表
    :return: 文件流，单个文件直接下载，多个文件压缩成 zip 包下载
    '''
    file_path_list = request.json.get('file_path_list', [])
    
    if not file_path_list:
        return jsonify({'error': 'No file paths provided'}), 400
    
    # 给每个文件路径加上文件根目录
    file_path_list = [os.path.join(app.config['FILE_ROOT'], path) for path in file_path_list]
    
    if len(file_path_list) == 1:
        file_path = file_path_list[0]
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': f'File {file_path} does not exist'}), 404
    else:
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for file_path in file_path_list:
                if os.path.exists(file_path):
                    zf.write(file_path, os.path.basename(file_path))
                else:
                    return jsonify({'error': f'File {file_path} does not exist'}), 404
        
        memory_file.seek(0)
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='files.zip')


# =============== 图片处理接口 ===============
import StatisticalDistribution_tool
import EqualDistribution_tool

# 图像处理接口的公共部分
def process_image(request, result_folder, process_func):
    file_path = request.form.get('file_path')
    if not file_path:
        return jsonify({'error': 'file_path is required'}), 400
    input_path = os.path.join(app.config['FILE_ROOT'], file_path)
    if not os.path.exists(input_path):
        return jsonify({'error': 'file not found'}), 404
    gradation = request.form.get('gradation', 3)
    grayscale = request.form.get('grayscale', 0)
    # 随机生成输出文件名
    output_name = generate_file_name('png')
    date_folder = datetime.datetime.now().strftime('%Y-%m-%d')
    save_folder = os.path.join(app.config['FILE_ROOT'], result_folder, date_folder)
    create_folder_if_not_exists(save_folder)
    output_path = os.path.join(save_folder, output_name)
    try:
        process_func(input_path, output_path, grayscale=bool(int(grayscale)), gradation=int(gradation))
        file_path = os.path.join(result_folder, date_folder, output_name)
        return jsonify({'file_path': file_path}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal error'}), 500

# 平均分阶处理
@app.route('/equal_distribution', methods=['POST'])
def equal_distribution():
    '''
    平均分阶处理
    :param file_path: 文件路径
    :param gradation: 分阶数
    :param grayscale: 是否灰度化, 1: 灰度化, 0: 不灰度化
    :return: {'file_path': 'results/xxx.png'}
    '''
    return process_image(request, app.config['RESULT_FOLDER_1'], EqualDistribution_tool.process_image)

# 根据统计分布处理图像分阶
@app.route('/statistical_distribution', methods=['POST'])
def statistical_distribution():
    '''
    根据统计分布处理图像分阶
    :param file_path: 文件名
    :param gradation: 分阶数
    :param grayscale: 是否灰度化, 1: 灰度化, 0: 不灰度化
    :return: {'file_path': 'results/xxx.png'}
    '''
    return process_image(request, app.config['RESULT_FOLDER_2'], StatisticalDistribution_tool.process_image)

# 调整对比度
@app.route('/adjust_contrast', methods=['POST'])
def adjust_contrast():
    '''
    调整对比度
    :param file_path: 文件路径
    :param contrast: 对比度因子（大于 1 增加对比度，小于 1 降低对比度）
    :return: {'filename': 'xxx.png'}
    '''
    file_path = request.form.get('file_path')
    if not file_path:
        return jsonify({'error': 'file_path is required'}), 400
    input_path = os.path.join(app.config['FILE_ROOT'], file_path)
    if not os.path.exists(input_path):
        return jsonify({'error': 'file not found'}), 404
    contrast = request.form.get('contrast', 1)
    output_name = generate_file_name('png')
    date_folder = datetime.datetime.now().strftime('%Y-%m-%d')
    result_folder = app.config['RESULT_FOLDER_3']
    save_folder = os.path.join(app.config['FILE_ROOT'], result_folder, date_folder)
    create_folder_if_not_exists(save_folder)
    output_path = os.path.join(save_folder, output_name)
    try:
        StatisticalDistribution_tool.adjust_contrast(input_path, float(contrast), output_path)
        file_path = os.path.join(result_folder, date_folder, output_name)
        return jsonify({'file_path': file_path}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal error'}), 500
    


# =============== 定时清理图片 ===============

CLEANUP_INTERVAL_HOURS = 2
DELETE_BEFORE_HOURS = 2

# 定时清理图片
def delete_old_files(folder, hours):
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(hours=hours)
    
    for root, dirs, files in os.walk(folder):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            dir_name = os.path.basename(dir_path)
            try:
                dir_date = datetime.datetime.strptime(dir_name, '%Y-%m-%d').date()
                if dir_date < cutoff.date():
                    for file in os.listdir(dir_path):
                        os.remove(os.path.join(dir_path, file))
                    os.rmdir(dir_path)
                elif dir_date == cutoff.date():
                    for file in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, file)
                        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff:
                            os.remove(file_path)
                    if not os.listdir(dir_path):  # 如果文件夹为空，则删除文件夹
                        os.rmdir(dir_path)
            except ValueError:
                continue

def batch_delete_old_files(hours):
    folder = app.config['FILE_ROOT']
    # 遍历根目录下的一级文件夹
    for dir in os.listdir(folder):
        dir_path = os.path.join(folder, dir)
        if os.path.isdir(dir_path):
            delete_old_files(dir_path, hours)

# 执行定时清理任务
def scheduled_cleanup():
    batch_delete_old_files(DELETE_BEFORE_HOURS)

# 配置定时任务，每两小时执行一次
scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_cleanup, trigger="interval", hours=CLEANUP_INTERVAL_HOURS)
scheduler.start()

# 调试清理API
# @app.route('/debug-cleanup', methods=['POST'])
# def debug_cleanup():
#     hours = request.form.get('hours', DELETE_BEFORE_HOURS)
#     batch_delete_old_files(int(hours))
#     return jsonify({'status': 'Cleanup executed'}), 200

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
