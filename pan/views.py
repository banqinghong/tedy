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
    logger = logging.getLogger("tedy.pan.views")
    # 前端传入 user_id,path两个参数
    rev_json = json.loads(request.body)
    user_id = rev_json["user_id"]
    path = rev_json["fileDir"]
    # phone = TedyUser.objects.get(id=user_id).phone
    query_filed = {"path": path, "owner_id": user_id}
    values_list = ("fileName", "fileSize", "modifyTime", "category")
    content = FileInfo.objects.filter(**query_filed).values_list(*values_list)
    if not content:
        response_msg = {"content": "", "status": "ERROR", "errMsg": "目录不存在"}
        logger.info(response_msg)
        return JsonResponse(response_msg)
    return_file_list = []
    response_msg = {"status": "OK", "errMsg": ""}
    for item in content:
        modify_time = get_timestamp(item[2])
        file_info = {"fileName": item[0], "modifyTime": modify_time, "size": item[1], "category": item[3]}
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
        return JsonResponse({"status": "ERROR", "errMsg": "目录不存在", "content": ""})
    for upload_file in my_files:
        write_file_path = os.path.join(store_path, upload_file.name)
        # 写入文件之前判断文件是否存在，不存在则返回错误
        if os.path.exists(write_file_path):
            return JsonResponse({"status": "ERROR", "errMsg": "文件已存在", "content": ""})
        # 判断容量是否足够
        used_cap = get_dir_size(os.path.join(FILE_STORE_PATH, phone))
        if int(used_cap) + upload_file.size > TOTAL_CAP:
            return JsonResponse({"status": "ERROR", "errMsg": "容量不足", "content": ""})
        # 保存文件 save_file为文件写入函数
        save_file(write_file_path, upload_file)
        modifyTime = timestamp_datetime(os.path.getmtime(write_file_path))
        createTime = timestamp_datetime(os.path.getctime(write_file_path))
        fileSize = get_best_size(upload_file.size)
        # 获取上传文件信息
        file_info = {"fileSize": fileSize, "fileName": upload_file.name, "path": path, "modifyTime": str(modifyTime),
                     "owner_id": user_id, "createTime": str(createTime)}
        # # content.append(file_info)
        category = get_file_type(write_file_path)
        # 将文件信息写入数据库
        FileInfo.objects.create(**file_info, deleted=0, category=category)
    response_msg = {"status": "OK", "errMsg": "", "content": ""}
    return JsonResponse(response_msg)
