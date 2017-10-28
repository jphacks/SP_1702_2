from django.conf.urls import url
from twitter import views

urlpatterns = [
    # 書籍
    url(r'^v1/books/$', views.get_twitter, name='twitter'),     # 一覧
]