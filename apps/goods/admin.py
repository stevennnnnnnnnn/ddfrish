from django.contrib import admin
from apps.goods.models import *
from django.core.cache import cache
# Register your models here.


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 发出异步任务，让celery去重新生成index.html
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 每次更新首页静态文件都需要清除缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        super().delete_model(request, obj)

        # 发出异步任务，让celery去重新生成index.html
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        cache.delete('index_page_data')


admin.site.register(GoodsType, BaseModelAdmin)
admin.site.register(Goods, BaseModelAdmin)
admin.site.register(GoodsSKU, BaseModelAdmin)
# admin.site.register(GoodsImage, BaseModelAdmin)
admin.site.register(IndexGoodsBanner, BaseModelAdmin)
admin.site.register(IndexTypeGoodsBanner, BaseModelAdmin)
admin.site.register(IndexPromotionBanner, BaseModelAdmin)
