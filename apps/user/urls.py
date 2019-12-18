from django.conf.urls import url
from user.views import RegisterView, ActiveView, LoginView
from user import views


urlpatterns = [
    # url('^register$', views.register, name='register'),
    url('^register$', RegisterView.as_view(), name='register'),
    url('^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    url('^login$', LoginView.as_view(), name='login'),
    url('^verify_code/$', views.verify_code, name='verify_code'),
]

