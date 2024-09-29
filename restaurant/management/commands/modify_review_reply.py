from django.core.management.base import BaseCommand
import random
from restaurant.models import Review
from datetime import time


class Command(BaseCommand):
    help = 'Modify reply comment'

    def handle(self, *args, **kwargs):
        # Define the choices
        A_part = ['この度は当店をご利用いただきありがとうございました。', '当店にお越しいただき誠にありがとうございます。', 'ご来訪いただきありがとうございました。', '今回は当店をお選びくださり有難うございます。', 'ご来訪有難うございます。', '先ずは足元の悪い中お越しくださり感謝申し上げます。']
        B_part = ['ご満足いただけまして一同安堵しております。', 'このようなお言葉を頂戴し光栄でございます。', '頂いたメッセージは担当スタッフも目を通し、感激しておりました。']
        C_part = ['当店は品質を向上させつつも、よりお越しいただきやすい価格でご提供できるよう精進してまいる所存です。', 'スタッフの笑顔と行き届いた清掃を心掛け、お客様により快適な空間をご提供できるよう取り組んでまいります。', '創業の精神である温かいおもてなしをスタッフ一同で共有し、サービスの向上に取り組んでまいります。', '引き続きシェフが自信をもってご提供するお食事はもちろんのこと、居心地の良い空間を提供できるよう心掛けてまいります。', 'いつでも「帰ってきた」と思っていただける。そんな店でありたいと考えています。', '今後ともお客さまから選ばれ続けるよう改善を積み重ねていく所存です。']
        D_part = ['またのお越しをお待ちしております。', 'この度は誠にありがとうございました。', 'またのご来店をお待ちしております。', '再会を一同楽しみにしております。', '今後ともよろしくお願いいたします。', '改めて今回は誠にありがとうございました。', '引き続き当店をお引き立てくださいますようお願い申し上げます。']

        # Query to get all records with id > 10
        reviews = Review.objects.filter(id__gte=11)
        for review in reviews:
            new_reply = f"{random.choice(A_part)}{random.choice(B_part)}{random.choice(C_part)}{random.choice(D_part)}"
            # Update name and description
            review.reply = new_reply
            # Save the changes
            review.save()
        print(f"{reviews.count()} records updated successfully!")
