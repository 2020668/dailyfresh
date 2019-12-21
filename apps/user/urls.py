from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from user.views import RegisterView, ActiveView, LoginView, LogoutView, UserInfoView, UserOrderView, AddressView
from user import views


urlpatterns = [
    # url('^register$', views.register, name='register'),
    url('^register$', RegisterView.as_view(), name='register'),
    url('^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    url('^login$', LoginView.as_view(), name='login'),
    url('^logout$', LogoutView.as_view(), name='logout'),

    url('^verify_code/$', views.verify_code, name='verify_code'),
    url('^$', UserInfoView.as_view(), name='user'),     # 用户中心　信息页
    url('^order$', UserOrderView.as_view(), name='order'),      # 用户中心　订单页
    url('^address$', AddressView.as_view(), name='address')      # 用户中心　地址页
]

