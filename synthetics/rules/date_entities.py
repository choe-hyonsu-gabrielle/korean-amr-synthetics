import re
from synthetics.utils.kr2num import kr2num

GENERAL_DATE_CONCEPTS = [
    '공휴일', '휴일', '평일',
]
NAMED_DATES = [
    '‘국제 스포츠 평화’의 날', 'Boxing day', 'National Korean War Veterans Armistice Day', '개천절',
    '경로의 날', '경찰의 날', '경칩', '곡우', '공무원 노동절', '과학 데이', '광군제', '광명성절', '광복절', '구정', '국경절',
    '국군의 날', '국제 고문피해자 지원의 날', '국제 아동절', '근로자의 날', '노동당 창건일', '노동절', '다케시마(독도)의 날',
    '다케시마의 날', '단오', '단오절', '독립기념일', '돌', '돼지날', '로비 데이', '마틴루서킹데이', '명절', '명절 때', '백로',
    '밸런타인', '밸런타인데이', '법의 날', '복날', '복싱 데이', '부처님오신날', '부활절', '북방영토의 날', '사월 초파일', '삭망',
    '삼짓날', '상공의 날', '새해', '석가탄신일', '설', '설 명절', '설날', '성모마리아 대축일', '성모승천대축일', '성탄',
    '성탄 전날', '성탄절', '세계 수협의 날', '세계 에이즈의 날', '세계 여성의 날', '세계 책의 날', '소방의 날', '순국선열의 날',
    '스무날', '스승의 날', '스포츠 평화의 날', '시민의 날', '어린이날', '어버이날', '예수 부활 대축일', '예수성탄대축일', '추석',
    '우수', '울산 조선해양의 날', '원자력의 날', '전승절', '위안부의 날', '인민군 창건 기념일춘절', '인민군 창건일', '임산부의 날',
    '입추', '입춘', '장애인의 날', '전승절', '전전날', '정월 대보름', '정월대보름', '정전협정일', '조선해양의 날', '주먹밥의 날',
    '중복', '중복날', '중양절', '중추절', '지구의 날', '참전용사 정전협정의 날', '창건기념일', '처서', '철의 날', '초하루', '추석',
    '추석 명절', '추석명절', '추수감사절', '춘절', '춘제', '크리스마스', '크리스마스 이브', '크리스마스이브', '태양절', '하지',
    '한가위', '한국전쟁 참전용사 정전협정의 날', '한글날', '해일', '현충일', '히나마쓰리', '亥日', '春節', '穀雨', '雛祭り',
    '어린이날', '8·15', '3·1절 '
]
DEIXIS_DATES = {
    '오늘': '+0',
    '금일': '+0',
    '당일': '+0',
    '이날': '+0',
    '그날': '+0',
    '같은날': '+0',
    '같은 날': '+0',
    '이튿날': '+1',
    '이틑날': '+1',
    '내일': '+1',
    '다음날': '+1',
    '다음 날': '+1',
    '모레': '+2',
    '내일모레': '+2',
    '글피': '+3',
    '전날': '-1',
    '하루 전날': '-1',
    '어제': '-1',
    '어저께': '-1',
    '그제': '-2',
    '그저께': '-2',
    '엊그제': '-3',
    '엊그저께': '-3',
    '그끄저께': '-3'
}


def datetime_preprocess(entity_str: str):
    entity_str = re.sub(r'^(오는|올|이번|지난)\s', '', entity_str)
    entity_str = re.sub(r'(쯤|께|경|중|치|\s정도|만$)', '', entity_str)
    entity_str = entity_str.split('·')[-1]
    return entity_str.strip()


def parse_number(entity_str: str) -> str:
    return re.search(r'\d+', entity_str).group()


def parse_weekday(entity_str: str) -> str:
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    return weekdays[weekdays.index(entity_str[0])] + '요일'


class DateTimeNormalizer:
    def __init__(self):
        self.allow = ('DT_DURATION', 'DT_DAY', 'DT_WEEK', 'DT_MONTH', 'DT_YEAR', 'DT_SEASON', 'DT_OTHERS',
                      'TI_DURATION', 'TI_HOUR', 'TI_MINUTE', 'TI_SECOND', 'TI_OTHERS')

    def __call__(self, entity_type: str, entity_str: str):
        assert entity_type in self.allow
        if entity_type == 'DT_DAY':
            entity_str = datetime_preprocess(entity_str)
            if entity_str in GENERAL_DATE_CONCEPTS:
                return ':general', entity_str
            elif entity_str in NAMED_DATES:
                return ':named', entity_str
            elif entity_str in DEIXIS_DATES:
                return ':day', DEIXIS_DATES[entity_str]
            elif re.search(r'[이삼]?십?\s?[일이삼사오육칠팔구]일', entity_str):
                return ':day', kr2num(entity_str[:-1])
            elif re.search(r'\d\d?일?', entity_str):
                return ':day', parse_number(entity_str)
            elif re.search(r'[월화수목금토일]요?일?', entity_str):
                return ':weekday', parse_weekday(entity_str)
            elif re.search(r'[첫둘셋넷]', entity_str):
                return ':day', 'D+' + str(list('첫둘셋넷').index(entity_str[0]) + 1)
            elif re.search(r'마지막', entity_str):
                return ':day', 'D-1'



if __name__ == '__main__':
    with open('testers.txt', encoding='utf-8') as fp:
        samples = fp.read().splitlines()

    module = DateTimeNormalizer()
    for s in samples:
        print(s, module('DT_DAY', s))
