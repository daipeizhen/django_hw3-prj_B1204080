"""與飲食紀錄相關的資料模型。"""

from django.db import models  # Django ORM 提供的模型基底類別
from django.contrib.auth.models import User  # Django 內建的使用者模型


class FoodRecord(models.Model):
    """儲存單次飲食紀錄的資料表。"""

    # 所有者（外鍵關聯到 Django User 模型）
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_records')
    # 紀錄建立時間，自動填入建立時間
    created_at = models.DateTimeField(auto_now_add=True)
    # 飲食日期（使用 DateField，只記錄日期）
    food_date = models.DateField()
    # 食物名稱（最多 100 字）
    food_name = models.CharField(max_length=100)
    # 卡洛里數（正整數）
    calories = models.PositiveIntegerField()
    # 數量（例如 1 份、200g）
    quantity = models.CharField(max_length=50)
    # 備註（選填）
    notes = models.TextField(blank=True, null=True)

    class Meta:
        """模型的額外設定。"""
        # 預設依飲食日期由新到舊排序
        ordering = ['-food_date', '-created_at']

    def __str__(self) -> str:
        """在後台或除錯時顯示紀錄內容的文字格式。"""
        return f'{self.food_date} | {self.food_name} ({self.quantity}) - {self.calories} kcal'
