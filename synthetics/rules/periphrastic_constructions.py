from typing import Literal
from collections import defaultdict
from functools import cache


PERIPHRASTIC_CONSTRUCTIONS = {
    "-ㄴ 가운데": ("ETM$ ^가운데/NNG", None),
    "-ㄴ 감이 있-": ("ETM$ ^감/NNG ^있/VA", None),
    "-ㄴ 격(이-)": ("ETM$ ^격/NNB", None),
    "-ㄴ 결과": ("(NNG+.+/XSV|VV)\+.+/ETM$ ^결과/NNG(\+,/SP)?$", None),
    "-ㄴ 고로": ("ETM$ ^고로/MAG", None),
    "-ㄴ 관계로": ("ETM$ ^관계/NNG\+로/JKB", None),
    "-ㄴ 길에": ("[는던]/ETM$ ^길/NNG\+에/JKB$", None),
    "-ㄴ 김에": ("ETM$ ^김/NNB\+에/JKB", None),
    "-ㄴ 까닭에": ("ETM$ ^까닭/NNG\+에/JKB", None),
    "-ㄴ 까닭으로": ("ETM$ ^까닭/NNG\+으로/JKB", None),
    "-ㄴ 끝에": ("ETM$ ^끝/NNG\+에/JKB", None),
    "-ㄴ 나머지": ("ETM$ ^나머지/NNG(\+,/SP)?$", None),
    "-ㄴ 다음(에)": ("ETM$ ^다음/NNG", None),
    "-ㄴ 대로": ("ETM$ ^대로/NNB", None),
    "-ㄴ 대신": ("ETM$ ^대신/NNG", None),
    "-ㄴ 덕분에": ("ETM$ ^덕분/NNG", None),
    "-ㄴ 덕(에|으로)": ("ETM$ ^덕/NNG", None),
    "-ㄴ 덕택(에|으로)": ("ETM$ ^덕택/NNG", None),
    "-ㄴ 데에": ("ETM$ ^데/NNB", None),
    "-ㄴ 도중(에)": ("ETM$ ^도중/NNG", None),
    "-ㄴ 동시에": ("ETM$ ^동시/NNG[^$]+", None),
    "-ㄴ 동안(에)": ("ETM$ ^동안/NNG", None),
    "-ㄴ 둥": ("ETM$ ^둥/NNB$", None),
    "-ㄴ 뒤(에)": ("ETM$ ^뒤/NNG", None),
    "-ㄴ 등": ("ETM$ ^등/NNB", None),
    "-ㄴ 바 있-": ("ETM$ ^바/NNB ^있/VA", None),
    "-ㄴ 바(,)": ("ETM$ ^바/NNB(\+,/SP)?$", None),
    "-ㄴ 바람에": ("ETM$ ^바람/NNB\+에/JKB$", None),
    "-ㄴ 반면(에)": ("ETM$ ^반면/NNG", None),
    "-ㄴ 법이 없-": ("ETM$ ^법/NNB+./J..?$ ^없/VA", None),
    "-ㄴ 법이-": ("ETM$ ^법/NNB\+이/VCP", None),
    "-ㄴ 사이(에)": ("ETM$ ^사이/NNG(\+에/JKB)?$", None),
    "-ㄴ 상태로": ("ETM$ ^상태/NNG", None),
    "-ㄴ 수가 있-": ("ETM$ ^수/NNB\+./(JX|JKS)$ ^있/VA", None),
    "-ㄴ 수밖에 없-": ("ETM$ ^수/NNB$ ^밖에/JX$ ^없/VA", None),
    "-ㄴ 식(이-)": ("ETM$ ^식/NNB", None),
    "-ㄴ 양하-": ("ETM$ ^양/NNB\+하/XSA", None),
    "-ㄴ 연후에": ("ETM$ ^연후/NNG", None),
    "-ㄴ 와중에": ("ETM$ ^와중/NNG\+에/JKB", None),
    "-ㄴ 외에": ("ETM$ ^외/NNB\+에/JKB", None),
    "-ㄴ 의도(로|에서)": ("ETM$ ^의도/NNG\+(로|에서)/JKB", None),
    "-ㄴ 이래(,|로)": ("ETM$ ^이래/NNB", None),
    "-ㄴ 이상": ("ETM$ ^이상/NNG(\+,/SP)?$", None),
    "-ㄴ 이유로": ("ETM$ 이유/NNG\+로/JKB", None),
    "-ㄴ 이후(로|에)": ("ETM$ ^이후/NNG", None),
    "-ㄴ 적이 없-": ("ETM$ ^적/NNB ^없/VA", None),
    "-ㄴ 적이 있-": ("ETM$ ^적/NNB ^있/VA", None),
    "-ㄴ 족족": ("ETM$ ^족족/NNB", None),
    "-ㄴ 줄(을) 모르-": (" [ㄴ은는]/ETM$ ^줄/NNB ^모르/VV", None),
    "-ㄴ 줄(을) 알-": ("[ㄴ은는]/ETM$ ^줄/NNB ^알/VV", None),
    "-ㄴ 중(이-)": ("ETM$ ^중/NNB", None),
    "-ㄴ 직후": ("ETM$ ^직후/NNG", None),
    "-ㄴ 차(이-)": ("ETM$ ^차/NNB", None),
    "-ㄴ 찰나(에)": ("ETM$ ^찰나/NNG", None),
    "-ㄴ 채(로)": ("ETM$ ^채/NNB", None),
    "-ㄴ 척(하-)": ("ETM$ ^척/NNB", None),
    "-ㄴ 체(하-)": ("ETM$ ^체/NNB", None),
    "-ㄴ 축에 들-": ("ETM$ ^축/NNB ^들/VV", None),
    "-ㄴ 축에 속하-": ("ETM$ ^축/NNB ^속하/VV", None),
    "-ㄴ 탓(이-)": ("ETM$ ^탓/NNG", None),
    "-ㄴ 통에": ("ETM$ ^통/NNB\+에/JKB", None),
    "-ㄴ 편(이-)": ("ETM$ ^편/NNB", None),
    "-ㄴ 한": ("ETM$ ^한/NNG", None),
    "-ㄴ 한에서": ("ETM$ ^한/NNG\+에서/JKB$", None),
    "-ㄴ 한이 있(어도|더라도)": ("ETM$ ^한/NNG\+이/JKS$ ^있/VA", None),
    "-ㄴ 한편": ("ETM$ ^한편/NNG", None),
    "-ㄴ 후(에)": ("ETM$ ^후/NNG", None),
    "-ㄴ/ㄹ 것 같-": ("ETM$ ^[것거]/NNB ^같/VA", None),
    "-ㄴ/ㄹ 것": ("ETM$ ^[것거]/NNB", None),
    "-ㄴ/ㄹ 것이 틀림없-": ("ETM$ ^[것거]/NNB ^틀림없/VA", None),
    "-ㄴ/ㄹ 겸": ("ETM$ ^겸/NNB", None),
    "-ㄴ/ㄹ 경우(,|에|에는)": ("ETM$ ^경우/NNG(에/JKB\+[ㄴ는]/JX|\+,/SP)?$", None),
    "-ㄴ/ㄹ 노릇이-": ("ETM$ ^노릇/NNG", None),
    "-ㄴ/ㄹ 데가 없": ("ETM$ ^데/NNB ^없/VA", None),
    "-ㄴ/ㄹ 듯": ("ETM$ ^듯/NNB$", None),
    "-ㄴ/ㄹ 듯싶-": ("ETM$ ^듯/NNB\+싶/VX", None),
    "-ㄴ/ㄹ 듯이": ("ETM$ ^듯이/(NNB|EC)", None),
    "-ㄴ/ㄹ 듯하-": ("ETM$ ^듯/NNB\+하/XSA", None),
    "-ㄴ/ㄹ 때": ("ETM$ ^때/NNG", None),
    "-ㄴ/ㄹ 마당에": ("ETM$ ^마당/NNB\+에/JKB", None),
    "-ㄴ/ㄹ 만큼": ("ETM$ ^만큼/NNB", None),
    "-ㄴ/ㄹ 모양이-": ("ETM$ ^모양/NNB", None),
    "-ㄴ/ㄹ 바에(야|는)": ("ETM$ ^바/NNB\+에/JKB", None),
    "-ㄴ/ㄹ 법하-": ("ETM$ ^법/NNB\+하/XSA", None),
    "-ㄴ/ㄹ 성싶-": ("ETM$ ^성/NNB\+싶/VX", None),
    "-ㄴ/ㄹ 셈이-": ("ETM$ ^셈/NNB", None),
    "-ㄴ/ㄹ 시기(에)": ("ETM$ ^시기/NNG", None),
    "-ㄴ/ㄹ 양(이-)": ("ETM$ ^양/NNB", None),
    "-ㄴ/ㄹ 즈음": ("ETM$ ^즈음", None),
    "-ㄴ/ㄹ 지": ("ETM$ ^지/NNB", None),
    "-ㄴ/ㄹ 지경(이-)": ("ETM$ ^지경/NNB", None),
    "-ㄴ/ㄹ 참(이-)": ("ETM$ ^참/NNB", None),
    "-ㄴ/ㄹ 터(이-)": ("ETM$ ^터/NNB", None),
    "-ㄴ/ㄹ 판(이-)": ("ETM$ ^판/NNB", None),
    "-ㄴ/ㄹ 판국(이-)": ("ETM$ ^판국/NNG", None),
    "-ㄴ/ㄹ지도 모르-": ("(ㄴ지|는지|ㄹ지|을지)/EF\+도/JX$ ^모르/VV", None),
    "-ㄴ가 보-": ("ㄴ가/EF$ ^보/VX", None),
    "-ㄴ가 싶-": ("[ㄴ던]가/EF$ ^싶/VX", None),
    "-ㄴ가 하면": ("는가/EF$ ^하/VV\+면/EC", None),
    "-ㄴ다는/-려는/-려던/ㄹ 계획이-": ("(ㄹ|을|단|다는|ㄴ다는|려는|으려는|려던|으려던)/ETM$ ^계획/NNG", None),
    "-ㄴ다는/-려는/-려던/ㄹ 생각(이-)": ("(ㄹ|을|려는|으려는|려던|으려던|자던|자는)/ETM$ ^생각/NNG\+(이/VCP|에/JKB|에서/JKB)", None),
    "-ㄴ데 반하여": ("[ㄴ는]데/EC$ ^반하/VV\+아/EC", None),
    "-ㄴ데 비(해|하여)": ("[ㄴ는]데/EC$ ^비/NNG\+하/XSV", None),
    "-ㄴ데도 불구하고": ("(ㄴ데|는데)/EC\+도/JX$ ^불구하/VV", None),
    "-ㄹ 것(이라는|으로) 전망(이-|하-|되-)": ("ETM$ ^[것거]/NNB ^전망/NNG", None),
    "-ㄹ 겨를이 없-": ("ETM$ ^겨를/NNB ^없(/VA|이/MAG)", None),
    "-ㄹ 나위(가) 없-": ("ETM$ ^나위/NNB ^없(/VA|이/MAG)", None),
    "-ㄹ 녘에": ("ETM$ ^녘/NNB", None),
    "-ㄹ 따름(이-)": ("ETM$ ^따름/NNB", None),
    "-ㄹ 리(가) 없-": ("ETM$ ^리/NNB ^없/VA", None),
    "-ㄹ 리(가) 있-": ("ETM$ ^리/NNB ^있/VA", None),
    "-ㄹ 리가 만무하-": ("ETM$ ^리/NNB ^만무/NNG", None),
    "-ㄹ 만도 하-": ("ETM$ ^만/NNB\+도/JX$ ^하/V", None),
    "-ㄹ 만하-": ("ETM$ ^만/NNB\+하/XSA", None),
    "-ㄹ 무렵(에)": ("ETM$ ^무렵/NNB", None),
    "-ㄹ 방침이-": ("ETM$ ^방침/NNG", None),
    "-ㄹ 법도 하-": ("ETM$ ^법/NNB\+도/JX$ ^하/VV", None),
    "-ㄹ 뻔(하-)": ("ETM$ ^뻔/NNB", None),
    "-ㄹ 뿐(더러/이-)": ("ETM$ ^뿐/NNB", None),
    "-ㄹ 뿐(만) 아니라": ("ETM$ ^뿐/NNB ^아니/VCN", None),
    "-ㄹ 수 없-": ("ETM$ ^수/NNB ^없/VA", None),
    "-ㄹ 수 있-": ("ETM$ ^수/NNB ^있/VA", None),
    "-ㄹ 수밖에 없-": ("ETM$ ^수/NNB\+밖에/JX ^없/VA", None),
    "-ㄹ 시(에)": ("ETM$ ^시/NNB", None),
    "-ㄹ 예정이-": ("[ㄹ을]/ETM$ ^예정/NNG", None),
    "-ㄹ 작정이-": ("ETM$ ^작정/NNG", None),
    "-ㄹ 적에": ("ETM$ ^적/NNB", None),
    "-ㄹ 전망이-": ("[ㄹ을]/ETM$ ^전망/NNG", None),
    "-ㄹ 정도(이-)": ("[ㄹ을]/ETM$ 정도/NNG", None),
    "-ㄹ 줄(을) 모르-": ("[ㄹ을]/ETM$ ^줄/NNB ^모르/VV", None),
    "-ㄹ 줄(을) 알-": ("[ㄹ을]/ETM$ ^줄/NNB ^알/VV", None),
    "-ㄹ 턱(이) 없-": ("ETM$ ^턱/NNB ^없/VA", None),
    "-ㄹ/-던/-려던 때": ("(ㄹ|을|던|려던)/ETM$ ^때/NNG", None),
    "-ㄹ까 보-": ("[ㄹ을]까/EF$ ^보/V", None),
    "-ㄹ까 싶-": ("[ㄹ을]까/EF$ ^싶/VX", None),
    "-ㄹ까 하-": ("[ㄹ을]까/EF$ ^하/VV", None),
    "-ㄹ지 모르-": ("[ㄹ을]지/EF ^모르/VV", None),
    "-게 되-": ("게/EC$ ^되/VV", None),
    "-게 마련이-": ("게/EC$ ^마련/NNB", None),
    "-게 만들-": ("게/EC$ ^만들/VV", None),
    "-게 하-": ("(VV|롭/XSA)\+게/EC$ ^하/VV", None),
    "-고 계시-": ("고/EC$ ^계시/VX", None),
    "-고 나-": ("고/EC$ ^나/VX", None),
    "-고 들-": ("고/EC$ ^들/VX", None),
    "-고 말-": ("고/EC$ ^말/VX", None),
    "-고 보-": ("고/EC$ ^보/VX", None),
    "-고 싶-": ("고/EC$ ^싶/VX", None),
    "-고 있-": ("고/EC$ ^있/VX", None),
    "-고 있음에도": ("고/EC$ ^있/VX\+음/ETN\+에/JKB\+도/JX", None),
    "-고 해서": ("\+고/EC$ ^하/VX\+아서/EC", None),
    "-고는 하-": ("고는/EC$ ^하/VX", None),
    "-고도 남-": ("(고도/EC|고/EC\+도/JX)$ ^남/V", None),
    "-고자 하-": ("고자/EC$ ^하/VX", None),
    "-기 그지없-": ("기/ETN$ ^그지없/VA", None),
    "-기 나름이-": ("기/ETN$ ^나름/NNB", None),
    "-기 때문(이-)": ("기/ETN$ ^때문/NNB", None),
    "-기 마련이-": ("기/ETN$ ^마련/NNB", None),
    "-기 망정이-": ("기/ETN$ ^망정/NNB", None),
    "-기 바라-": ("기/ETN ^바라/VV", None),
    "-기 쉽-": ("기/ETN ^쉽/VA", None),
    "-기 시작하-": ("기/ETN ^시작/NNG", None),
    "-기 십상이-": ("기/ETN ^십상/NNG", None),
    "-기 어렵-": ("기/ETN ^어렵/VA", None),
    "-기 예사이-": ("기/ETN ^예사/NNG", None),
    "-기 원하-": ("기/ETN ^원하/VA", None),
    "-기 위하-": ("기/ETN ^위하/VV", None),
    "-기 이전에": ("기/ETN$ ^이전/NNG", None),
    "-기 일쑤이-": ("기/ETN ^일쑤/NNG", None),
    "-기 짝이 없-": ("기/ETN ^짝/NNG\+이/JKS$ ^없/VA", None),
    "-기 틀리-": ("기/ETN ^틀리/VV", None),
    "-기(가) 무섭게": ("기/ETN ^무섭/VA\+게/EC$", None),
    "-기(에) 따라": ("기/ETN ^따르/VV", None),
    "-기(에) 앞서": ("기/ETN ^앞서/(VV|MAG)", None),
    "-기가 바쁘게": ("기/ETN ^바쁘/VA", None),
    "-기가 이를 데 없-": ("기/ETN$ ^이르/VV\+ㄹ/ETM$ ^데/NNB ^없/VA", None),
    "-기까지 하-": ("기/ETN\+까지/JX$ ^하/VX", None),
    "-기나 하-": ("기/ETN\+나/JX$ ^하/VX", None),
    "-기는 하-": ("기/ETN\+는/JX$ ^하/VX", None),
    "-기도 하-": ("기/ETN\+도/JX$ ^하/VX", None),
    "-기로 하-": ("기/ETN\+로/JKB$ ^하/VV", None),
    "-기만 하-": ("기/ETN\+만/JX$ ^하/V", None),
    "-나 보-": ("나/(EC/EF)$ ^보/(VX|VV)", None),
    "-나 싶-": ("나/(EC/EF)$ ^보/VX", None),
    "-는 하-": ("는/JX$ ^하/VX", None),
    "-다 못하-": ("다/EC$ ^못하/VX", None),
    "-다 보-": ("다/EC$ ^보/VX", None),
    "-다/라는 전망(이-)": ("(다는|ㄴ다는|리란|으리란|리라는|으리라는)/ETM$ ^전망/NNG", None),
    "-도록 하-": ("도록/EC$ ^하/VX", None),
    "-려(고) 들-": ("려고?/EC$ ^들/VX", None),
    "-려고 하-": ("(려고|으려고)/EC$ ^하/VX", None),
    "-로(서)는 처음으로": ("으?로서/JKB\+[ㄴ는]/JX$ ^처음/NNG", None),
    "-를 놓고": ("JKO$ ^놓/VV\+고/EC", None),
    "-를 두고": ("JKO$ ^두/VV\+고/EC", None),
    "-만에 처음으로": ("만/NNB\+에/JKB$ ^처음/NNG", None),
    "-면 안 되-": ("으?면/EC$ ^안/MAG$ ^되/VV", None),
    "-면 좋-": ("면/EC$ ^좋/VA", None),
    "-서는 한이 없-": ("서/EC\+는/JX$ ^한/NNG\+이/JKS$ ^없/VA", None),
    "-어 가-": ("[아어]/EC$ ^가/VX", None),
    "-어 가지고": ("[아어]/EC$ ^가지/VX", None),
    "-어 계시-": ("[아어]/EC$ ^계시/VX", None),
    "-어 나가-": ("[아어]/EC$ ^나가/VX", None),
    "-어 내-": ("[아어]/EC$ ^내/VX", None),
    "-어 놓-": ("[아어]/EC$ ^놓/VX", None),
    "-어 달-": ("[아어]/EC$ ^달/VX", None),
    "-어 대-": ("[아어]/EC$ ^대/VX", None),
    "-어 두-": ("[아어]/EC$ ^두/VX", None),
    "-어 드리-": ("[아어]/EC$ ^드리/VX", None),
    "-어 들-": ("[아어]/EC$ ^들/VX", None),
    "-어 마지않-": ("[아어]/EC$ ^마지않/VX", None),
    "-어 먹-": ("[아어]/EC$ ^먹/VX", None),
    "-어 버릇하-": ("[아어]/EC$ ^버릇하/VX", None),
    "-어 버리-": ("[아어]/EC$ ^버리/VX", None),
    "-어 보-": ("[아어]/EC$ ^보/VX", None),
    "-어 보이-": ("[아어]/EC$ ^보이/VV", None),
    "-어 오-": ("[아어]/EC$ ^오/VX", None),
    "-어 있-": ("[아어]/EC$ ^있/VX", None),
    "-어 주-": ("[아어]/EC$ ^주/VX", None),
    "-어 죽겠-": ("[아어]/EC$ ^죽/VV\+겠/EP", None),
    "-어 지-": ("[아어]/EC$ ^지/VV", None),
    "-어 치우-": ("[아어]/EC$ ^치우/VX", None),
    "-어도 되-": ("[아어]도/EC$ ^되/VV", None),
    "-어도 좋-": ("[아어]도/EC$ ^좋/VA", None),
    "-어야 되-": ("[아어]야/EC$ ^되/VV", None),
    "-어야 하-": ("[아어]야/EC$ ^하/VX", None),
    "-에 관하-": ("에/JKB$ ^관하/VV", None),
    "-에 대하-": ("에/JKB$ ^대하/VV", None),
    "-에 따라": ("에/JKB$ ^따르/VV\+아/EC", None),
    "-에 따르면": ("에/JKB$ ^따르/VV\+면/EC", None),
    "-에 비해": ("에/JKB$ ^비/NNG\+하/XSV\+아/EC", None),
    "-에도 불구하고": ("에/JKB\+도/JX$ ^불구하/VV", None),
    "-에서(는) 처음(으로)": ("에서/JKB(\+[ㄴ는]/JX)?$ ^처음/NNG", None),
    "-와/과 다르게": ("[와과]/JKB$ ^다르/VA\+게$", None),
    "-와/과 달리": ("[와과]/JKB$ ^달리/MAG", None),
    "-와/과 동시에": ("[와과]/JKB$ ^동시/NNG\+에/JKB", None),
    "-와/과 함께": ("[와과]/JKB$ ^함께/MAG(\+,/SP)?$", None),
    "-으면 하-": ("으면/EC$ ^하/VX", None),
    "-을 대상으로": ("JKO$ 대상/NNG\+으로/JKB", None),
    "-을 마지막으로": ("JKO$ 마지막/NNG\+으로/JKB", None),
    "-을 시작으로": ("JKO$ 시작/NNG\+으로/JKB", None),
    "-을 위하-": ("JKO$ ^위하/VV", None),
    "-을 향해/하여": ("JKO$ ^향하/VV\+아/EC", None),
    "-을 통해": ("JKO$ ^통하/VV", None),
    "-을 포함": ("JKO$ ^포함/NNG", None),
    "-을/를 끝으로": ("JKO$ 끝/NNG\+으로/JKB", None),
    "-의 경우": ("의/JKG$ ^경우/NNG", None),
    "-이 아니-": ("이/JKS$ ^아니/VCN", None),
    "-지 말-": ("지/EC$ ^말/VX", None),
    "-지 못하-": ("지/EC$ ^못하/VX", None),
    "-지 싶-": ("지/EC$ ^싶/VX", None),
    "-지 않-": ("지/EC$ ^않/VX", None),
    "~ 기준": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^기준/NNG", None),
    "~ 대비": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^대비/NNG", None),
    "~ 도중": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^도중/NNG", None),
    "~ 동안": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^동안/NNG", None),
    "~ 등": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^등/NNB", None),
    "~ 따위": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^따위/NNB", None),
    "~ 때문에": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|XSN)$ ^때문/NNB", None),
    "~ 미만": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^미만/NNG", None),
    "~ 뿐": ("(NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^뿐/NNB", None),
    "~ 시": ("(NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^시/NNB", None),
    "~ 이내": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이내/NNG", None),
    "~ 이상": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이상/NNG", None),
    "~ 이외": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이외/NNG", None),
    "~ 이유로": ("[을를]/JKO$ ^이유/NNG\+로/JKB", None),
    "~ 이전": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이전/NNG", None),
    "~ 이하": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이하/NNG", None),
    "~ 이후": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이후/NNG", None),
    "~ 전": ("(NP|NNG|NNB|MMD|ETN|XSN)$ ^전/NNG", None),
    "~ 중": ("(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^중/NNB", None),
    "~ 직전": ("(NP|NNG|ETN|XSN)$ ^직전/NNG", None),
    "~ 직후": ("(NP|NNG|ETN|XSN)$ ^직후/NNG", None),
    "~ 후": ("(NP|NNG|NNB|MMD|ETN|XSN)$ ^후/NNG", None)
}


