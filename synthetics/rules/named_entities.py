"""
reference: 국립국어원 <2021년 개체명 분석 및 개체 연결 말뭉치 연구 분석>

`ne`: Referring expressions of named-entities, proper names of instances or singletons
    - `class`, `type` 또는 `species`의 이름이 아닌 `instance`의 이름 또는 이명
    ex) 아인슈타인(Person), 러시아(GPE), 지구(Planet), 6.25(Event), 언어학(Field of studies), 신라면(Food-product)

# ge: name of class or species, generic name
    - `instantiatable`의 이름 또는 이명. 즉, `class`, `type` 또는 `species`의 이름
    - 개별 instance의 이름을 짓지 않는 관습이 지배적이거나, 특정 subclass를 구분짓기 위한 목적의 이름
    ex) 사과(Subclass of Fruit), PHEV(Subclass of Vehicle), 한국인(Subtype of ethnic groups), 반달가슴곰(Species of Animal)

# tm: general terms for (abstract) concept? terminologies?
    - conceptual referring
"""
from synthetics.primitives.amr.concept import AMRNamedEntityConcept
from synthetics.primitives.amr.concept import AMRGenericNameConcept
from synthetics.primitives.amr.concept import AMRTerminologyConcept


NAMED_ENTITIES = {
    # PERSON (PS) - 인명 및 인물의 별칭
    'PS_NAME': ('ne.person', AMRNamedEntityConcept),
    # ex. 흥선대원군, 아이유, 단군, 제우스, 돌부처, 쯔양, sojujsh
    'PS_CHARACTER': ('ne.fictitious-character*', AMRNamedEntityConcept),
    # ex. 뽀로로, 루피, 심슨, 엘사, 어피치, 라이언, 무지, 해리 포터, 유시진
    'PS_PET': ('ne.animal', AMRNamedEntityConcept),
    # ex. 뽀삐, 쿠키, 탄이, 절미, 달리, 김또또, 이뭉치

    # STUDY_FIELD (FD) - 학문 분야 및 학파명
    'FD_SCIENCE': ('tm.study-field*', AMRTerminologyConcept),
    # ex. 물리학, 생명과학, 수학, 기계공학, 수의학, 자동차공학, 전기공학
    'FD_SOCIAL_SCIENCE': ('tm.study-field*', AMRTerminologyConcept),
    # ex. 인류학, 사회학, 경제학, 정치학, 심리학/고전학파, 신고전학파
    'FD_MEDICINE': ('tm.study-field*', AMRTerminologyConcept),
    # ex. 의학, 병리학, 보건의료학, 신경과학/비뇨기과, 신경과, 내과
    'FD_ART': ('tm.study-field*', AMRTerminologyConcept),
    # ex. 문예학, 음악사학, 미술사학, 공연예술학/인상파, 점묘파, 신경향파
    'FD_HUMANITIES': ('tm.study-field*', AMRTerminologyConcept),
    # ex. 언어학, 철학, 국어국문학, 독어독문학/구조주의 언어학파, 아날학파
    'FD_OTHERS': ('tm.study-field*', AMRTerminologyConcept),
    # ex. 농학, 군사학, 가정학, 건강과학, 박물관학 등

    # THEORY (TR) - 특정 이론, 법칙, 원리
    'TR_SCIENCE': ('tm.theory*', AMRTerminologyConcept),
    # ex. 21세기형수학공식, 이진법, 원심분리법, 기체확산법
    'TR_SOCIAL_SCIENCE': ('tm.theory*', AMRTerminologyConcept),
    # ex. 민주주의, 공산주의, 노동가치설, 대화법, 법치주의, 평등주의, 애니미즘, 토테미즘, 샤머니즘
    'TR_MEDICINE': ('tm.theory*', AMRTerminologyConcept),
    # ex. 인공호흡, 요혈자극법, 바이오피드백
    'TR_ART': ('tm.theory*', AMRTerminologyConcept),
    # ex. 고딕양식, 고전주의, 몽타주, 오마주, 클로즈업 샷, 루즈샷, 다다이즘
    'TR_HUMANITIES': ('tm.theory*', AMRTerminologyConcept),
    # ex. 주지주의, 구조주의, 이기론, 관념론, 니힐리즘, 이데아설
    'TR_OTHERS': ('tm.theory*', AMRTerminologyConcept),
    # ex. 교통류 이론, 자동초록기법, 텍스트 마이닝 기법

    # ARTIFACTS (AF) - 사람에 의해 창조된 인공물
    'AF_BUILDING': ('ne.facility', AMRNamedEntityConcept),
    # ex. 대한생명 63빌딩, 동대문운동장, 서해대교, 롯데월드타워
    'AF_CULTURAL_ASSET': ('ne.cultural-asset*', AMRNamedEntityConcept),
    # ex. 숭례문, 천마총, 불국사, 서울 원각사지 십층석탑, 에펠탑, 미디 운하
    'AF_ROAD': ('ne.road|railway-line', AMRNamedEntityConcept),
    # ex. 세종로, 올림픽대로, 삼성로1길, 충북선, 경부선
    'AF_TRANSPORT': ('ne.transportation*', AMRNamedEntityConcept),
    # ex. 갈라테아호, 경비정, 벤츠, 자기부상열차
    'AF_MUSICAL_INSTRUMENT': ('ge.musical-instrument*', AMRGenericNameConcept),
    # ex. 기타, 캐스터네츠, 편경, 꽹과리, 대금, 해금, 신시사이저
    'AF_WEAPON': ('ge.weapon*', AMRGenericNameConcept),
    # ex. 기관단총, 시한폭탄, 곡사포, 고정포, 탄도미사일, 도끼, 칼
    'AF_ART_WORKS': ('ne.work-of-art', AMRNamedEntityConcept),
    # 작품명 (예시 없음)
    'AFA_DOCUMENT': ('ne.publication', AMRNamedEntityConcept),
    # ex. 대동여지도, 동의보감, 한역대장경, 반지의 제왕
    'AFA_PERFORMANCE': ('ne.work-of-art', AMRNamedEntityConcept),
    # ex. 농악무, 백조의 호수, 명성황후, 캐츠
    'AFA_VIDEO': ('ne.work-of-art', AMRNamedEntityConcept),
    # ex. 기생충, 아빠어디가, CJ홈쇼핑, KBS2TV
    'AFA_ART_CRAFT': ('ne.work-of-art', AMRNamedEntityConcept),
    # ex. 생각하는 사람, 도산도, 게르니카, 지옥의 문
    'AFA_MUSIC': ('ne.music', AMRNamedEntityConcept),
    # 돈 카를로스, 아이다, 카르멘, 한국환상곡, 보태평
    'AF_WARES': ('ne.product', AMRNamedEntityConcept),
    # 판매되는 상품 및 제품 (예시 없음)
    'AFW_SERVICE_PRODUCTS': ('ne.service-product*', AMRNamedEntityConcept),
    # ex. 우리희망드림적금, 에어비앤비, 동유럽 발칸 일주 9일
    'AFW_OTHER_PRODUCTS': ('ne.product', AMRNamedEntityConcept),
    # ex. 포스트잇, 에어조던 원, 그린터치 물티슈

    # ORGANIZATION (OG) - 기관 및 단체
    'OGG_ECONOMY': ('ne.company', AMRNamedEntityConcept),
    # ex. 삼성전자, 현대자동차, LG그룹, OECD, 동양증권
    'OGG_EDUCATION': ('ne.university|school', AMRNamedEntityConcept),
    # ex. 밀알유치원, 서울대학교, 청담어학원, 논산훈련소, 국제한국어교육학회
    'OGG_MILITARY': ('ne.military', AMRNamedEntityConcept),
    # ex. 해군, 공군, 육군, 인민군, 해군기지, 국방품질관리소, 한미연합사령부
    'OGG_MEDIA': ('ne.company', AMRNamedEntityConcept),
    # ex. KBS, MBC, TJB, 한국일보, 씨네 21, 공익광고협의회, 월스트리트저널, AP통신
    'OGG_SPORTS': ('ne.team|league', AMRNamedEntityConcept),
    # ex. 국민체육진흥심의위원회, 국기원, 국군체육부대, 맨체스터 유나이티드
    'OGG_ART': ('ne.organization', AMRNamedEntityConcept),
    # ex. 독일디자인협회, 루브르박물관, 예술의 전당, 리움미술관, 대한극장
    'OGG_MEDICINE': ('ne.organization', AMRNamedEntityConcept),
    # ex. 세계보건기구, KMI한국의학연구소, 삼성서울병원, 경희한의원, 새봄약국
    'OGG_RELIGION': ('ne.religious-group', AMRNamedEntityConcept),
    # ex. 기독교, 불교, 증산도, 대한성공회, 한국기독교장로회, 장로교, 성결교, 화엄종
    'OGG_SCIENCE': ('ne.research-institute', AMRNamedEntityConcept),
    # ex. 국제전기통신연합, 한국표준과학연구원, 한국에너지기술연구원
    'OGG_LIBRARY': ('ne.library*', AMRNamedEntityConcept),
    # ex. 국립중앙도서관, 국회도서관, 바티칸도서관, 법학전문도서관, 일송도서관
    'OGG_LAW': ('ne.government-organization', AMRNamedEntityConcept),
    # ex. 광주지방법원, 대한법무사협회, 저작권심의조정위원회
    'OGG_POLITICS': ('ne.government-organization', AMRNamedEntityConcept),
    # ex. 청와대, 국회, 대사관, 미래부, 정보통신부, 정부, 우체국, 경찰서, 소방서
    'OGG_FOOD': ('ne.company', AMRNamedEntityConcept),
    # ex. 맥도날드, 김밥천국, 롯데리아, 맘스터치, 스타벅스, 파리바게트
    'OGG_HOTEL': ('ne.hotel', AMRNamedEntityConcept),
    # ex. 신라호텔, 한화콘도, 대명리조트, 워커힐, 호텔신라, 백담사산장
    'OG_OTHERS': ('ne.organization', AMRNamedEntityConcept),
    # ex. 유색인종향상전국협회, 녹색연합, 참여연대, 블링크, 원잇(ONE IT), 아미

    # LOCATION (LC) - 지역/장소, 지형/지리
    'LCP_COUNTRY': ('ne.country', AMRNamedEntityConcept),
    # ex. 한국, 미국, 독일, 프랑스, 터키, 러시아, 가나
    'LCP_PROVINCE': ('ne.province|state', AMRNamedEntityConcept),
    # ex. 경기도, 제주도, 충청도, 강원도, 전라도, 경상도, 텍사스주
    'LCP_COUNTY': ('ne.county', AMRNamedEntityConcept),
    # ex. 영월군, 도암면, 횡계리, 노암동
    'LCP_CITY': ('ne.city', AMRNamedEntityConcept),
    # ex. 강릉, 부산, 태백, 뉴욕, 맨체스터, 덴버, 요코하마, 이스탄불
    'LCP_CAPITALCITY': ('ne.city', AMRNamedEntityConcept),
    # ex. 서울, 베이징, 런던, 파리, 워싱턴 D.C., 오타와, 캔버라
    'LCG_RIVER': ('ne.river|lake', AMRNamedEntityConcept),
    # ex. 한강, 섬진강, 춘천호, 아산호, 청계천, 중랑천, 관곡지, 예당저수지
    'LCG_OCEAN': ('ne.ocean|sea|strait|canal', AMRNamedEntityConcept),
    # ex. 남극해, 북극해, 동해, 태평양, 산호해
    'LCG_BAY': ('ne.gulf|bay|peninsula', AMRNamedEntityConcept),
    # ex. 라몬만, 랴오둥반도, 변산반도, 도쿄만
    'LCG_MOUNTAIN': ('ne.mountain|volcano', AMRNamedEntityConcept),
    # ex. 라우산, 태백산맥, 차령산맥, 계룡산, 공룡능선, 박달재
    'LCG_ISLAND': ('ne.island', AMRNamedEntityConcept),
    # ex. 나이팅게일섬, 로스제도, 백령도, 독도
    'LCG_CONTINENT': ('ne.world-region|continent', AMRNamedEntityConcept),
    # ex. 아시아, 아프리카, 아메리카, 오세아니아, 유라시아, 유럽
    'LC_SPACE': ('ne.moon|planet|star|constellation', AMRNamedEntityConcept),
    # ex. 태양, 달, 지구, 수성, 모어하우스혜성, 핼리혜성, 전갈자리, 고리성운
    'LC_OTHERS': ('ne.local-region', AMRNamedEntityConcept),
    # ex. 서울역, 신도림역, 인천국제공항, 서울남부터미널, 국립수목원, 금강휴게소

    # CIVILIZATION (CV) - 문명/문화
    'CV_NAME': ('ne.nationality|ethnic-group', AMRNamedEntityConcept),
    # ex. 인더스문명, 황허문명, 거석문화, 도싯문화, 4차산업혁명, 르네상스
    'CV_TRIBE': ('ne.nationality|ethnic-group', AMRNamedEntityConcept),
    # ex. 이라크족, 유대인, 조선족, 마오리족, 아메리카인디언
    'CV_LANGUAGE': ('ne.language', AMRNamedEntityConcept),
    # ex. 한국어, 아랍어, 프랑스어, 산스크리트
    'CV_POLICY': ('ne.program|policy*', AMRNamedEntityConcept),
    # ex. 카스트, 쓰레기종량제, 직업공무원제도, 연금제도, 고시제도
    'CV_LAW': ('ne.law|treaty', AMRNamedEntityConcept),
    # ex. 국제연합헌장, 민법, 형법, 함무라비법전, 관습법, 헌법

    'CV_CURRENCY': 'currency*',   # ex. 달러, 원, 엔, 유로, 루피, 위안
    'CV_TAX': 'tax*',   # ex. 법인세, 소득공제, 면허세, 관세, 부가가치세
    'CV_FUNDS': 'funds*',   # ex. 거치연금, 문예진흥기금, 공적자금, 퇴직연금, 코리아 펀드
    'CV_ART': None,   # ex. 소설, 시, 판타지소설, 판소리, 힙합, 케이팝, 공포영화, 미국드라마
    'CV_SPORTS': 'sports*',   # ex. 축구, 야구, 수상스키, 스키, 스케이팅, 하이킹, 행글라이딩
    'CV_SPORTS_POSITION': 'have-org-role-91',   # ex. 투수, 포수, 스트라이커, 골키퍼, 미드필더
    'CV_SPORTS_INST': 'sports-instrument*',   # ex. 스케이트, 인라인스케이트, 야구공, 배트, 아이젠, 오리발
    'CV_PRIZE': 'award',   # ex. 노벨경제학상, 대통령상, 대종상, 다승왕, 타격왕
    'CV_RELATION': 'have-rel-role-91',   # ex. 엄마, 아버지, 가족, 형제, 제자, 아들, 딸, 자식, 친척
    'CV_OCCUPATION': 'have-org-role-91',   # ex. 화가, 극작가, 건축가, 가정교사, 언어학자, 공인중개사
    'CV_POSITION': 'have-org-role-91',   # ex. 부장, 과장, 대리, 대위, 중위, 소위, 대통령, 국무총리, 장관
    'CV_FOOD': 'food-dish',   # ex. 소고기, 소금, 명란젓, 국수, 김치, 나물, 된장찌개, 1955버거, 맵슐랭치킨
    'CV_DRINK': 'food-drink*',   # ex. 물, 우유, 주스, 홍차, 레모네이드, 칵테일, 위스키, 레드불
    'CV_FOOD_STYLE': 'food-style*',   # ex. 한식, 양식, 중식, 보양식, 패스트푸드
    'CV_CLOTHING': 'clothing*',   # ex. 모시, 메리야스, 와이셔츠, 레이온, 양모, 점퍼
    'CV_BUILDING_TYPE': 'architectural-style*',   # ex. 기능주의건축, 노르만양식, 시토파건축, 도리스양식

    # DATE (DT) - 기간 및 계절, 시기/시대
    'DT_DURATION': 'temporal-quantity|date-interval',   # ex. ~부터 ~까지, ~ 간, 전반기/후반기, 성수기/비수기
    'DT_DAY': 'date-entity',   # ex. 입춘, 곡우, 내일, 모레, 금일, 당일, 29일
    'DT_WEEK': 'date-entity',   # ex. 지난주, 이번 주, 다음 주, 첫 주, 둘째 주
    'DT_MONTH': 'date-entity',   # ex. 이달, 지난달, 4월, 10월
    'DT_YEAR': 'date-entity',   # ex. 작년, 내년, 올해, 서기 2910년, 영락1년
    'DT_SEASON': 'date-entity',   # ex. 봄, 여름, 가을, 겨울, 춘계, 하계, 추계, 동계
    'DT_GEOAGE': 'geoage',   # ex. 원시시대, 구석기시대, 캄브리아기, 중생대, 원생대, 선사시대
    'DT_DYNASTY': 'dynasty',   # ex. 청대, 조선시대, 조선 후기, 명대, 고려시대, 고려 말
    'DT_OTHERS': 'date-entity',   # ex. ~년 후/전, ~부터/까지/정도, ~세기, ~때

    # TIME (TI) - 시계상으로 나타나는 시/시각, 시간 범위
    'TI_DURATION': 'temporal-quantity|date-interval',   # ex. 6시~9시, 낮, 밤, 점심, 저녁, 오전, 오후, 밤낮
    'TI_HOUR': 'date-entity',   # ex. 12시, 저녁 8시
    'TI_MINUTE': 'date-entity',   # ex. 13분, 30분, 29분
    'TI_SECOND': 'date-entity',   # ex. 27초, 15초, 30초
    'TI_OTHERS': 'date-entity',   # ex. 3시 이전, 8시 20분, 6시까지

    # QUANTITY (QT) - 수량/분량, 순서/순차, 수사로 이루어진 표현
    'QT_AGE': 'age-01, temporal-quantity',   # ex. 만 55세, 50~60대, 생후 10주, 3개월령
    'QT_SIZE': 'area-quantity',   # ex. 1제곱미터(㎡), 1아르(a), 1헥타르(ha), 9, 606.33㎢
    'QT_LENGTH': 'distance-quantity',   # ex. 0.76mm, 900m, 8km, 82피트
    'QT_COUNT': 'quantity*',   # ex. 6개, 8백 70선, 하나, 둘
    'QT_MAN_COUNT': 'quantity*',   # ex. 한 명, 두 사람, 3명, 열댓 명
    'QT_WEIGHT': 'mass-quantity',   # ex. 30kg, 140q, 백 근, 9만 t, 85~100kg, 60q, 5만 톤, 170t
    'QT_PERCENTAGE': 'percentage-entity',   # ex. 약 75%, 8~12ppm, 4배, 400~500ppm, 1/3, 절반 이상
    'QT_SPEED': 'acceleration-quantity',   # ex. 1km/s, 30km/s
    'QT_TEMPERATURE': 'temperature-quantity',   # ex. 22~25℃, 41~43.5˚
    'QT_VOLUME': 'volume-quantity',   # ex. 두 말, 2홉, 20ℓ, 2되, 2만 2000㎦
    'QT_ORDER': 'ordinal-entity',   # ex. 1위, 3수, 100주년, 제10회, 3학년, 제10회, 제2대
    'QT_PRICE': 'monetary-quantity',   # ex. 72만 원, 60억 달러
    'QT_PHONE': 'phone-number-entity',   # ex. 042-101-1010, 114, 112, 119, 1588-1588, 031, 02, 001, 00700
    'QT_SPORTS': 'score-entity :op1 :op2',   # ex. 1승2패, 5타점, 3:2, 2연승, 6이닝, 1볼넷, 6오버파
    'QT_CHANNEL': 'media-channel*',   # ex. 2채널, FM 98.1, 91.9, 95.9 MHz
    'QT_ALBUM': 'ordinal-entity',   # ex. 1집, 1.5집, Ⅵ, part 1, vol. 2
    'QT_ADDRESS': 'street-address-91',   # ex. 110-704, 200-776, 24457, 32호, 179번지, 668-4
    'QT_OTHERS': 'quantity*',   # ex. 45점, 100점, 지식머니 20, 북위 38도, 53' 51, 2960X1440

    # EVENT (EV) - 특정 사건/사고/행사 명칭
    'EV_ACTIVITY': 'political-movement',   # ex. 공민권운동, 브나로드운동, 노예해방선언, 인권선언, 밀라노칙령
    'EV_WAR_REVOLUTION': 'war',   # ex. 러일전쟁, 남북전쟁, 청교도혁명, 4.19혁명, 명량해전, 516 쿠데타
    'EV_SPORTS': 'game',   # ex. 올림픽경기대회, 서울올림픽, 오버워치리그, 태권도 대회
    'EV_FESTIVAL': 'festival',   # ex. 이천도자기축제, 칸 영화제, 방탄 콘서트, 책 읽는 춘천, 서울 패션 위크
    'EV_OTHERS': 'event',   # ex. 세월호 참사, 다보스포럼, 키스해링전, 월드바리스타챔피언쉽

    # ANIMAL (AM) - 사람을 제외한 짐승
    'AM_INSECT': 'animal*',   # ex. 벼메뚜기, 가시거미, 지네, 불나방, 배추흰나비, 참매미
    'AM_BIRD': 'animal*',   # ex. 왜가리, 뻐꾸기, 거위, 두루미, 황새
    'AM_FISH': 'animal*',   # ex. 참가자미, 전기뱀장어, 연어, 갈치, 멸치, 미꾸라지, 숭어, 날치
    'AM_MAMMALIA': 'animal*',   # ex. 해달, 토끼, 오소리, 돌고래, 박쥐, 고슴도치, 두더지
    'AM_AMPHIBIA': 'animal*',   # ex. 개구리, 두꺼비, 산개구리, 산청개구리, 도롱뇽, 맹꽁이
    'AM_REPTILIA': 'animal*',   # ex. 도마뱀, 거북, 자라, 구렁이, 백사, 공룡, 악어
    'AM_TYPE': 'animal*',   # ex. 강장동물, 구두동물, 극피동물, 내항동물, 모악동물, 선형동물
    'AM_PART': 'part-of',   # ex. 목, 살, 등, 배, 몸통, 손, 입, 갈기
    'AM_OTHERS': 'pathogen*',   # ex. 가재(절지동물), 문어, 오징어(연체동물)

    # PLANT (PT) - 꽃/나무, 육지식물, 해조류, 버섯류, 이끼류
    'PT_FRUIT': 'plant*',   # ex. 사과, 배, 자두, 바나나, 복숭아, 오렌지, 포도, 호두, 쌀, 보리
    'PT_FLOWER': 'plant*',   # ex. 저먼아이리스, 백합, 국화, 제비꽃, 히아신스, 초롱꽃, 할미꽃
    'PT_TREE': 'plant*',   # ex. 후박나무, 벚나무, 분비나무, 너도밤나무
    'PT_GRASS': 'plant*',   # ex. 향부자, 하늘타리뿌리, 인삼, 생강, 감자, 싱아, 갈대
    'PT_TYPE': 'plant*',   # ex. 장미목, 이판화군, 외떡잎식물, 붓꽃과, 백합목, 낙엽교목
    'PT_PART': 'part-of',   # ex. 뿌리, 가지, 가시, 꽃, 꽃잎, 꽃봉오리, 꽃수술, 꽃받침, 씨앗
    'PT_OTHERS': 'plant*',   # ex. 우산이끼, 송이버섯, 김, 미역, 매생이, 선인장, 콩나물

    # MATERIAL (MT) - 원소 및 금속, 암석/보석, 화학 물질
    'MT_ELEMENT': 'material*',   # ex. 이테르븀, 프로메튬, 디스프로슘, 셀렌, 헬륨
    'MT_METAL': 'material*',   # ex. 황산철, 알루미늄, 아연, 구리, 수은, 아말감
    'MT_ROCK': 'material*',   # ex. 화강암, 흑운모화강암, 진사, 역암, 사암, 편암, 편마암
    'MT_CHEMICAL': 'material*',   # ex. 암모니아, 과산화수소, 에탄올, 황화수소, 네온, 일산화탄소, 헤모글로빈, 비타민

    # TERM (TM) - 위에서 정의된 세부 개체명 이외의 개체명
    'TM_COLOR': 'color*',   # ex. 흰색, 흰빛, 흑색, 회색, 황, 홍색, 하늘색, 파란빛
    'TM_DIRECTION': 'direction',   # ex. 최북단, 중앙부, 중앙, 중부, 서쪽, 서부, 상부, 북쪽
    'TM_CLIMATE': 'climate*',   # ex. 아열대기후, 고산기후, 고지기후, 도시기후, 동안기후
    'TM_SHAPE': 'shape*',   # ex. 삼각형, 사각형, 팔각형, 일자형, 원통형, 삼각뿔 모양, 가로무늬, 구름무늬
    'TM_CELL_TISSUE_ORGAN': 'cell-tissue*',   # ex. 간상세포, 각막세포, 고막, 뉴런, 늑연골, 식도, 콩팥, 비장
    'TMM_DISEASE': 'desease',   # ex. 기침, 폐결핵, 기관지확장증, 레트증후군, 피고름가래
    'TMM_DRUG': 'drug*',   # ex. 헤파린, 근이완제, 모기향, 소화제, 아스피린, 구충제
    'TMI_HW': 'product',   # ex. 하드디스크드라이브, 마이크로프로세서, 롬, 디스켓, 소자 소켓, 감각 센서
    'TMI_SW': 'program',   # ex. 윈도우10, 리눅스, 반디집, 알송, 한컴오피스 한글, MS워드, 트로이목마, 자바
    'TMI_SITE': 'url-entity',   # ex. https://opendict.korean.go.kr/, https://www.korean.go.kr/
    'TMI_EMAIL': 'email-address-entity',   # ex. esuhyeon@glab.hallym.ac.kr
    'TMI_MODEL': 'product',   # ex. LM1000-2CX
    'TMI_SERVICE': 'service*',   # ex. 와이브로서비스, DMB서비스, 카카오톡, 인스타그램, 네이버, 다음, 구글
    'TMI_PROJECT': 'project*',   # ex. BrainKorea21, 4대강사업, 그린 IT 사업, 무료치과진료사업
    'TMIG_GENRE': 'genre*',   # ex. RPG, 실시간 전략 게임, 1인칭 슈팅 게임
    'TM_SPORTS': 'sports-term*'    # ex. 밀어내기 득점, 솔로 홈런, 바스켓카운트, 리바운드, 발리슛
}