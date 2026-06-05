"""Django Admin 後台的客製化設定。"""

from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from .models import FoodRecord


class CalorieRangeFilter(admin.SimpleListFilter):
    """自訂卡路里範圍過濾器。"""
    title = '卡路里範圍'
    parameter_name = 'calorie_range'

    def lookups(self, request, model_admin):
        """定義卡路里範圍選項。"""
        return (
            ('low', '低熱量 (< 200 kcal)'),
            ('medium', '中熱量 (200 - 500 kcal)'),
            ('high', '高熱量 (> 500 kcal)'),
        )

    def queryset(self, request, queryset):
        """根據選擇過濾查詢集。"""
        if self.value() == 'low':
            return queryset.filter(calories__lt=200)
        if self.value() == 'medium':
            return queryset.filter(calories__gte=200, calories__lte=500)
        if self.value() == 'high':
            return queryset.filter(calories__gt=500)
        return queryset


@admin.register(FoodRecord)
class FoodRecordAdmin(admin.ModelAdmin):
    """FoodRecord 模型的後台管理介面。"""

    # 列表顯示的欄位（包含自訂方法顯示卡路里級別）
    list_display = (
        'id',
        'user',
        'food_date',
        'food_name',
        'calories_display',
        'quantity',
        'created_at_short'
    )

    # 可搜尋的欄位
    search_fields = ('user__username', 'food_name', 'notes', 'quantity')

    # 可過濾的欄位（包括自訂的卡路里範圍過濾）
    list_filter = ('food_date', 'created_at', 'user', CalorieRangeFilter)

    # 每頁顯示的記錄數
    list_per_page = 20

    # 按日期由新到舊排序
    ordering = ('-food_date', '-created_at')

    # 只讀欄位
    readonly_fields = ('created_at', 'calories_info')

    # 日期層次瀏覽（按食物日期分層）
    date_hierarchy = 'food_date'

    # 分組顯示的欄位
    fieldsets = (
        ('用戶信息', {
            'fields': ('user',)
        }),
        ('飲食信息', {
            'fields': ('food_date', 'food_name', 'calories', 'quantity', 'calories_info')
        }),
        ('額外信息', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """過濾查詢集，普通使用者只能看到自己的記錄。"""
        qs = super().get_queryset(request)
        # 超級使用者可以看到所有記錄
        if request.user.is_superuser:
            return qs
        # 普通使用者只能看到自己的記錄
        return qs.filter(user=request.user)

    def calories_display(self, obj):
        """以不同顏色顯示卡路里數值。"""
        if obj.calories < 200:
            color = 'green'
            level = '低'
        elif obj.calories <= 500:
            color = 'orange'
            level = '中'
        else:
            color = 'red'
            level = '高'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} kcal ({})</span>',
            color, obj.calories, level
        )
    calories_display.short_description = '卡路里'

    def created_at_short(self, obj):
        """簡化顯示建立時間。"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_short.short_description = '建立時間'

    def calories_info(self, obj):
        """在詳細檢視中顯示卡路里資訊。"""
        if obj.calories < 200:
            info = f'{obj.calories} kcal - 低熱量飲食'
        elif obj.calories <= 500:
            info = f'{obj.calories} kcal - 中等熱量飲食'
        else:
            info = f'{obj.calories} kcal - 高熱量飲食'
        return format_html('<strong>{}</strong>', info)
    calories_info.short_description = '卡路里分類'

    def save_model(self, request, obj, form, change):
        """保存時自動設置使用者為目前登入的使用者。"""
        if not change:  # 新建記錄
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        """普通使用者只能刪除自己的記錄。"""
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.user == request.user

    def has_change_permission(self, request, obj=None):
        """普通使用者只能編輯自己的記錄。"""
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.user == request.user
