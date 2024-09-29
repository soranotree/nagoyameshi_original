import random
from restaurant.models import Menu
from datetime import time

# Define the A and B choices based on the criteria
A_before_18 = ['日替わり', 'うどん', 'そば', 'ラーメン', 'パンケーキ', 'ランチ']
B_before_18 = ['定食', 'セット']

A_after_17_30 = ['ステーキ', 'しゃぶしゃぶ', '鍋', '刺身', 'ハンバーグ', 'フレンチ', 'イタリアン', 'ブイヤベース', 'うなぎ', 'ラム', '和牛', 'ソーセージ', 'バーベキュー']
B_after_17_30 = ['セット', 'コース', '御膳', 'フルコース']

A_others = ['カレー', 'パンケーキ', 'ショートケーキ', 'ポップコーン', 'おつまみ']
B_others = ['単品']

# Query to get all Menu records with id > 14
menus = Menu.objects.filter(id__gt=14)

for menu in menus:
    if menu.available_end < time(18, 0):
        # For those with available_end before 18:00
        new_name = f"{random.choice(A_before_18)}{random.choice(B_before_18)}"
    elif menu.available_from >= time(17, 30):
        # For those with available_from being 17:30 or later
        new_name = f"{random.choice(A_after_17_30)}{random.choice(B_after_17_30)}"
    else:
        # For all other records
        new_name = f"{random.choice(A_others)}{random.choice(B_others)}"
    
    # Update name and description
    menu.name = new_name
    menu.description = f"{new_name}をお楽しみください。"
    
    # Save the changes
    menu.save()

print(f"{menus.count()} records updated successfully!")
