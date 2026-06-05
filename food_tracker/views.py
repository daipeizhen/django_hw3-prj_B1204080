"""處理飲食記錄 Web 介面與 API 的各種 View 函式。"""

from django.shortcuts import render, redirect, get_object_or_404  # 常用輔助函式
from django.views.decorators.csrf import ensure_csrf_cookie  # CSRF 相關裝飾器
from django.contrib.auth import authenticate, login, logout  # 認證相關函式
from django.contrib.auth.decorators import login_required  # 登入檢查裝飾器
from django.contrib import messages  # 訊息框架，顯示一次性提示
from django.core.paginator import Paginator  # 分頁工具
from django.db.models import Sum  # 資料庫聚合函式
from django.views.decorators.http import require_POST  # 限制 POST 請求
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import FoodRecord  # 飲食紀錄資料模型
from .serializers import FoodEntrySerializer  # 飲食紀錄序列化器
from .forms import FoodRecordForm, UserRegistrationForm  # 表單


class FoodRecordViewSet(viewsets.ModelViewSet):
    """RESTful 飲食紀錄 API：支援 list/create/retrieve/update/delete。"""

    serializer_class = FoodEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """普通使用者只能操作自己的紀錄，管理員可看全部。"""
        if self.request.user.is_superuser:
            return FoodRecord.objects.all()
        return FoodRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """新增紀錄時自動綁定目前登入者。"""
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def food_summary_api(request):
    """回傳目前使用者的飲食紀錄摘要 JSON。"""
    records_qs = FoodRecord.objects.all() if request.user.is_superuser else FoodRecord.objects.filter(user=request.user)
    return Response({
        'record_count': records_qs.count(),
        'total_calories': records_qs.aggregate(Sum('calories'))['calories__sum'] or 0,
    })


def register(request):
    """使用者註冊頁面。"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 註冊成功後自動登入
            login(request, user)
            messages.success(request, f'歡迎 {user.username}！註冊成功，已自動登入。')
            return redirect('food_tracker:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    """使用者登入頁面。"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'歡迎回來，{user.username}！')
            return redirect('food_tracker:home')
        else:
            messages.error(request, '使用者名稱或密碼錯誤，請重試。')
    return render(request, 'login.html')


@login_required(login_url='food_tracker:login')
def user_logout(request):
    """使用者登出。"""
    logout(request)
    messages.success(request, '您已成功登出。')
    return redirect('food_tracker:home')


def home(request):
    """首頁：顯示簡單介紹或導引到新增與查詢頁面。"""
    # 直接渲染 home.html 模板
    return render(request, 'home.html')


@ensure_csrf_cookie
@login_required(login_url='food_tracker:login')
def api_tools_page(request):
    """API 操作網頁：讓使用者直接測試 GET/POST/DELETE。"""
    return render(request, 'api_tools.html')


@ensure_csrf_cookie # 確保瀏覽器有 CSRF Cookie，讓前端 JavaScript 可以安全地呼叫 API
@login_required(login_url='food_tracker:login')
def add_food_page(request):
    """顯示新增飲食紀錄的頁面，並確保瀏覽器有 CSRF Cookie。"""
    if request.method == 'POST':
        form = FoodRecordForm(request.POST)
        if form.is_valid():
            food_record = form.save(commit=False)
            food_record.user = request.user  # 自動設置使用者為目前登入的使用者
            food_record.save()
            messages.success(request, '飲食記錄新增成功！')
            return redirect('food_tracker:history')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = FoodRecordForm()
    return render(request, 'add_food.html', {'form': form})


@login_required(login_url='food_tracker:login')
def history_records(request):
    """查詢飲食紀錄的頁面，含資料表與分頁功能。"""
    # 只取得目前登入使用者的飲食紀錄
    records_qs = FoodRecord.objects.filter(user=request.user)
    # 計算目前使用者全部紀錄的總卡路里數
    total_calories = records_qs.aggregate(Sum('calories'))['calories__sum'] or 0
    # 使用 Django 的 Paginator，每頁顯示 10 筆
    paginator = Paginator(records_qs, 10)
    # 從查詢字串取得目前頁碼，例如 ?page=2；若未提供則自動為第 1 頁
    page_number = request.GET.get('page')
    # 取得分頁物件（會自動處理不合法的頁碼）
    page_obj = paginator.get_page(page_number)
    # 將當頁資料、分頁物件與總卡路里數傳給模板
    return render(
        request,
        'history.html',
        {
            'records': page_obj.object_list,
            'page_obj': page_obj,
            'total_calories': total_calories,
        },
    )


@require_POST
@login_required(login_url='food_tracker:login')
def delete_record(request, pk: int):
    """刪除指定主鍵 pk 的飲食紀錄。只允許 POST 請求。"""
    # 若找不到該主鍵會自動回傳 404
    rec = get_object_or_404(FoodRecord, pk=pk)
    
    # 檢查權限：只有所有者和超級使用者可以刪除
    if rec.user != request.user and not request.user.is_superuser:
        messages.error(request, '您沒有權限刪除此記錄。')
        return redirect('food_tracker:history')
    
    # 刪除該筆紀錄
    rec.delete()
    messages.success(request, '記錄已成功刪除。')
    # 刪除後重新導回查詢頁面
    return redirect('food_tracker:history')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_add_food(request):
    """保留舊版 POST /api/add-food/，內部改由 DRF serializer 回傳 JSON。"""
    serializer = FoodEntrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
