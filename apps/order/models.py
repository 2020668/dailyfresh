from django.db import models
from db.base_model import BaseModel


class OrderInfo(BaseModel):
    PAY_METHOD = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付')
    )

    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (1, '待发货'),
        (1, '待收货'),
        (1, '待评价'),
        (1, '已完成'),
    )

    order_id = models.CharField(max_length=128, primary_key=True, verbose_name='订单编号')
    user = models.ForeignKey('user.User', verbose_name='用户', on_delete=models.DO_NOTHING)
    address = models.ForeignKey('user.Address', verbose_name='地址', on_delete=models.DO_NOTHING)
    pay_method = models.SmallIntegerField(choices=PAY_METHOD, default=3, verbose_name='支付方式')
    total_count = models.IntegerField(default=1, verbose_name='商品数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价格')
    transit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')
    trance_no = models.CharField(max_length=128, verbose_name='支付编号')

    class Meta:
        db_table = 'df_order_info'
        verbose_name = '订单信息'
        verbose_name_plural = verbose_name


# 订单商品
class OrderGoods(BaseModel):
    order = models.ForeignKey('OrderInfo', verbose_name='订单信息', on_delete=models.DO_NOTHING)
    sku = models.ForeignKey('goods.GoodsSKu', verbose_name='商品SKU', on_delete=models.DO_NOTHING)
    count = models.IntegerField(default=1, verbose_name='商品数目')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    comment = models.CharField(max_length=256, default='', verbose_name='评论')

    class Meta:
        db_table = 'product_order'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name
