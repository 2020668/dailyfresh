from django.conf.urls import url
from apps.goods import views

urlpatterns = [
    url('', views.index, name='index'),
]
