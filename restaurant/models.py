import datetime

from accounts.models import CustomUser
from django.db import models

class Category(models.Model):
  """カテゴリーモデル"""
  name = models.CharField(verbose_name='カテゴリー名', max_length=64)
  photo = models.ImageField(verbose_name='写真', blank=True, null=True)
  created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
  updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
  
  class Meta:
    verbose_name_plural = 'Category'

  def __str__(self):
    return self.name

class Restaurant(models.Model):
  """レストランモデル"""
  shop_owner = models.ForeignKey(CustomUser, verbose_name='店舗オーナー', on_delete=models.PROTECT, null=True, blank=True)
  category = models.ForeignKey(Category, verbose_name='カテゴリー', on_delete=models.PROTECT)
  rate = models.FloatField(verbose_name='レート', default=0.0)
  zip_code = models.CharField(verbose_name='郵便番号', max_length=32)
  shop_name = models.CharField(verbose_name='店舗名', max_length=64)
  address = models.CharField(verbose_name='住所', max_length=128)
  phone = models.CharField(verbose_name='電話番号', max_length=32)
  owner_name = models.CharField(verbose_name='代表者名', max_length=64)
  email = models.CharField(max_length=128, null=True, blank=True, verbose_name='メールアドレス')
  description = models.CharField(verbose_name='説明', max_length=128)
  photo = models.ImageField(verbose_name='写真', blank=True, null=True)
  business_time = models.CharField(verbose_name='営業時間', max_length=64, null=True, blank=True)
  close_day_of_week = models.CharField(verbose_name='定休日', max_length=32, null=True, blank=True)
  created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
  updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
  
  class Meta:
    verbose_name_plural = 'Restaurant'
    
  def __str__(self):
    return self.shop_name
  
class DiningTable(models.Model):
  """卓モデル"""
  NUMBER_OF_PEOPLE = (('', '選択してください'), (1, '1名'), (2, '2名'), (3, '3名'), (4, '4名'), (5, '5名'), (6, '6名'), (7, '7名'), (8, '8名'), (9, '9名'), (10, '10名'), (11, '11名'), (12, '12名'), (13, '13名'), (14, '14名'), (15, '15名'), (16, '16名'), (17, '17名'), (18, '18名'), (19, '19名'), (20, '20名'), (21, '21名'), (22, '22名'), (23, '23名'), (24, '24名'), (25, '25名'), (26, '26名'), (27, '27名'), (28, '28名'), (29, '29名'), (30, '30名'), (31, '31名'), (32, '32名'), (33, '33名'), (34, '34名'), (35, '35名'), (36, '36名'), (37, '37名'), (38, '38名'), (39, '39名'), (40, '40名'), (41, '41名'), (42, '42名'), (43, '43名'), (44, '44名'), (45, '45名'), (46, '46名'), (47, '47名'), (48, '48名'),(49, '49名'), (50, '50名'),)

  restaurant = models.ForeignKey(Restaurant, verbose_name='レストラン', on_delete=models.PROTECT)
  name_for_internal = models.CharField(verbose_name='卓名（店舗管理用）', max_length=64)
  name_for_customer = models.CharField(verbose_name='卓名（HP表示用）', max_length=64)
  min_people = models.IntegerField(verbose_name='最少人数', choices=NUMBER_OF_PEOPLE, default='')
  max_people = models.IntegerField(verbose_name='最大人数', choices=NUMBER_OF_PEOPLE, default='')
  created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
  updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
  
  class Meta:
    verbose_name_plural = 'Dining Table'

  def __str__(self):
    return self.name_for_internal

