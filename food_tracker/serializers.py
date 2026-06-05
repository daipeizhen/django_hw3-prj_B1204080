"""REST API 使用的序列化與驗證邏輯。"""

from rest_framework import serializers  # DRF 提供的序列化與驗證工具
from .models import FoodRecord  # 匯入飲食紀錄模型


class FoodEntrySerializer(serializers.ModelSerializer):
    """用於建立與驗證飲食紀錄的序列化器。"""

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        """序列化器的設定。"""
        model = FoodRecord
        fields = ['id', 'user', 'food_date', 'food_name', 'calories', 'quantity', 'notes', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_food_name(self, value):
        """驗證食物名稱不為空且長度合理。"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError('食物名稱不能為空')
        if len(value) > 100:
            raise serializers.ValidationError('食物名稱最多 100 個字')
        return value

    def validate_calories(self, value):
        """驗證卡洛里數為正整數。"""
        if value <= 0:
            raise serializers.ValidationError('卡洛里數必須大於 0')
        if value > 10000:
            raise serializers.ValidationError('卡洛里數过大（請輸入 0–10000）')
        return value

    def validate_quantity(self, value):
        """驗證數量不為空。"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError('數量不能為空')
        return value
