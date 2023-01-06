# ne: named-entity, proper names, names of instance, singletons
# ge: name of class, generic nouns
# gc: general terms for concept, terminologies

NE_MAPPINGS = {
    # PERSON (PS) - 인명 및 인물의 별칭
    'PS_NAME': 'person',  # ex. 흥선대원군, 아이유, 단군, 제우스, 돌부처, 쯔양, sojujsh
    'PS_CHARACTER': 'fictitious-character*',  # ex. 뽀로로, 루피, 심슨, 엘사, 어피치, 라이언, 무지, 해리 포터, 유시진
    'PS_PET': 'companion-animal*',  # ex. 뽀삐, 쿠키, 탄이, 절미, 달리, 김또또, 이뭉치

    # STUDY_FIELD (FD) - 학문 분야 및 학파명
    'FD_SCIENCE': 'study-field|school*',  # ex. 물리학, 생명과학, 수학, 기계공학, 수의학, 자동차공학, 전기공학
    'FD_SOCIAL_SCIENCE': 'study-field|school*',  # ex. 인류학, 사회학, 경제학, 정치학, 심리학/고전학파, 신고전학파
    'FD_MEDICINE': 'study-field|school*',  # ex. 의학, 병리학, 보건의료학, 신경과학/비뇨기과, 신경과, 내과
    'FD_ART': 'study-field|school*',  # ex. 문예학, 음악사학, 미술사학, 공연예술학/인상파, 점묘파, 신경향파
    'FD_HUMANITIES': 'study-field|school*',  # ex. 언어학, 철학, 국어국문학, 독어독문학/구조주의 언어학파, 아날학파
    'FD_OTHERS': 'study-field|school*',  # ex. 농학, 군사학, 가정학, 건강과학, 박물관학 등

    # THEORY (TR) - 특정 이론, 법칙, 원리
    'TR_SCIENCE': 'theory*',  # ex. 21세기형수학공식, 이진법, 원심분리법, 기체확산법
    'TR_SOCIAL_SCIENCE': 'theory*',  # ex. 민주주의, 공산주의, 노동가치설, 대화법, 법치주의, 평등주의, 애니미즘, 토테미즘, 샤머니즘
    'TR_MEDICINE': 'theory*',  # ex. 인공호흡, 요혈자극법, 바이오피드백
    'TR_ART': 'theory*',  # ex. 고딕양식, 고전주의, 몽타주, 오마주, 클로즈업 샷, 루즈샷, 다다이즘
    'TR_HUMANITIES': 'theory*',  # ex. 주지주의, 구조주의, 이기론, 관념론, 니힐리즘, 이데아설
    'TR_OTHERS': 'theory*',  # ex. 교통류 이론, 자동초록기법, 텍스트 마이닝 기법

    # ARTIFACTS (AF) - 사람에 의해 창조된 인공물
    'AF_BUILDING': 'building',  # ex. 대한생명 63빌딩, 동대문운동장, 서해대교, 롯데월드타워
    'AF_CULTURAL_ASSET': 'cultural-asset*',  # ex. 숭례문, 천마총, 불국사, 서울 원각사지 십층석탑, 에펠탑, 미디 운하
    'AF_ROAD': 'road',  # ex. 세종로, 올림픽대로, 삼성로1길, 충북선, 경부선
    'AF_TRANSPORT': 'transportation*',  # ex. 갈라테아호, 경비정, 벤츠, 자기부상열차
    'AF_MUSICAL_INSTRUMENT': 'musical-instrument*',  # ex. 기타, 캐스터네츠, 편경, 꽹과리, 대금, 해금, 신시사이저
    'AF_WEAPON': 'weapon*',  # ex. 기관단총, 시한폭탄, 곡사포, 고정포, 탄도미사일, 도끼, 칼
    'AF_ART_WORKS': 'work-of-art',  # 작품명
    'AFA_DOCUMENT': 'publication',  # ex. 대동여지도, 동의보감, 한역대장경, 반지의 제왕
    'AFA_PERFORMANCE': 'show',  # ex. 농악무, 백조의 호수, 명성황후, 캐츠
    'AFA_VIDEO': 'movie',  # ex. 기생충, 아빠어디가, CJ홈쇼핑, KBS2TV
    'AFA_ART_CRAFT': 'picture',  # ex. 생각하는 사람, 도산도, 게르니카, 지옥의 문
    'AFA_MUSIC': 'music',  # 돈 카를로스, 아이다, 카르멘, 한국환상곡, 보태평
    'AF_WARES': 'product',  # 판매되는 상품 및 제품
    'AFW_SERVICE_PRODUCTS': 'service-product*',  # ex. 우리희망드림적금, 에어비앤비, 동유럽 발칸 일주 9일
    'AFW_OTHER_PRODUCTS': 'goods*',  # ex. 포스트잇, 에어조던 원, 그린터치 물티슈

    # ORGANIZATION (OG) - 기관 및 단체
    'OGG_ECONOMY': 'organization',  # ex. 삼성전자, 현대자동차, LG그룹, OECD, 동양증권
    'OGG_EDUCATION': 'university|school',  # ex. 밀알유치원, 서울대학교, 청담어학원, 논산훈련소, 국제한국어교육학회
    'OGG_MILITARY': 'military',  # ex. 해군, 공군, 육군, 인민군, 해군기지, 국방품질관리소, 한미연합사령부
    'OGG_MEDIA': 'company',  # ex. KBS, MBC, TJB, 한국일보, 씨네 21, 공익광고협의회, 월스트리트저널, AP통신
    'OGG_SPORTS': 'team',  # ex. 국민체육진흥심의위원회, 국기원, 국군체육부대, 맨체스터 유나이티드
    'OGG_ART': 'organization',  # ex. 독일디자인협회, 루브르박물관, 예술의 전당, 리움미술관, 대한극장
    'OGG_MEDICINE': 'organization',  # ex. 세계보건기구, KMI한국의학연구소, 삼성서울병원, 경희한의원, 새봄약국
    'OGG_RELIGION': 'religious-group',  # ex. 기독교, 불교, 증산도, 대한성공회, 한국기독교장로회, 장로교, 성결교, 화엄종
    'OGG_SCIENCE': 'organization',  # ex. 국제전기통신연합, 한국표준과학연구원, 한국에너지기술연구원
    'OGG_LIBRARY': 'library*',  # ex. 국립중앙도서관, 국회도서관, 바티칸도서관, 법학전문도서관, 일송도서관
    'OGG_LAW': 'government-organization',  # ex. 광주지방법원, 대한법무사협회, 저작권심의조정위원회
    'OGG_POLITICS': 'government-organization',  # ex. 청와대, 국회, 대사관, 미래부, 정보통신부, 정부, 우체국, 경찰서, 소방서
    'OGG_FOOD': 'company',  # ex. 맥도날드, 김밥천국, 롯데리아, 맘스터치, 스타벅스, 파리바게트
    'OGG_HOTEL': 'hotel',  # ex. 신라호텔, 한화콘도, 대명리조트, 워커힐, 호텔신라, 백담사산장
    'OG_OTHERS': 'organization',  # ex. 유색인종향상전국협회, 녹색연합, 참여연대, 블링크, 원잇(ONE IT), 아미

    # LOCATION (LC) - 지역/장소, 지형/지리
    'LCP_COUNTRY': 'country',  # ex. 한국, 미국, 독일, 프랑스, 터키, 러시아, 가나
    'LCP_PROVINCE': 'province',  # ex. 경기도, 제주도, 충청도, 강원도, 전라도, 경상도, 텍사스주
    'LCP_COUNTY': 'county',  # ex. 영월군, 도암면, 횡계리, 노암동
    'LCP_CITY': 'city',  # ex. 강릉, 부산, 태백, 뉴욕, 맨체스터, 덴버, 요코하마, 이스탄불
    'LCP_CAPITALCITY': 'city',  # ex. 서울, 베이징, 런던, 파리, 워싱턴 D.C., 오타와, 캔버라
    'LCG_RIVER': 'river',  # ex. 한강, 섬진강, 춘천호, 아산호, 청계천, 중랑천, 관곡지, 예당저수지
    'LCG_OCEAN': 'ocean',  # ex. 남극해, 북극해, 동해, 태평양, 산호해
    'LCG_BAY': 'bay',  # ex. 라몬만, 랴오둥반도, 변산반도, 도쿄만
    'LCG_MOUNTAIN': 'mountain',  # ex. 라우산, 태백산맥, 차령산맥, 계룡산, 공룡능선, 박달재
    'LCG_ISLAND': 'island',  # ex. 나이팅게일섬, 로스제도, 백령도, 독도
    'LCG_CONTINENT': 'continent',  # ex. 아시아, 아프리카, 아메리카, 오세아니아, 유라시아, 유럽
    'LC_SPACE': 'astronomical-object*',  # ex. 태양, 달, 지구, 수성, 모어하우스혜성, 핼리혜성, 전갈자리, 고리성운
    'LC_OTHERS': 'location',  # ex. 서울역, 신도림역, 인천국제공항, 서울남부터미널, 국립수목원, 금강휴게소

    'CV_SPORTS': 'sports*',
    'CV_SPORTS_INST': 'sports-instrument*',
    'CV_POLICY': 'policy*',
    'CV_TAX': 'tax*',
    'CV_FUNDS': 'funds*',
    'CV_BUILDING_TYPE': 'architectural-style*',
    'CV_FOOD': 'food-dish',
    'CV_DRINK': 'food-drink*',
    'CV_CLOTHING': 'clothing*',
    'CV_CURRENCY': 'currency*',
    'CV_FOOD_STYLE': 'food-style*',


    'MT_ELEMENT': 'material*', 'MT_METAL': 'material*', 'MT_ROCK': 'material*', 'MT_CHEMICAL': 'material*',
    'TM_COLOR': 'color*', 'TM_CLIMATE': 'climate*', 'TM_SHAPE': 'shape*', 'TM_CELL_TISSUE': 'cell-tissue*',
    'TMI_HW': 'product', 'TMI_GENRE': 'genre*', 'TM_SPORTS': 'sports-term*',

    'CV_NAME': 'ethnic-group',
    'CV_TRIBE': 'ethnic-group',
    'CV_LANGUAGE': 'language',
    'CV_PRIZE': 'award',
    'CV_LAW': 'law',
    'EV_OTHERS': 'event',
    'EV_ACTIVITY': 'political-movement',
    'EV_WAR_REVOLUTION': 'war',
    'EV_SPORTS': 'game',
    'EV_FESTIVAL': 'festival',
    'TMI_MODEL': 'product',
    'TMI_SW': 'program',
    'TMI_SERVICE': 'service*',
    'TMI_PROJECT': 'project*',
    'TMM_DISEASE': 'desease',
    'TMM_DRUG': 'drug*',
    'QT_CHANNEL': 'media-channel*',

}
