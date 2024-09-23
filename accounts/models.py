from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
  """拡張ユーザーモデル"""
  ACCOUNT_TYPE = (
    (0, '選択してください'), (1, 'ユーザー会員'), (2, '店舗オーナー'), (3, 'システム管理者'),
    )
  user_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='ユーザー名')
  # email = models.CharField(max_length=128, null=True, blank=True, verbose_name='メールアドレス')
  # phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='電話番号')
  # 有料会員情報
  # account_type = 0
  username = models.CharField(max_length=150, unique=True, blank=True, null=True)
  account_type = models.IntegerField(verbose_name='アカウント種別', choices=ACCOUNT_TYPE, null=True, blank=True, default=0)
  is_subscribed = models.BooleanField(default=False, verbose_name='有料会員')
  card_number = models.CharField(max_length=128, null=True, blank=True, verbose_name='カード番号')
  card_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='カード名義')
  expiry = models.CharField(max_length=7, null=True, blank=True, verbose_name='カード有効期限', help_text='YYYY-MM形式で入力してください')
  created_at = models.DateTimeField(verbose_name='お気に入り登録日時', auto_now_add=True)
  updated_at = models.DateTimeField(verbose_name='お気に入り更新日時', auto_now=True)

  class Meta:
    verbose_name_plural = 'CustomUser'
  
  def __str__(self):
      return self.username
