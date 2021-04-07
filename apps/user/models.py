from django.db import models
from django.contrib.auth.models import AbstractUser  # 用户验证类
from db.base_model import BaseModel
# Create your models here.


class User(AbstractUser, BaseModel):
    """用户模型类"""

    class Meta:
        db_table = 'ddf_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class AddressManage(models.Manager):
    """地址模型管理类"""

    def get_defualt_addr(self, user):
        """获取用户默认收货地址"""
        try:
            addr = self.get(user=user, is_default=True)
        except self.model.DoesNotExist:
            addr = None
        return addr

    def get_all_addr(self, user):
        """获取所有地址"""
        try:
            addr = self.filter(user=user)
        except self.model.DoesNotExist:
            addr = None
        return addr


class Address(BaseModel):
    """地址模型类"""

    user = models.ForeignKey('User', verbose_name='所属帐户', on_delete=models.CASCADE)  # 删除User之后对应的地址也会被删除
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收货地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮编')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    # 自定义一个管理类，方便后台管理
    object = AddressManage()

    class Meta:
        db_table = 'ddf_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name