class Reservation(models.Model):
  """予約モデル"""
  TIMES = (
    ('', '選択してください'), (datetime.time(12, 0), '12:00'), (datetime.time(13, 0), '13:00'), (datetime.time(14, 0), '14:00'),(datetime.time(15, 0), '15:00'), (datetime.time(18, 0), '18:00'), (datetime.time(19, 0), '19:00'), (datetime.time(20, 0), '20:00'), (datetime.time(21, 0), '21:00'), (datetime.time(22, 0), '22:00'),
    )
  NUMBER_OF_PEOPLE = (
    ('', '選択してください'), (1, '1名'), (2, '2名'), (3, '3名'), (4, '4名'), (5, '5名'), (6, '6名'), (7, '7名'), (8, '8名'), (9, '9名'), (10, '10名'),
    )

  customer = models.ForeignKey(CustomUser, verbose_name='ユーザー会員', on_delete=models.PROTECT, null=True, blank=True)
  restaurant = models.ForeignKey(Restaurant, verbose_name='レストラン', on_delete=models.PROTECT)
  dining_table = models.ForeignKey(DiningTable, verbose_name='卓情報', on_delete=models.PROTECT)
  date = models.DateField(verbose_name='予約日')
  time_start = models.TimeField(verbose_name='予約開始時間', choices=TIMES, default='')
  time_end = models.TimeField(verbose_name='予約終了時間', choices=TIMES, default='', null=True, blank=True)
  number_of_people = models.IntegerField(verbose_name='人数', choices=NUMBER_OF_PEOPLE, default='', null=True, blank=True)
  is_booked = models.BooleanField(verbose_name='予約済みフラグ', default='0')
  created_at = models.DateTimeField(verbose_name='予約受付日時', auto_now_add=True)
  updated_at = models.DateTimeField(verbose_name='予約更新日時', auto_now=True)
  
  class Meta:
    verbose_name_plural = 'Reservation'

  def __str__(self):
    return self.restaurant.shop_name

class Review(models.Model):
  """レビューモデル"""
  RATES = ((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'))

  customer = models.ForeignKey(CustomUser, verbose_name='ユーザー会員', on_delete=models.PROTECT, null=True, blank=True)
  restaurant = models.ForeignKey(Restaurant, verbose_name='レストラン', on_delete=models.PROTECT)
  visit_date = models.DateField(verbose_name='訪問日')
  comment = models.TextField(verbose_name='コメント', blank=True, null=True)
  rate = models.IntegerField(verbose_name='レート', default=5, choices=RATES)
  # reply = models.TextField(verbose_name='回答', blank=True, null=True)
  display_masked = models.BooleanField(verbose_name='非表示フラグ', default='0')
  comment_created_at = models.DateTimeField(verbose_name='レビュー作成日時', auto_now_add=True)
  comment_updated_at = models.DateTimeField(verbose_name='レビュー更新日時', auto_now=True)
  # reply_created_at = models.DateTimeField(verbose_name='回答作成日時', auto_now_add=True)
  # reply_updated_at = models.DateTimeField(verbose_name='回答更新日時', auto_now=True)
  
  class Meta:
    verbose_name_plural = 'Review'

  def __str__(self):
    return self.restaurant.shop_name

class ReviewReply(models.Model):
  """レビュー回答モデル"""
  review = models.ForeignKey(Review, verbose_name='レビュー', on_delete=models.PROTECT)
  reply = models.TextField(verbose_name='回答', blank=True, null=True)
  display_masked = models.BooleanField(verbose_name='非表示フラグ', default='0')
  comment_created_at = models.DateTimeField(verbose_name='回答作成日時', auto_now_add=True)
  comment_updated_at = models.DateTimeField(verbose_name='回答更新日時', auto_now=True)
  
  class Meta:
    verbose_name_plural = 'Review Reply'

  def __str__(self):
    return self.review.restaurant.shop_name


class Favorite(models.Model):
  """お気に入りモデル"""
  customer = models.ForeignKey(CustomUser, verbose_name='ユーザー会員', on_delete=models.PROTECT, null=True, blank=True)
  restaurant = models.ForeignKey(Restaurant, verbose_name='レストラン', on_delete=models.PROTECT)
  created_at = models.DateTimeField(verbose_name='お気に入り登録日時', auto_now_add=True)
  updated_at = models.DateTimeField(verbose_name='お気に入り更新日時', auto_now=True)
  
  class Meta:
    verbose_name_plural = 'Favorite'
  
  def __str__(self):
    return self.restaurant.shop_name