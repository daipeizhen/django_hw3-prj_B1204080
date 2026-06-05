"""飲食記錄相關的 Django ModelForm。"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import FoodRecord


class FoodRecordForm(forms.ModelForm):
    """飲食記錄的 ModelForm，包含資料驗證。"""

    class Meta:
        model = FoodRecord
        fields = ['food_date', 'food_name', 'calories', 'quantity', 'notes']
        labels = {
            'food_date': '飲食日期',
            'food_name': '食物名稱',
            'calories': '卡路里數',
            'quantity': '數量',
            'notes': '備註（選填）',
        }
        widgets = {
            'food_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'food_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入食物名稱',
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入卡路里數',
                'min': '1',
                'max': '10000',
            }),
            'quantity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例如：1 份、200g',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '備註（非必填）',
                'rows': 3,
            }),
        }

    def clean_food_date(self):
        """驗證飲食日期不能是未來的時間。"""
        food_date = self.cleaned_data.get('food_date')
        if food_date and food_date > timezone.now().date():
            raise forms.ValidationError('飲食日期不能是未來的日期')
        return food_date

    def clean_food_name(self):
        """驗證食物名稱不為空。"""
        food_name = self.cleaned_data.get('food_name')
        if not food_name or len(food_name.strip()) == 0:
            raise forms.ValidationError('食物名稱不能為空')
        return food_name

    def clean_calories(self):
        """驗證卡路里數為正整數。"""
        calories = self.cleaned_data.get('calories')
        if calories is None:
            raise forms.ValidationError('卡路里數不能為空')
        if calories <= 0:
            raise forms.ValidationError('卡路里數必須大於 0')
        if calories > 10000:
            raise forms.ValidationError('卡路里數過大（請輸入 0–10000）')
        return calories

    def clean_quantity(self):
        """驗證數量不為空。"""
        quantity = self.cleaned_data.get('quantity')
        if not quantity or len(quantity.strip()) == 0:
            raise forms.ValidationError('數量不能為空')
        return quantity


class UserRegistrationForm(UserCreationForm):
    """使用者註冊表單，基於 Django 內建的 UserCreationForm。"""

    email = forms.EmailField(
        required=True,
        label='電子郵件',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入電子郵件',
        }),
    )
    username = forms.CharField(
        label='使用者名稱',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入使用者名稱',
        }),
    )
    password1 = forms.CharField(
        label='密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入密碼',
        }),
    )
    password2 = forms.CharField(
        label='確認密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '請再次輸入密碼',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        """確保電子郵件唯一。"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('此電子郵件已被註冊')
        return email

    def save(self, commit=True):
        """保存使用者並設置電子郵件。"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
