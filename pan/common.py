from pan.models import TedyUser, FileInfo
from django.http import JsonResponse
import os
import time
import datetime
import filetype


def mkdir(path):
    if os.path.exists(path):
        return u'目录存在'
    else:
        os.makedirs(path)


def get_timestamp(str_time):
    t = str_time.timetuple()
    return time.mktime(t)


def get_best_size(size_of_bytes):
    for (cutoff, label) in [(1024*1024*1024, "GB"), (1024*1024, "MB"), (1024, "KB")]:
        if size_of_bytes >= cutoff:
            return "%.1f %s" % (size_of_bytes * 1.0 / cutoff, label)
    # if size_of_bytes == 1:
    #     return "1 byte"
    # else:
    #     bytes = "%.1f" % (size_of_bytes or 0,)
    #     return (bytes[:-2] if bytes.endswith('.0') else bytes) + ' bytes'
    return "%d bytes" % size_of_bytes


def save_file(file_path, file):
    write_file = open(file_path, "wb+")
    for chunk in file.chunks():
        write_file.write(chunk)
    write_file.close()
    return 0


def get_dir_size(dir_path):
    size_sum = 0
    for root, dirs, files in os.walk(dir_path):
        size_sum += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size_sum


# 将时间戳转换成字符串日期格式
def timestamp_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")


def get_file_type(file_path):
    file_type = filetype.guess(file_path)
    image_list = ["png", "jpg", "jpeg", "gif", "bmp", "ico"]
    video_list = ["mp4", "m4v", "avi", "flv", "mpg"]
    if file_type is None:
        return "file"
    elif file_type.extension in image_list:
        return "picture"
    elif file_type.extension in video_list:
        return "video"
    else:
        return "file"


def get_error_msg(error_code=""):
    error_msg = {"status": "ERROR", "errMsg": error_code, "content": ""}
    return error_msg

