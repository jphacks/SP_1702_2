# Create your views here.
import collections
import json
from collections import OrderedDict

import requests
from django.http import HttpResponse


# Create your views here.


def render_json_response(request, data, status=None):
    """response を JSON で返却"""
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    callback = request.GET.get('callback')
    if not callback:
        callback = request.POST.get('callback')  # POSTでJSONPの場合
    if callback:
        json_str = "%s(%s)" % (callback, json_str)
        response = HttpResponse(json_str, content_type='application/javascript; charset=UTF-8', status=status)
    else:
        response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
    return response


def get_food(request):  # twitter取得
    res = []
    word_list = []
    postdata = request.GET
    lat = postdata["lat"]
    lon = postdata["lon"]
    response = requests.get(
        "https://api.gnavi.co.jp/RestSearchAPI/20150630/?format=json&keyid=52c9b75982497e0529413aed453662d2&latitude=" + lat + "&longitude=" + lon)
    # タイムライン取得用のURL
    data = response.json()

    data = OrderedDict([('shop', data["rest"][0]["name"])])

    return render_json_response(request, data)
