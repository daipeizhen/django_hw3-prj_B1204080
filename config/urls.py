"""專案層級 URL 設定。

這裡只負責：
1. 後台管理站台路徑 /admin/
2. 其餘所有路徑交給 food_tracker 應用處理
"""

from django.contrib import admin  # Django 內建後台
from django.urls import path, include  # path 用來註冊路由，include 可匯入其他 app 的 urls


urlpatterns = [
    # 後台管理介面網址，例如 http://127.0.0.1:8000/admin/
    path('admin/', admin.site.urls),
    # 將根路徑底下的所有網址交給 food_tracker/urls.py 處理
    path('', include('food_tracker.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
