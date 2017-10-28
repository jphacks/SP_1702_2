import json
from collections import OrderedDict

import requests
from django.http import HttpResponse
from requests_oauthlib import OAuth1Session

import termextract.mecab
import termextract.core
import collections
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


def get_twitter(request):  # twitter取得
    res = []
    word_list = []
    CK = 'TddC18rLgkTpINdoTSEXbIdJY'  # Consumer Key
    CS = 'mNaw4USUSbe8TKt1lnfKvLzGVpYRAnXXJTgoTZlQnRtFJfTHQl'  # Consumer Secret
    AT = '924084285719568384-hTXQsl5VJSjXe6PHRs2fN9kXK07CxzT'  # Access Token
    AS = 'sjy93O0EcCXlAQWdl0Tv6BPPTMAw6crNY63yA0dhi2u7D'  # Accesss Token Secert

    params = {
        "count": "200"
    }

    # タイムライン取得用のURL
    url = "https://api.twitter.com/1.1/statuses/home_timeline.json"

    twitter = OAuth1Session(CK, CS, AT, AS)
    req = twitter.get(url, params=params)

    if req.status_code == 200:
        # レスポンスはJSON形式なので parse する
        timeline = json.loads(req.text)
        # 各ツイートの本文を表示
        for tweet in timeline:
            res.append(tweet["text"])

            # 形態素解析
            response = requests.post(
                "https://labs.goo.ne.jp/api/morph",
                json.dumps({"app_id": "01b8ea01ad55394c6e987fc3a84332dc5848e12a3b0b57c3dba01eb4b0b7b9ac",
                            "sentence": tweet["text"]}),
                headers={'Content-Type': 'application/json'})

            word = ""
            json_responses = json.loads(response.text)
            print(json_responses)
            for x in range(0, len(json_responses["word_list"][0])):
                word = json_responses["word_list"][0][x][0]
                word_list.append(word)

    else:
        pass

    frequency = termextract.mecab.cmp_noun_dict(word_list)
    LR = termextract.core.score_lr(frequency,
                                   ignore_words=termextract.mecab.IGNORE_WORDS,
                                   lr_mode=1, average_rate=1
                                   )
    term_imp = termextract.core.term_importance(frequency, LR)

    # 重要度が高い順に並べ替えて出力
    data_collection = collections.Counter(term_imp)
    for cmp_noun, value in data_collection.most_common():
        print(termextract.core.modify_agglutinative_lang(cmp_noun), value, sep="\t")
    data = OrderedDict([('tweet', res)])

    return render_json_response(request, data)
