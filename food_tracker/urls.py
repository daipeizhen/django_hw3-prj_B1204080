"""food_tracker 應用的 URL 設定。"""

from django.urls import include, path  # 用來定義 URL 與 view 的對應關係
from rest_framework.routers import DefaultRouter
from . import views  # 匯入同資料夾底下的 views 模組

# 設定 URL 反向解析用的命名空間，例如 {% url 'food_tracker:home' %}
app_name = 'food_tracker'

router = DefaultRouter()
router.register('records', views.FoodRecordViewSet, basename='food-record')


urlpatterns = [
    # 身份認證相關
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # 飲食記錄相關
    # 首頁：顯示說明或導引按鈕
    path('', views.home, name='home'),
    # 新增飲食紀錄的表單與結果頁面（使用 ModelForm）
    path('add/', views.add_food_page, name='add'),
    # 查詢飲食紀錄歷史（表格 + 分頁）
    path('history/', views.history_records, name='history'),
    # 刪除單筆紀錄，使用主鍵 pk
    path('records/<int:pk>/delete/', views.delete_record, name='delete'),
    # 提供前端 AJAX 呼叫的飲食新增 API（回傳 JSON）
    path('api/add-food/', views.api_add_food, name='api_add_food'),
    path('api/summary/', views.food_summary_api, name='food_summary_api'),
    path('api/', include(router.urls)),
]
