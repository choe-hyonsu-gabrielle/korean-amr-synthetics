from typing import Optional, Literal, Any
from collections import defaultdict
from functools import cache


PERIPHRASTIC_CONSTRUCTIONS = {
    "-ㄴ 가운데": (r"ETM$ ^가운데/NNG", None),
    "-ㄴ 감이 있-": (r"ETM$ ^감/NNG ^있/VA", None),
    "-ㄴ 격(이-)": (r"ETM$ ^격/NNB", None),
    "-ㄴ 결과": (r"(NNG+.+/XSV|VV)\+.+/ETM$ ^결과/NNG(\+,/SP)?$", None),
    "-ㄴ 고로": (r"ETM$ ^고로/MAG", None),
    "-ㄴ 관계로": (r"ETM$ ^관계/NNG\+로/JKB", None),
    "-ㄴ 길에": (r"[는던]/ETM$ ^길/NNG\+에/JKB$", None),
    "-ㄴ 김에": (r"ETM$ ^김/NNB\+에/JKB", None),
    "-ㄴ 까닭에": (r"ETM$ ^까닭/NNG\+에/JKB", None),
    "-ㄴ 까닭으로": (r"ETM$ ^까닭/NNG\+으로/JKB", None),
    "-ㄴ 끝에": (r"ETM$ ^끝/NNG\+에/JKB", None),
    "-ㄴ 나머지": (r"ETM$ ^나머지/NNG(\+,/SP)?$", None),
    "-ㄴ 다음(에)": (r"ETM$ ^다음/NNG", None),
    "-ㄴ 대로": (r"ETM$ ^대로/NNB", None),
    "-ㄴ 대신": (r"ETM$ ^대신/NNG", None),
    "-ㄴ 덕분에": (r"ETM$ ^덕분/NNG", None),
    "-ㄴ 덕(에|으로)": (r"ETM$ ^덕/NNG", None),
    "-ㄴ 덕택(에|으로)": (r"ETM$ ^덕택/NNG", None),
    "-ㄴ 데에": (r"ETM$ ^데/NNB", None),
    "-ㄴ 도중(에)": (r"ETM$ ^도중/NNG", None),
    "-ㄴ 동시에": (r"ETM$ ^동시/NNG[^$]+", None),
    "-ㄴ 동안(에)": (r"ETM$ ^동안/NNG", None),
    "-ㄴ 둥": (r"ETM$ ^둥/NNB$", None),
    "-ㄴ 뒤(에)": (r"ETM$ ^뒤/NNG", None),
    "-ㄴ 등": (r"ETM$ ^등/NNB", None),
    "-ㄴ 바 있-": (r"ETM$ ^바/NNB ^있/VA", None),
    "-ㄴ 바(,)": (r"ETM$ ^바/NNB(\+,/SP)?$", None),
    "-ㄴ 바람에": (r"ETM$ ^바람/NNB\+에/JKB$", None),
    "-ㄴ 반면(에)": (r"ETM$ ^반면/NNG", None),
    "-ㄴ 법이 없-": (r"ETM$ ^법/NNB+./J..?$ ^없/VA", None),
    "-ㄴ 법이-": (r"ETM$ ^법/NNB\+이/VCP", None),
    "-ㄴ 사이(에)": (r"ETM$ ^사이/NNG(\+에/JKB)?$", None),
    "-ㄴ 상태이-": (r"ETM$ ^상태/NNG\+이/VCP", None),
    "-ㄴ 상황이-": (r"ETM$ ^상황/NNG\+이/VCP", None),
    "-ㄴ 수가 있-": (r"ETM$ ^수/NNB\+./(JX|JKS)$ ^있/VA", None),
    "-ㄴ 수밖에 없-": (r"ETM$ ^수/NNB$ ^밖에/JX$ ^없/VA", None),
    "-ㄴ 식(이-)": (r"ETM$ ^식/NNB", None),
    "-ㄴ 양하-": (r"ETM$ ^양/NNB\+하/XSA", None),
    "-ㄴ 연후에": (r"ETM$ ^연후/NNG", None),
    "-ㄴ 와중에": (r"ETM$ ^와중/NNG\+에/JKB", None),
    "-ㄴ 외에": (r"ETM$ ^외/NNB\+에/JKB", None),
    "-ㄴ 의도(로|에서)": (r"ETM$ ^의도/NNG\+(로|에서)/JKB", None),
    "-ㄴ 이래(,|로)": (r"ETM$ ^이래/NNB", None),
    "-ㄴ 이상": (r"ETM$ ^이상/NNG(\+,/SP)?$", None),
    "-ㄴ 이유로": (r"ETM$ 이유/NNG\+로/JKB", None),
    "-ㄴ 이후(로|에)": (r"ETM$ ^이후/NNG", None),
    "-ㄴ 적이 없-": (r"ETM$ ^적/NNB ^없/VA", None),
    "-ㄴ 적이 있-": (r"ETM$ ^적/NNB ^있/VA", None),
    "-ㄴ 족족": (r"ETM$ ^족족/NNB", None),
    "-ㄴ 줄(을) 모르-": (r" [ㄴ은는]/ETM$ ^줄/NNB ^모르/VV", None),
    "-ㄴ 줄(을) 알-": (r"[ㄴ은는]/ETM$ ^줄/NNB ^알/VV", None),
    "-ㄴ 중(이-)": (r"ETM$ ^중/NNB", None),
    "-ㄴ 직후": (r"ETM$ ^직후/NNG", None),
    "-ㄴ 차(이-)": (r"ETM$ ^차/NNB", None),
    "-ㄴ 찰나(에)": (r"ETM$ ^찰나/NNG", None),
    "-ㄴ 채(로)": (r"ETM$ ^채/NNB", None),
    "-ㄴ 척(하-)": (r"ETM$ ^척/NNB", None),
    "-ㄴ 체(하-)": (r"ETM$ ^체/NNB", None),
    "-ㄴ 축에 들-": (r"ETM$ ^축/NNB ^들/VV", None),
    "-ㄴ 축에 속하-": (r"ETM$ ^축/NNB ^속하/VV", None),
    "-ㄴ 탓(이-)": (r"ETM$ ^탓/NNG", None),
    "-ㄴ 통에": (r"ETM$ ^통/NNB\+에/JKB", None),
    "-ㄴ 편(이-)": (r"ETM$ ^편/NNB", None),
    "-ㄴ 한": (r"ETM$ ^한/NNG", None),
    "-ㄴ 한에서": (r"ETM$ ^한/NNG\+에서/JKB$", None),
    "-ㄴ 한이 있(어도|더라도)": (r"ETM$ ^한/NNG\+이/JKS$ ^있/VA", None),
    "-ㄴ 한편": (r"ETM$ ^한편/NNG", None),
    "-ㄴ 후(에)": (r"ETM$ ^후/NNG", None),
    "-ㄴ/ㄹ 것 같-": (r"ETM$ ^[것거]/NNB ^같/VA", None),
    "-ㄴ/ㄹ 것": (r"ETM$ ^[것거]/NNB", None),
    "-ㄴ/ㄹ 것이 틀림없-": (r"ETM$ ^[것거]/NNB ^틀림없/VA", None),
    "-ㄴ/ㄹ 겸": (r"ETM$ ^겸/NNB", None),
    "-ㄴ/ㄹ 경우(,|에|에는)": (r"ETM$ ^경우/NNG(에/JKB\+[ㄴ는]/JX|\+,/SP)?$", None),
    "-ㄴ/ㄹ 노릇이-": (r"ETM$ ^노릇/NNG", None),
    "-ㄴ/ㄹ 데가 없": (r"ETM$ ^데/NNB ^없/VA", None),
    "-ㄴ/ㄹ 듯": (r"ETM$ ^듯/NNB$", None),
    "-ㄴ/ㄹ 듯싶-": (r"ETM$ ^듯/NNB\+싶/VX", None),
    "-ㄴ/ㄹ 듯이": (r"ETM$ ^듯이/(NNB|EC)", None),
    "-ㄴ/ㄹ 듯하-": (r"ETM$ ^듯/NNB\+하/XSA", None),
    "-ㄴ/ㄹ 때": (r"ETM$ ^때/NNG", None),
    "-ㄴ/ㄹ 마당에": (r"ETM$ ^마당/NNB\+에/JKB", None),
    "-ㄴ/ㄹ 만큼": (r"ETM$ ^만큼/NNB", None),
    "-ㄴ/ㄹ 모양이-": (r"ETM$ ^모양/NNB", None),
    "-ㄴ/ㄹ 바에(야|는)": (r"ETM$ ^바/NNB\+에/JKB", None),
    "-ㄴ/ㄹ 법하-": (r"ETM$ ^법/NNB\+하/XSA", None),
    "-ㄴ/ㄹ 성싶-": (r"ETM$ ^성/NNB\+싶/VX", None),
    "-ㄴ/ㄹ 셈이-": (r"ETM$ ^셈/NNB", None),
    "-ㄴ/ㄹ 시기(에)": (r"ETM$ ^시기/NNG", None),
    "-ㄴ/ㄹ 양(이-)": (r"ETM$ ^양/NNB", None),
    "-ㄴ/ㄹ 즈음": (r"ETM$ ^즈음", None),
    "-ㄴ/ㄹ 지": (r"ETM$ ^지/NNB", None),
    "-ㄴ/ㄹ 지경(이-)": (r"ETM$ ^지경/NNB", None),
    "-ㄴ/ㄹ 참(이-)": (r"ETM$ ^참/NNB", None),
    "-ㄴ/ㄹ 터(이-)": (r"ETM$ ^터/NNB", None),
    "-ㄴ/ㄹ 판(이-)": (r"ETM$ ^판/NNB", None),
    "-ㄴ/ㄹ 판국(이-)": (r"ETM$ ^판국/NNG", None),
    "-ㄴ/ㄹ지도 모르-": (r"(ㄴ지|는지|ㄹ지|을지)/EF\+도/JX$ ^모르/VV", None),
    "-ㄴ가 보-": (r"ㄴ가/EF$ ^보/VX", None),
    "-ㄴ가 싶-": (r"[ㄴ던]가/EF$ ^싶/VX", None),
    "-ㄴ가 하면": (r"는가/EF$ ^하/VV\+면/EC", None),
    "-ㄴ다는/-려는/-려던/ㄹ 계획이-": (r"(ㄹ|을|단|다는|ㄴ다는|려는|으려는|려던|으려던)/ETM$ ^계획/NNG", None),
    "-ㄴ다는/-려는/-려던/ㄹ 생각(이-)": (r"(ㄹ|을|려는|으려는|려던|으려던|자던|자는)/ETM$ ^생각/NNG\+(이/VCP|에/JKB|에서/JKB)", None),
    "-ㄴ데 반하여": (r"[ㄴ는]데/EC$ ^반하/VV\+아/EC", None),
    "-ㄴ데 비(해|하여)": (r"[ㄴ는]데/EC$ ^비/NNG\+하/XSV", None),
    "-ㄴ데도 불구하고": (r"(ㄴ데|는데)/EC\+도/JX$ ^불구하/VV", None),
    "-ㄹ 것(이라는|으로) 전망(이-|하-|되-)": (r"ETM$ ^[것거]/NNB ^전망/NNG", None),
    "-ㄹ 겨를이 없-": (r"ETM$ ^겨를/NNB ^없(/VA|이/MAG)", None),
    "-ㄹ 나위(가) 없-": (r"ETM$ ^나위/NNB ^없(/VA|이/MAG)", None),
    "-ㄹ 녘에": (r"ETM$ ^녘/NNB", None),
    "-ㄹ 따름(이-)": (r"ETM$ ^따름/NNB", None),
    "-ㄹ 리(가) 없-": (r"ETM$ ^리/NNB ^없/VA", [(':possibility', '-')]),
    "-ㄹ 리(가) 있-": (r"ETM$ ^리/NNB ^있/VA", None),
    "-ㄹ 리가 만무하-": (r"ETM$ ^리/NNB ^만무/NNG", [(':possibility', '-')]),
    "-ㄹ 만도 하-": (r"ETM$ ^만/NNB\+도/JX$ ^하/V", None),
    "-ㄹ 만하-": (r"ETM$ ^만/NNB\+하/XSA", None),
    "-ㄹ 무렵(에)": (r"ETM$ ^무렵/NNB", None),
    "-ㄹ 방침이-": (r"ETM$ ^방침/NNG", None),
    "-ㄹ 법도 하-": (r"ETM$ ^법/NNB\+도/JX$ ^하/VV", None),
    "-ㄹ 뻔(하-)": (r"ETM$ ^뻔/NNB", None),
    "-ㄹ 뿐(더러/이-)": (r"ETM$ ^뿐/NNB", None),
    "-ㄹ 뿐(만) 아니라": (r"ETM$ ^뿐/NNB ^아니/VCN", None),
    "-ㄹ 수 없-": (r"ETM$ ^수/NNB ^없/VA", [(':possibility', '-')]),
    "-ㄹ 수 있-": (r"ETM$ ^수/NNB ^있/VA", [(':possibility', '+')]),
    "-ㄹ 수밖에 없-": (r"ETM$ ^수/NNB\+밖에/JX ^없/VA", None),
    "-ㄹ 시(에)": (r"ETM$ ^시/NNB", None),
    "-ㄹ 예정이-": (r"[ㄹ을]/ETM$ ^예정/NNG", None),
    "-ㄹ 작정이-": (r"ETM$ ^작정/NNG", None),
    "-ㄹ 적에": (r"ETM$ ^적/NNB", None),
    "-ㄹ 전망이-": (r"[ㄹ을]/ETM$ ^전망/NNG", None),
    "-ㄹ 정도(이-)": (r"[ㄹ을]/ETM$ 정도/NNG", None),
    "-ㄹ 줄(을) 모르-": (r"[ㄹ을]/ETM$ ^줄/NNB ^모르/VV", None),
    "-ㄹ 줄(을) 알-": (r"[ㄹ을]/ETM$ ^줄/NNB ^알/VV", None),
    "-ㄹ 턱(이) 없-": (r"ETM$ ^턱/NNB ^없/VA", None),
    "-ㄹ/-던/-려던 때": (r"(ㄹ|을|던|려던)/ETM$ ^때/NNG", None),
    "-ㄹ까 보-": (r"[ㄹ을]까/EF$ ^보/V", None),
    "-ㄹ까 싶-": (r"[ㄹ을]까/EF$ ^싶/VX", None),
    "-ㄹ까 하-": (r"[ㄹ을]까/EF$ ^하/VV", None),
    "-ㄹ지 모르-": (r"[ㄹ을]지/EF ^모르/VV", None),
    "-게 되-": (r"게/EC$ ^되/VV", None),
    "-게 마련이-": (r"게/EC$ ^마련/NNB", None),
    "-게 만들-": (r"게/EC$ ^만들/VV", None),
    "-게 하-": (r"(VV|롭/XSA)\+게/EC$ ^하/VV", None),
    "-고 계시-": (r"고/EC$ ^계시/VX", None),
    "-고 나-": (r"고/EC$ ^나/VX", None),
    "-고 들-": (r"고/EC$ ^들/VX", None),
    "-고 말-": (r"고/EC$ ^말/VX", None),
    "-고 보-": (r"고/EC$ ^보/VX", None),
    "-고 싶-": (r"고/EC$ ^싶/VX", None),
    "-고 있-": (r"고/EC$ ^있/VX", None),
    "-고 있음에도": (r"고/EC$ ^있/VX\+음/ETN\+에/JKB\+도/JX", None),
    "-고 해서": (r"\+고/EC$ ^하/VX\+아서/EC", None),
    "-고는 하-": (r"고는/EC$ ^하/VX", None),
    "-고도 남-": (r"(고도/EC|고/EC\+도/JX)$ ^남/V", None),
    "-고자 하-": (r"고자/EC$ ^하/VX", None),
    "-기 그지없-": (r"기/ETN$ ^그지없/VA", None),
    "-기 나름이-": (r"기/ETN$ ^나름/NNB", None),
    "-기 때문(이-)": (r"기/ETN$ ^때문/NNB", None),
    "-기 마련이-": (r"기/ETN$ ^마련/NNB", None),
    "-기 망정이-": (r"기/ETN$ ^망정/NNB", None),
    "-기 바라-": (r"기/ETN ^바라/VV", None),
    "-기 쉽-": (r"기/ETN ^쉽/VA", None),
    "-기 시작하-": (r"기/ETN ^시작/NNG", None),
    "-기 십상이-": (r"기/ETN ^십상/NNG", None),
    "-기 어렵-": (r"기/ETN ^어렵/VA", None),
    "-기 예사이-": (r"기/ETN ^예사/NNG", None),
    "-기 원하-": (r"기/ETN ^원하/VA", None),
    "-기 위하-": (r"기/ETN ^위하/VV", None),
    "-기 이전에": (r"기/ETN$ ^이전/NNG", None),
    "-기 일쑤이-": (r"기/ETN ^일쑤/NNG", None),
    "-기 짝이 없-": (r"기/ETN ^짝/NNG\+이/JKS$ ^없/VA", None),
    "-기 틀리-": (r"기/ETN ^틀리/VV", None),
    "-기(가) 무섭게": (r"기/ETN ^무섭/VA\+게/EC$", None),
    "-기(에) 따라": (r"기/ETN ^따르/VV", None),
    "-기(에) 앞서": (r"기/ETN ^앞서/(VV|MAG)", None),
    "-기가 바쁘게": (r"기/ETN ^바쁘/VA", None),
    "-기가 이를 데 없-": (r"기/ETN$ ^이르/VV\+ㄹ/ETM$ ^데/NNB ^없/VA", None),
    "-기까지 하-": (r"기/ETN\+까지/JX$ ^하/VX", None),
    "-기나 하-": (r"기/ETN\+나/JX$ ^하/VX", None),
    "-기는 하-": (r"기/ETN\+는/JX$ ^하/VX", None),
    "-기도 하-": (r"기/ETN\+도/JX$ ^하/VX", None),
    "-기로 하-": (r"기/ETN\+로/JKB$ ^하/VV", None),
    "-기만 하-": (r"기/ETN\+만/JX$ ^하/V", None),
    "-나 보-": (r"나/(EC/EF)$ ^보/(VX|VV)", None),
    "-나 싶-": (r"나/(EC/EF)$ ^보/VX", None),
    "-는 하-": (r"는/JX$ ^하/VX", None),
    "-다 못하-": (r"다/EC$ ^못하/VX", None),
    "-다 보-": (r"다/EC$ ^보/VX", None),
    "-다/라는 전망(이-)": (r"(다는|ㄴ다는|리란|으리란|리라는|으리라는)/ETM$ ^전망/NNG", None),
    "-도록 하-": (r"도록/EC$ ^하/VX", None),
    "-려(고) 들-": (r"려고?/EC$ ^들/VX", None),
    "-려고 하-": (r"(려고|으려고)/EC$ ^하/VX", None),
    "-로(서)는 처음으로": (r"으?로서/JKB\+[ㄴ는]/JX$ ^처음/NNG", None),
    "-로 인하-": (r"로/JKB$ ^인/NNG\+하/XSV", None),
    "-를 거치-": (r"JKO$ ^거치/VV", None),
    "-를 놓고": (r"JKO$ ^놓/VV\+고/EC", None),
    "-를 두고": (r"JKO$ ^두/VV\+고/EC", None),
    "-만에 처음으로": (r"만/NNB\+에/JKB$ ^처음/NNG", None),
    "-면 안 되-": (r"으?면/EC$ ^안/MAG$ ^되/VV", None),
    "-면 좋-": (r"면/EC$ ^좋/VA", None),
    "-서는 한이 없-": (r"서/EC\+는/JX$ ^한/NNG\+이/JKS$ ^없/VA", None),
    "-어 가-": (r"[아어]/EC$ ^가/VX", None),
    "-어 가지고": (r"[아어]/EC$ ^가지/VX", None),
    "-어 계시-": (r"[아어]/EC$ ^계시/VX", None),
    "-어 나가-": (r"[아어]/EC$ ^나가/VX", None),
    "-어 내-": (r"[아어]/EC$ ^내/VX", None),
    "-어 놓-": (r"[아어]/EC$ ^놓/VX", None),
    "-어 달-": (r"[아어]/EC$ ^달/VX", None),
    "-어 대-": (r"[아어]/EC$ ^대/VX", None),
    "-어 두-": (r"[아어]/EC$ ^두/VX", None),
    "-어 드리-": (r"[아어]/EC$ ^드리/VX", None),
    "-어 들-": (r"[아어]/EC$ ^들/VX", None),
    "-어 마지않-": (r"[아어]/EC$ ^마지않/VX", None),
    "-어 먹-": (r"[아어]/EC$ ^먹/VX", None),
    "-어 버릇하-": (r"[아어]/EC$ ^버릇하/VX", None),
    "-어 버리-": (r"[아어]/EC$ ^버리/VX", None),
    "-어 보-": (r"[아어]/EC$ ^보/VX", None),
    "-어 보이-": (r"[아어]/EC$ ^보이/VV", None),
    "-어 오-": (r"[아어]/EC$ ^오/VX", None),
    "-어 있-": (r"[아어]/EC$ ^있/VX", None),
    "-어 주-": (r"[아어]/EC$ ^주/VX", None),
    "-어 죽겠-": (r"[아어]/EC$ ^죽/VV\+겠/EP", None),
    "-어 지-": (r"[아어]/EC$ ^지/VV", None),
    "-어 치우-": (r"[아어]/EC$ ^치우/VX", None),
    "-어도 되-": (r"[아어]도/EC$ ^되/VV", None),
    "-어도 좋-": (r"[아어]도/EC$ ^좋/VA", None),
    "-어야 되-": (r"[아어]야/EC$ ^되/VV", None),
    "-어야 하-": (r"[아어]야/EC$ ^하/VX", None),
    "-에 관하-": (r"에/JKB$ ^관하/VV", None),
    "-에 대하-": (r"에/JKB$ ^대하/VV", None),
    "-에 따라": (r"에/JKB$ ^따르/VV\+아/EC", None),
    "-에 따르면": (r"에/JKB$ ^따르/VV\+면/EC", None),
    "-에 비해": (r"에/JKB$ ^비/NNG\+하/XSV\+아/EC", None),
    "-에도 불구하고": (r"에/JKB\+도/JX$ ^불구하/VV", None),
    "-에서(는) 처음(으로)": (r"에서/JKB(\+[ㄴ는]/JX)?$ ^처음/NNG", None),
    "-와/과 다르게": (r"[와과]/JKB$ ^다르/VA\+게$", None),
    "-와/과 달리": (r"[와과]/JKB$ ^달리/MAG", None),
    "-와/과 동시에": (r"[와과]/JKB$ ^동시/NNG\+에/JKB", None),
    "-와/과 함께": (r"[와과]/JKB$ ^함께/MAG(\+,/SP)?$", None),
    "-으면 하-": (r"으면/EC$ ^하/VX", None),
    "-을 대상으로": (r"JKO$ 대상/NNG\+으로/JKB", None),
    "-을 마지막으로": (r"JKO$ 마지막/NNG\+으로/JKB", None),
    "-을 시작으로": (r"JKO$ 시작/NNG\+으로/JKB", None),
    "-을 위하-": (r"JKO$ ^위하/VV", None),
    "-을 향해/하여": (r"JKO$ ^향하/VV\+아/EC", None),
    "-을 통해": (r"JKO$ ^통하/VV", None),
    "-을 포함": (r"JKO$ ^포함/NNG", None),
    "-을/를 끝으로": (r"JKO$ 끝/NNG\+으로/JKB", None),
    "-의 경우": (r"의/JKG$ ^경우/NNG", None),
    "-이 아니-": (r"이/JKS$ ^아니/VCN", [(':polarity', '-')]),
    "-지 말-": (r"지/EC$ ^말/VX", [(':polarity', '-')]),
    "-지 못하-": (r"지/EC$ ^못하/VX", [(':polarity', '-')]),
    "-지 싶-": (r"지/EC$ ^싶/VX", None),
    "-지 않-": (r"지/EC$ ^않/VX", [(':polarity', '-')]),
    "~ 기준": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^기준/NNG", None),
    "~ 대비": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^대비/NNG", None),
    "~ 도중": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^도중/NNG", None),
    "~ 동안": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^동안/NNG", None),
    "~ 등": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^등/NNB", None),
    "~ 따위": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^따위/NNB", None),
    "~ 때문에": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|XSN)$ ^때문/NNB", None),
    "~ 미만": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^미만/NNG", None),
    "~ 뿐": (r"(NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^뿐/NNB", None),
    "~ 시": (r"(NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^시/NNB", None),
    "~ 이내": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이내/NNG", None),
    "~ 이상": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이상/NNG", None),
    "~ 이외": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이외/NNG", None),
    "~ 이유로": (r"[을를]/JKO$ ^이유/NNG\+로/JKB", None),
    "~ 이전": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이전/NNG", None),
    "~ 이하": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이하/NNG", None),
    "~ 이후": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^이후/NNG", None),
    "~ 전": (r"(NP|NNG|NNB|MMD|ETN|XSN)$ ^전/NNG", None),
    "~ 중": (r"(NP|NR|NNB|NNG|MMD|MAG|SN|SW|ETN|XSN)$ ^중/NNB", None),
    "~ 직전": (r"(NP|NNG|ETN|XSN)$ ^직전/NNG", None),
    "~ 직후": (r"(NP|NNG|ETN|XSN)$ ^직후/NNG", None),
    "~ 후": (r"(NP|NNG|NNB|MMD|ETN|XSN)$ ^후/NNG", None),
    "~ 씨": (r"NNP$ ^씨/NNB", None)
}


def prioritize(rules: dict[str, tuple[str, Any]], sort: Literal['simple-to-complex', 'complex-to-simple']):
    assert sort in ('simple-to-complex', 'complex-to-simple')
    assert len(rules.keys()) == len(rules.values())
    reverse = False if sort == 'simple-to-complex' else True
    ngram_ranks = defaultdict(list)
    for key, (regex, guide) in rules.items():
        ngram_ranks[len(regex.split())].append(key)
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

    def __init__(self, sort: Literal['simple-to-complex', 'complex-to-simple'] = 'simple-to-complex'):
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
