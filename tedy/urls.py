"""tedy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from pan import views as pan_views
from django.conf.urls import handler404, handler500, handler403

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^web/file/list$', pan_views.file_list, name='file_list'),
    url(r'^web/file/upload$', pan_views.file_upload, name='file_upload'),
    url(r'^web/file/test$', pan_views.test, name='file_test'),
]

handler403 = pan_views.error_page_403
handler404 = pan_views.error_page_404
handler500 = pan_views.error_page_500
