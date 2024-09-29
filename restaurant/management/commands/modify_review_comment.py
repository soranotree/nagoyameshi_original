from django.core.management.base import BaseCommand
import random
from restaurant.models import Review
from datetime import time


class Command(BaseCommand):
    help = 'Modify review comment'

    def handle(self, *args, **kwargs):
        # Define the choices
        A_part = ['訪問したのは確か', '振り返ればあれは', '思い起こせば', 'このお店に行ったのは', '通算で3回目になりますが、このレビューは初めて行った時のもので確か', '前回訪れたのは']
        B_part = ['初めてで多少の不安はありましたが、ネットの評判をみて迷うことなくここに決めました。', '雨を避けるようにこの店に飛び込みました。', '暖かい雰囲気のこのお店に引き込まれるように入りました。']
        C_part = ['このお店の感想ですが、とにかく美味しいの一言に尽きます！', '当店はメニューが豊富でまた訪れたくなります。', 'ここは食事だけでなくアンティークな家具が醸し出す雰囲気が特徴です。', 'このお店は料理だけではなく、スタッフの笑顔も大きな癒しです。', '思うのですが、名店は出される水のクオリティからして違います！', '老舗の安定感というものでしょうか、静かで清掃が行き届いていて居心地の良い空間を提供してくれます。風格すら感じられますね。']
        D_part = ['誰をお連れしてもどんなシーンでも後悔はないと思います。', 'この地域を訪れるのなら話題作りにもお勧めです！', '欲を言えば、もう少し価格が安ければ言うことはないと思います。ただあの雰囲気ですからそれも許容範囲内です！', '同行した両親も大変満足していました。良い思い出ができ感謝しております。', 'お陰様で商談もスムーズに進み、お客様も上司も大満足でした。', '夜景がとってもきれいなので窓際の席がお勧めです！']
        # Query to get all records with id > 10
        reviews = Review.objects.filter(id__gte=11)
        for review in reviews:
            new_comment = f"{random.choice(A_part)}{review.visit_date.year}年{review.visit_date.month}月。{random.choice(B_part)}{random.choice(C_part)}{random.choice(D_part)}"
            # Update name and description
            review.comment = new_comment
            # Save the changes
            review.save()
        print(f"{reviews.count()} records updated successfully!")
