from django.shortcuts import render
from pan.models import TedyUser, FileInfo
from django.http import HttpResponse, StreamingHttpResponse, FileResponse, JsonResponse
import json
import time
import logging
import django.utils.log
import logging.handlers
from pan.common import *
from tedy.settings import FILE_STORE_PATH, TOTAL_CAP

mkdir(FILE_STORE_PATH)
logger = logging.getLogger("tedy.pan.views")
# Create your views here.


def test(request):
    return render(request, 'test.html')


def error_page_403(request):
    return JsonResponse({"status": "ERROR", "errMsg": "没有权限", "content": ""})


def error_page_404(request):
    return JsonResponse({"status": "ERROR", "errMsg": "该页面不存在", "content": ""})


def error_page_500(request):
    return JsonResponse({"status": "ERROR", "errMsg": "服务器内部错误", "content": ""})


def file_list(request):
    # 前端传入 user_id,path两个参数
    rev_json = json.loads(request.body)
    user_id = rev_json["user_id"]
    path = rev_json["fileDir"]
    phone = TedyUser.objects.get(id=user_id).phone
    dir_list_path = os.path.join(FILE_STORE_PATH, phone, path)
    # print(dir_list_path)
    if not os.path.isdir(dir_list_path):
        response_msg = get_error_msg("目录不存在")
        logger.info(response_msg)
        logger.info({"path": dir_list_path})
        return JsonResponse(response_msg)
    return_file_list = []
    response_msg = {"status": "OK", "errMsg": ""}
    for item in os.listdir(dir_list_path):
        file_to_list = os.path.join(dir_list_path, item)
        m_time = int(os.path.getmtime(file_to_list))
        if os.path.isfile(file_to_list):
            file_size = get_best_size(os.path.getsize(file_to_list))
            category = get_file_type(file_to_list)
            file_info = {"fileName": item, "size": file_size, "modifyTime": m_time, "category": category}
            return_file_list.append(file_info)
        else:
            file_info = {"fileName": item, "size": "", "modifyTime": m_time, "category": "directory"}
            return_file_list.append(file_info)
    response_msg["content"] = return_file_list
    logger.info(response_msg)
    return JsonResponse(response_msg)


def file_upload(request):
    user_id = request.POST.get('user_id')
    path = request.POST.get('fileDir')
    phone = TedyUser.objects.get(id=user_id).phone
    my_files = request.FILES.getlist('my_file', None)
    store_path = os.path.join(FILE_STORE_PATH, phone, path)
    # 判断目录是否存在
    if not os.path.exists(store_path):
        return JsonResponse(get_error_msg("目录不存在"))
    for upload_file in my_files:
        write_file_path = os.path.join(store_path, upload_file.name)
        # 写入文件之前判断文件是否存在，不存在则返回错误
        if os.path.exists(write_file_path):
            return JsonResponse(get_error_msg("文件已存在"))
        # 判断容量是否足够
        used_cap = get_dir_size(os.path.join(FILE_STORE_PATH, phone))
        if int(used_cap) + upload_file.size > TOTAL_CAP:
            return JsonResponse(get_error_msg("容量不足"))
        # 保存文件 save_file为文件写入函数
        save_file(write_file_path, upload_file)
        modifyTime = timestamp_datetime(os.path.getmtime(write_file_path))  # 获取文件时间戳并转换成字符串格式
        createTime = timestamp_datetime(os.path.getctime(write_file_path))
        fileSize = get_best_size(upload_file.size)
        # 获取上传文件信息
        file_info = {"fileSize": fileSize, "fileName": upload_file.name, "path": path, "modifyTime": str(modifyTime),
                     "owner_id": user_id, "createTime": str(createTime)}
        # # content.append(file_info)
        category = get_file_type(write_file_path)
        file_info["category"] = category
        # # 将文件信息写入数据库
        # FileInfo.objects.create(**file_info, deleted=0, category=category)
        logger.info(file_info)
    response_msg = {"status": "OK", "errMsg": "", "content": ""}
    return JsonResponse(response_msg)


def file_new_dir(request):
    rev_json = json.loads(request.body)
    user_id = rev_json["user_id"]
    path = rev_json["fileDir"]
    newDir = rev_json["newDir"]
    phone = TedyUser.objects.get(id=user_id).phone
    new_dir_path = os.path.join(FILE_STORE_PATH, phone, path, newDir)
    try:
        os.mkdir(new_dir_path)
        modifyTime = timestamp_datetime(os.path.getmtime(new_dir_path))  # 获取文件时间戳并转换成字符串格式
        createTime = timestamp_datetime(os.path.getctime(new_dir_path))
        # 获取修改后文件信息
        file_info = {"fileSize": 0, "fileName": newDir, "path": path, "modifyTime": str(modifyTime),
                     "owner_id": user_id, "createTime": str(createTime)}
        # 将修改后文件信息更新至数据库
        # FileInfo.objects.create(**file_info, deleted=0, category="directory")
        logger.info(file_info)
    except FileNotFoundError:
        logger.info({"path": new_dir_path})
        return JsonResponse(get_error_msg("路径不存在"))
    except FileExistsError:
        logger.info({"path": new_dir_path})
        return JsonResponse(get_error_msg("目录已存在"))
    response_msg = {"status": "OK", "errMsg": "", "content": ""}
    return JsonResponse(response_msg)


def file_re_name(request):
    rev_json = json.loads(request.body)
    user_id = rev_json["user_id"]
    path = rev_json["fileDir"]
    reNameFile = rev_json["reNameFile"]  # 源文件名
    newName = rev_json["newName"]  # 目标文件名
    phone = TedyUser.objects.get(id=user_id).phone
    src_file_name = os.path.join(FILE_STORE_PATH, phone, path, reNameFile)
    dst_file_name = os.path.join(FILE_STORE_PATH, phone, path, newName)
    logger.info({"src_file_name": src_file_name, "dst_file_name": dst_file_name})
    try:
        # 重命名文件
        os.rename(src_file_name, dst_file_name)
        # modifyTime = timestamp_datetime(os.path.getmtime(dst_file_name))
        # file_info = {"fileName": newName, "path": path, "modifyTime": str(modifyTime)}
        # src_file_filter = {"fileName": reNameFile, "path": path, "owner_id": user_id}
        # FileInfo.objects.filter(**src_file_filter).update(**file_info)
    except FileNotFoundError:
        logger.info(get_error_msg("源文件不存在"))
        return JsonResponse(get_error_msg("源文件不存在"))
    except FileExistsError:
        logger.info(get_error_msg("目标文件已存在"))
        return JsonResponse(get_error_msg("目标文件已存在"))
    response_msg = {"status": "OK", "errMsg": "", "content": ""}
    return JsonResponse(response_msg)

