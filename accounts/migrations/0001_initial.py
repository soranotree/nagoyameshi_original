# Generated by Django 4.2.16 on 2024-12-25 08:03

import django.contrib.auth.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "user_name",
                    models.CharField(
                        blank=True, max_length=128, null=True, verbose_name="ユーザー名"
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True, max_length=150, null=True, unique=True
                    ),
                ),
                (
                    "account_type",
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (0, "選択してください"),
                            (1, "ユーザー会員"),
                            (2, "店舗オーナー"),
                            (3, "システム管理者"),
                        ],
                        default=0,
                        null=True,
                        verbose_name="アカウント種別",
                    ),
                ),
                (
                    "is_subscribed",
                    models.BooleanField(default=False, verbose_name="有料会員"),
                ),
                (
                    "card_number",
                    models.CharField(
                        blank=True, max_length=128, null=True, verbose_name="カード番号"
                    ),
                ),
                (
                    "card_name",
                    models.CharField(
                        blank=True, max_length=128, null=True, verbose_name="カード名義"
                    ),
                ),
                (
                    "expiry",
                    models.CharField(
                        blank=True,
                        help_text="YYYY-MM形式で入力してください",
                        max_length=7,
                        null=True,
                        verbose_name="カード有効期限",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="お気に入り登録日時"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="お気に入り更新日時"
                    ),
                ),
                (
                    "subscription_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "CustomUser",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
