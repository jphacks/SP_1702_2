from django.conf.urls import url
from food import views

urlpatterns = [
    url(r'^food/$', views.get_food, name='food'),     # 一覧
]