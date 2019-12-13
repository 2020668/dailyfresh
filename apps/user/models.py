from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings

from db.base_model import BaseModel


# Create your models here.


class User(AbstractUser, BaseModel):

    # 生成用户前面字符串
    # def generate_active_token(self):
    #     serializer = Serializer(settings.SECRET_KEY, 3600)
    #     info = {'confirm': self.id}
    #     token = serializer.dump(info)
    #     return token.decode()

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Address(BaseModel):
    user = models.ForeignKey(User, verbose_name='所属账户', on_delete=models.DO_NOTHING)
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    address = models.CharField(max_length=100, verbose_name='收件人地址')
    zip_code = models.IntegerField(null=True, verbose_name='邮政编码')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    # objects = AddressManager()

    class Meta:
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name
