import collections
import json
import os
from collections import OrderedDict

import requests
import termextract.core
import termextract.mecab
from django.http import HttpResponse
from requests_oauthlib import OAuth1Session


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
    print(request)
    res = []
    word_list = []
    CK = 'D9fYYLjLvJEbR3au47bXTas3z'  # Consumer Key
    CS = 'VXZaoyzkkxi5LBORMlsBYl1odq5HdJkxP4QwO9SsZo0q1uY9tL'  # Consumer Secret
    AT = '1321250221-Ny8XKv7BKC6TF5hjYJuX6SkDF4DJZzcSUoLbiXp'  # Access Token
    AS = '9AL5jzfTqGVSgao0yILAgwNtdXC3wpqnvIwGw0SDFquDE'  # Accesss Token Secert

    params = {"user_id": "924084285719568384",
              "include_rts": "false",
              "count": "10",
              "exclude_replies": "true"}

    # タイムライン取得用のURL
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"

    twitter = OAuth1Session(CK, CS, AT, AS)
    req = twitter.get(url, params=params)
    f1 = open("sample.txt", "w")

    if req.status_code == 200:
        # レスポンスはJSON形式なので parse する
        timeline = json.loads(req.text)
        # 各ツイートの本文を表示
        for tweet in timeline:
            print(tweet["text"])
            res.append(tweet["text"])

            # 形態素解析
            response = requests.post(
                "https://labs.goo.ne.jp/api/morph",
                json.dumps({"app_id": "992b19514586fa359cd274b6d1fb79106fda77a08d4d65e2e9e18d5d5b879f45",
                            "sentence": tweet["text"]}),
                headers={'Content-Type': 'application/json'})

            word = ""
            json_responses = json.loads(response.text)

            for x in range(0, len(json_responses["word_list"][0])):
                word = json_responses["word_list"][0][x][0]
                if word != " ":
                    if x != len(json_responses["word_list"][0])-1:
                        f1.write(word + "\n")
                    else:
                        f1.write(word)

    else:
        pass

    f1.close()
    f2 = open("sample.txt", "r", encoding="utf-8").read()
    frequency = termextract.mecab.cmp_noun_dict(f2)
    print("done")
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
    f2.close()

    os.remove('sample.txt')
    return render_json_response(request, data)
