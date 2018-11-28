from django.db import models

# Create your models here.


class TedyUser(models.Model):
    userName = models.CharField(max_length=10)
    nickName = models.CharField(max_length=30, null=True)
    createTime = models.DateTimeField(auto_now_add=True)
    modifyTime = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField()
    deletedTime = models.DateTimeField(null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=11)


class FileInfo(models.Model):
    fileName = models.CharField(max_length=60)
    createTime = models.DateTimeField(auto_now_add=True)
    modifyTime = models.DateTimeField(null=True)
    deleted = models.BooleanField()
    fileSize = models.CharField(max_length=15, null=True)
    path = models.CharField(max_length=255, null=True)
    owner = models.ForeignKey(TedyUser)
    category = models.CharField(max_length=10)

