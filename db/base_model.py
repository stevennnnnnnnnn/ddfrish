from django.db import models


class BaseModel(models.Model):
    """模型抽象类，为所有几成此基类的模型类加入以下三个字段"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=0, verbose_name='是否删除')

    class Meta:
        """说明是个抽象类"""
        abstract = True
