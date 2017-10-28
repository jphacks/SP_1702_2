from django.shortcuts import render
import json
from django.http import HttpResponse
from collections import OrderedDict
from requests_oauthlib import OAuth1Session
from sklearn.feature_extraction.text import TfidfVectorizer

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

def get_twitter(request):# twitter取得
    response = []
    CK = 'TddC18rLgkTpINdoTSEXbIdJY'  # Consumer Key
    CS = 'mNaw4USUSbe8TKt1lnfKvLzGVpYRAnXXJTgoTZlQnRtFJfTHQl'  # Consumer Secret
    AT = '924084285719568384-hTXQsl5VJSjXe6PHRs2fN9kXK07CxzT'  # Access Token
    AS = 'sjy93O0EcCXlAQWdl0Tv6BPPTMAw6crNY63yA0dhi2u7D'  # Accesss Token Secert

    params = {}

    # タイムライン取得用のURL
    url = "https://api.twitter.com/1.1/statuses/home_timeline.json"

    twitter = OAuth1Session(CK, CS, AT, AS)
    req = twitter.get(url, params=params)

    if req.status_code == 200:
        # レスポンスはJSON形式なので parse する
        timeline = json.loads(req.text)
        # 各ツイートの本文を表示
        for tweet in timeline:
            print(tweet["text"])
            response.append(tweet["text"])

    else:
        pass

    tfidf_vect = TfidfVectorizer()
    X_tfidf = tfidf_vect.fit_transform(response)
    print(X_tfidf)

    data = OrderedDict([ ('tweet', response) ])
    return render_json_response(request, data)