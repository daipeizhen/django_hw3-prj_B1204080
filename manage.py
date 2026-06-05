"""Django 專案的指令列入口程式。

執行方式範例：
    python manage.py runserver
    python manage.py migrate
       
开启Admin 後台：
    http://127.0.0.1:8000/admin/
    預設帳號：dpz1001
    电子邮件：chen999153@gmail.com
    預設密碼：123
"""

#!/usr/bin/env python
import os  # 作業系統相關功能（環境變數等）
import sys  # 存取命令列參數 sys.argv


def main() -> None:
    """設定 Django 環境並轉交給官方的指令處理函式。"""
    # 若未設定 DJANGO_SETTINGS_MODULE，預設使用 config.settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    # 從 Django 載入執行指令列命令的主函式
    from django.core.management import execute_from_command_line
    # 將命令列參數轉交給 Django 處理
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # 當此檔案被直接執行時，呼叫 main() 進入程式
    main()
