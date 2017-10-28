from django.conf.urls import url
from twitter import views

urlpatterns = [
    url(r'^tweet/$', views.get_twitter, name='twitter'),     # 一覧
]