def prioritize(rules: dict[str, str], sort: Literal['simple-to-complex', 'complex-to-simple'] = 'simple-to-complex'):
    assert sort in ('simple-to-complex', 'complex-to-simple')
    assert len(rules.keys()) == len(rules.values())
    reverse = False if sort == 'simple-to-complex' else True
    ngram_ranks = defaultdict(list)
    for key, rule in rules.items():
        ngram_ranks[len(rule.split())].append(key)
    for n in ngram_ranks:
        ngram_ranks[n] = sorted(ngram_ranks[n], key=lambda k: len(rules[k]), reverse=reverse)
    n_order = sorted(list(ngram_ranks.keys()), reverse=reverse)
    priority = []
    for n in n_order:
        priority.extend(ngram_ranks[n])
    return priority


class PeriphrasticConstructions(object):
    instance = None
    intact = True

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, sort: Literal['simple-to-complex', 'complex-to-simple']):
        if PeriphrasticConstructions.intact:
            self.ruleset = PERIPHRASTIC_CONSTRUCTIONS
            self.sort = sort
            self.priority = prioritize(self.ruleset, sort=sort)
            PeriphrasticConstructions.intact = False

    @cache
    def get_patterns(self):
        return [self.ruleset[key] for key in self.priority]


if __name__ == '__main__':
    pc = PeriphrasticConstructions(sort='simple-to-complex')
    print(pc.sort)
