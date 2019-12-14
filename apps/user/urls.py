from django.conf.urls import url
from user.views import RegisterView, ActiveView, LoginView


urlpatterns = [
    # url('^register$', views.register, name='register'),
    url('^register$', RegisterView.as_view(), name='register'),
    url('^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    url('^login$', LoginView.as_view(), name='login'),
]

