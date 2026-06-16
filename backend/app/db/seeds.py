import json

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from backend.app.core.embedding import embed_text_local
from backend.app.core.security import hash_password
from backend.app.models.post import Post
from backend.app.models.post_embedding import PostEmbedding
from backend.app.models.tag import Tag
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository


def seed_demo_users(database_engine) -> None:
    with Session(database_engine) as db:
        users = UserRepository(db)
        demo_users = [
            {
                "email": "member@sprint.local",
                "password": "password123",
                "role": "member",
            },
            {
                "email": "admin@sprint.local",
                "password": "admin123",
                "role": "admin",
            },
        ]

        for demo_user in demo_users:
            if users.get_by_email(demo_user["email"]) is None:
                users.create(
                    User(
                        email=demo_user["email"],
                        password_hash=hash_password(demo_user["password"]),
                        role=demo_user["role"],
                    )
                )

        db.commit()


SUPPORT_CARD_SOURCES = [
    (
        "[청년/주거] 서울시 청년월세 지원",
        "서울 거주 만 19~39세 청년, 임차보증금과 월세 부담이 있는 무주택 1인가구",
        "월세 일부를 일정 기간 지원하고 주거비 부담을 낮출 수 있도록 신청 절차를 안내합니다.",
        "연도별 공고 확인",
        "서울",
        "서울주거포털, 거주지 관할 주민센터",
        "https://housing.seoul.go.kr/",
        ["청년", "주거", "월세", "서울", "저소득"],
    ),
    (
        "[청년/자산] 청년도약계좌 상담 카드",
        "근로 또는 사업소득이 있는 청년 중 중장기 자산 형성을 준비하는 사람",
        "본인 납입금과 정부기여금, 비과세 혜택 가능성을 확인하도록 돕습니다.",
        "상시/은행별 신청기간 확인",
        "전국",
        "서민금융진흥원, 취급 은행",
        "https://www.kinfa.or.kr/",
        ["청년", "금융", "자산형성", "전국"],
    ),
    (
        "[취업/소득] 국민취업지원제도 1유형",
        "취업 취약계층, 저소득 구직자, 청년 구직자",
        "취업지원서비스와 구직촉진수당 대상 가능성을 함께 점검합니다.",
        "상시",
        "전국",
        "고용복지플러스센터, 국민취업지원제도",
        "https://www.kua.go.kr/",
        ["취업", "청년", "저소득", "상담", "전국"],
    ),
    (
        "[청년/생활] 서울 청년수당",
        "서울 거주 미취업 청년 중 진로 탐색과 생활비 부담이 있는 사람",
        "활동지원금, 진로 프로그램, 상담 연계를 안내합니다.",
        "서울시 공고 확인",
        "서울",
        "청년몽땅정보통",
        "https://youth.seoul.go.kr/",
        ["청년", "서울", "생활비", "취업"],
    ),
    (
        "[청년/저축] 희망두배 청년통장",
        "서울 거주 일하는 청년 중 소득과 재산 기준을 확인해야 하는 사람",
        "저축액 매칭 지원 가능성과 신청 서류를 점검합니다.",
        "연 1회 공고 확인",
        "서울",
        "서울시복지재단",
        "https://www.welfare.seoul.kr/",
        ["청년", "저축", "자산형성", "서울", "저소득"],
    ),
    (
        "[청년/주거] 전세보증금 반환보증 보증료 지원",
        "전월세 보증금 반환 위험을 줄이고 싶은 무주택 청년",
        "보증 가입 여부, 보증료 환급 가능성, 신청 경로를 확인합니다.",
        "지자체 공고 확인",
        "전국",
        "주택도시보증공사, 지자체",
        "https://www.khug.or.kr/",
        ["청년", "주거", "전세", "보증", "전국"],
    ),
    (
        "[청년/건강] 청년 마음건강 지원",
        "우울, 불안, 취업 스트레스 등 심리 상담이 필요한 청년",
        "상담 바우처, 정신건강복지센터, 청년센터 연결 가능성을 안내합니다.",
        "상시/지역별 접수",
        "전국",
        "복지로, 지역 정신건강복지센터",
        "https://www.bokjiro.go.kr/",
        ["청년", "건강", "상담", "복지"],
    ),
    (
        "[청년/문화] 서울 청년문화패스",
        "서울 거주 청년 중 문화생활 비용 지원을 찾는 사람",
        "공연과 전시 관람 지원 대상 여부와 신청 시기를 확인합니다.",
        "연도별 공고 확인",
        "서울",
        "서울문화포털",
        "https://culture.seoul.go.kr/",
        ["청년", "문화", "서울", "생활지원"],
    ),
    (
        "[취업/면접] 서울 취업날개서비스",
        "면접 정장이 필요한 서울 청년 구직자",
        "면접 정장 무료 대여, 예약 지점, 이용 횟수를 안내합니다.",
        "상시",
        "서울",
        "서울일자리포털",
        "https://job.seoul.go.kr/",
        ["청년", "취업", "면접", "서울"],
    ),
    (
        "[주거/상담] 청년 주거상담 연결",
        "계약, 보증금, 월세, 퇴거 문제로 상담이 필요한 청년",
        "주거상담센터, 법률 상담, 임대차 분쟁 조정 경로를 안내합니다.",
        "상시",
        "서울",
        "서울주거상담, 주택임대차분쟁조정위원회",
        "https://housing.seoul.go.kr/",
        ["청년", "주거", "상담", "서울"],
    ),
    (
        "[취업/공간] 서울시 일자리카페",
        "취업 준비 공간, 멘토링, 스터디룸이 필요한 청년",
        "자치구 일자리카페, 취업 프로그램, 공간 이용 정보를 안내합니다.",
        "상시",
        "서울",
        "서울일자리포털",
        "https://job.seoul.go.kr/",
        ["청년", "취업", "시설", "서울", "스터디"],
    ),
    (
        "[청년/정책] 온통청년 정책정보",
        "지역, 나이, 분야별 청년정책을 한 번에 찾고 싶은 사람",
        "청년일자리, 주거, 금융, 복지, 교육문화 정책 검색 경로를 안내합니다.",
        "실시간 갱신",
        "전국",
        "온통청년",
        "https://www.youthcenter.go.kr/",
        ["청년", "정책", "전국", "복지"],
    ),
    (
        "[복지시설/마포구] 마포구 종합사회복지관 상담",
        "마포구 거주자 중 생계, 주거, 돌봄, 사례관리 상담이 필요한 사람",
        "종합상담, 긴급지원 연계, 지역 자원 연결 가능성을 안내합니다.",
        "상시",
        "서울 마포구",
        "마포구 복지정책과, 종합사회복지관",
        "https://www.mapo.go.kr/",
        ["복지시설", "마포구", "상담", "저소득", "서울"],
    ),
    (
        "[청년시설/마포구] 서울청년센터 마포",
        "마포구 인근 청년 중 진로, 일자리, 생활 상담이 필요한 사람",
        "청년상담, 공간 이용, 정책 안내, 커뮤니티 프로그램을 연결합니다.",
        "상시",
        "서울 마포구",
        "청년몽땅정보통",
        "https://youth.seoul.go.kr/",
        ["청년", "마포구", "시설", "상담", "서울"],
    ),
    (
        "[청년공간/마포구] 마포청년나루",
        "마포구 청년 창업, 취업, 문화 활동 공간이 필요한 사람",
        "공간 대관, 역량강화 프로그램, 지역 청년 네트워크를 안내합니다.",
        "상시",
        "서울 마포구",
        "마포청년나루",
        "https://www.maponaru.or.kr/",
        ["청년", "마포구", "취업", "시설"],
    ),
    (
        "[복지시설/송파구] 송파구 사회복지시설 목록",
        "송파구 거주자 중 가까운 복지시설을 찾는 사람",
        "시설명, 시설유형, 시설종류, 운영기관 정보를 기준으로 상담 지점을 찾습니다.",
        "월간 갱신",
        "서울 송파구",
        "서울 열린데이터광장, 서울복지포털",
        "https://data.seoul.go.kr/",
        ["복지시설", "송파구", "상담", "서울"],
    ),
    (
        "[복지시설/구로구] 구로구 사회복지시설 목록",
        "구로구 거주자 중 사회복지관, 상담시설, 지역 복지자원이 필요한 사람",
        "시설 주소와 유형을 기준으로 가까운 지원기관을 안내합니다.",
        "월간 갱신",
        "서울 구로구",
        "서울 열린데이터광장, 서울복지포털",
        "https://data.seoul.go.kr/",
        ["복지시설", "구로구", "상담", "서울"],
    ),
    (
        "[노인/돌봄] 노인맞춤돌봄서비스",
        "일상생활 지원과 정기 안부 확인이 필요한 어르신",
        "방문 안전확인, 생활교육, 서비스 연계 대상 가능성을 점검합니다.",
        "상시",
        "전국",
        "복지로, 읍면동 주민센터",
        "https://www.bokjiro.go.kr/",
        ["노인", "돌봄", "복지", "전국"],
    ),
    (
        "[장애/상담] 장애인종합복지관 이용",
        "재활, 직업훈련, 가족상담, 활동지원 정보가 필요한 장애인과 가족",
        "거주지 인근 복지관 서비스와 신청 상담 경로를 안내합니다.",
        "상시",
        "전국",
        "사회복지시설정보시스템, 지자체",
        "https://www.w4c.go.kr/",
        ["장애", "복지시설", "상담", "전국"],
    ),
    (
        "[가족/돌봄] 가족센터 상담",
        "양육, 다문화, 가족갈등, 1인가구 지원이 필요한 가구",
        "가족상담, 교육, 돌봄 프로그램, 지역센터 연결을 안내합니다.",
        "상시",
        "전국",
        "한국건강가정진흥원, 가족센터",
        "https://www.familynet.or.kr/",
        ["가족", "돌봄", "상담", "복지"],
    ),
    (
        "[중장년/일자리] 50플러스센터",
        "중장년 재취업, 전직, 사회공헌 활동을 준비하는 사람",
        "상담, 교육, 커뮤니티, 일자리 프로그램을 안내합니다.",
        "상시",
        "서울",
        "서울시50플러스포털",
        "https://50plus.or.kr/",
        ["중장년", "취업", "교육", "서울"],
    ),
    (
        "[의료동행/서울] 병원안심동행서비스",
        "혼자 병원 이동과 접수가 어려운 1인가구, 어르신, 장애인",
        "병원 이동, 접수, 수납, 귀가 동행 가능성과 예약 경로를 안내합니다.",
        "상시",
        "서울",
        "서울시 병원안심동행서비스",
        "https://1in.seoul.go.kr/",
        ["의료", "돌봄", "1인가구", "서울"],
    ),
    (
        "[긴급돌봄/서울] 돌봄SOS센터",
        "갑작스러운 질병, 사고, 가족 부재로 긴급 돌봄이 필요한 시민",
        "일시재가, 식사지원, 동행지원, 주거편의 서비스 가능성을 점검합니다.",
        "상시",
        "서울",
        "동주민센터 돌봄SOS센터",
        "https://wis.seoul.go.kr/",
        ["돌봄", "긴급지원", "서울", "복지"],
    ),
    (
        "[식품지원] 푸드뱅크/푸드마켓",
        "식료품과 생필품 지원이 필요한 저소득 가구",
        "기부식품 이용 대상, 거주지 푸드마켓, 신청 상담 경로를 안내합니다.",
        "상시",
        "전국",
        "전국푸드뱅크, 지자체",
        "https://www.foodbank1377.org/",
        ["저소득", "식품", "복지", "전국"],
    ),
    (
        "[자립지원] 보호종료청년 자립지원",
        "아동복지시설 퇴소 후 주거, 생활, 진로 지원이 필요한 청년",
        "자립수당, 주거지원, 전담기관 상담, 멘토링 경로를 안내합니다.",
        "상시",
        "전국",
        "자립정보ON, 보건복지부",
        "https://jaripon.ncrc.or.kr/",
        ["청년", "자립", "주거", "복지"],
    ),
    (
        "[주거위기] 노숙인 종합지원 상담",
        "임시거처, 식사, 의료, 거리상담이 필요한 주거위기 상황",
        "종합지원센터, 응급잠자리, 의료지원, 사례관리 연결을 안내합니다.",
        "상시",
        "전국",
        "지자체 노숙인종합지원센터",
        "https://www.bokjiro.go.kr/",
        ["주거", "긴급지원", "저소득", "상담"],
    ),
    (
        "[여성/취업] 여성인력개발센터",
        "경력단절, 재취업, 직업훈련이 필요한 여성",
        "직업상담, 교육훈련, 취업알선, 새일센터 연계를 안내합니다.",
        "상시",
        "전국",
        "여성새로일하기센터",
        "https://saeil.mogef.go.kr/",
        ["취업", "여성", "교육", "상담"],
    ),
    (
        "[정신건강] 지역 정신건강복지센터",
        "우울, 불안, 자살위험, 정신건강 상담이 필요한 시민",
        "상담, 사례관리, 치료 연계, 위기상담 전화 이용 경로를 안내합니다.",
        "상시",
        "전국",
        "정신건강복지센터, 1393",
        "https://www.mentalhealth.go.kr/",
        ["건강", "상담", "복지", "위기"],
    ),
    (
        "[발달장애] 발달장애인지원센터",
        "발달장애인 개인별지원계획, 권리구제, 가족지원이 필요한 경우",
        "지역센터 상담, 서비스 계획, 주간활동서비스 정보를 안내합니다.",
        "상시",
        "전국",
        "중앙장애아동·발달장애인지원센터",
        "https://www.broso.or.kr/",
        ["장애", "발달장애", "상담", "복지"],
    ),
    (
        "[재난안전] 무더위쉼터",
        "폭염 시 냉방 공간과 휴식 장소가 필요한 시민",
        "쉼터명, 상세주소, 이용가능인원, 냉방기 보유 정보를 기준으로 가까운 쉼터를 찾습니다.",
        "하절기 집중 운영",
        "전국",
        "공공데이터포털 전국무더위쉼터표준데이터",
        "https://www.data.go.kr/data/15013199/standard.do",
        ["재난안전", "무더위쉼터", "노인", "시설"],
    ),
    (
        "[재난안전] 한파쉼터",
        "한파 시 난방 공간과 임시 대피 장소가 필요한 시민",
        "주민센터, 경로당, 복지관 등 한파쉼터 이용 경로를 안내합니다.",
        "동절기 집중 운영",
        "전국",
        "행정안전부, 지자체",
        "https://www.safekorea.go.kr/",
        ["재난안전", "한파쉼터", "시설", "노인"],
    ),
    (
        "[건강시설] 보건소 상담",
        "예방접종, 건강검진, 정신건강, 모자보건 상담이 필요한 시민",
        "거주지 보건소 서비스와 예약/문의 경로를 안내합니다.",
        "상시",
        "전국",
        "지역 보건소",
        "https://www.e-health.go.kr/",
        ["건강", "시설", "상담", "전국"],
    ),
    (
        "[의료인프라] 공공심야약국",
        "야간이나 휴일에 의약품 상담과 구입이 필요한 시민",
        "공공심야약국 위치, 운영시간, 전화 확인 경로를 안내합니다.",
        "야간/휴일",
        "전국",
        "대한약사회, 지자체",
        "https://www.pharm114.or.kr/",
        ["의료", "약국", "생활지원", "전국"],
    ),
    (
        "[의료인프라] 응급의료기관",
        "응급실, 야간진료, 중증응급 대응이 필요한 상황",
        "응급의료기관, 병상 정보, 119/1339 상담 경로를 안내합니다.",
        "상시",
        "전국",
        "응급의료포털 E-Gen",
        "https://www.e-gen.or.kr/",
        ["의료", "응급", "시설", "전국"],
    ),
    (
        "[보육시설] 어린이집 정보",
        "영유아 보육기관, 정원, 운영 유형, 위치 정보가 필요한 보호자",
        "어린이집 유형, 주소, 전화번호, 보육 서비스 확인 경로를 안내합니다.",
        "상시",
        "전국",
        "임신육아종합포털 아이사랑",
        "https://www.childcare.go.kr/",
        ["보육", "가족", "시설", "전국"],
    ),
    (
        "[노인시설] 경로당/노인여가복지시설",
        "어르신 여가, 식사, 프로그램, 안부 확인 공간이 필요한 경우",
        "지역 경로당, 노인복지관, 여가 프로그램 연결을 안내합니다.",
        "상시",
        "전국",
        "지자체 노인복지시설 데이터",
        "https://www.data.go.kr/",
        ["노인", "복지시설", "생활지원", "전국"],
    ),
    (
        "[행정상담] 동주민센터 복지상담",
        "기초생활보장, 긴급복지, 주거급여, 돌봄 신청을 시작해야 하는 시민",
        "초기 상담, 신청서류 확인, 담당 복지팀 연결 경로를 안내합니다.",
        "상시",
        "전국",
        "읍면동 주민센터",
        "https://www.gov.kr/",
        ["상담", "복지", "저소득", "전국"],
    ),
    (
        "[일자리카페/홍대] 청년 취업 스터디 공간",
        "마포·홍대 권역에서 취업 스터디룸과 멘토링이 필요한 청년",
        "공간 예약, 취업특강, 모의면접 프로그램을 안내합니다.",
        "상시",
        "서울 마포구",
        "서울시 일자리카페 정보",
        "https://data.seoul.go.kr/",
        ["청년", "취업", "마포구", "시설"],
    ),
    (
        "[일자리카페/강남] 면접·취업상담 공간",
        "강남 권역에서 면접 준비와 취업 상담이 필요한 청년",
        "스터디룸, 취업상담, 이력서 클리닉, 면접 프로그램을 안내합니다.",
        "상시",
        "서울 강남구",
        "서울시 일자리카페 정보",
        "https://data.seoul.go.kr/",
        ["청년", "취업", "강남구", "시설"],
    ),
    (
        "[일자리카페/노원] 북부권 청년 취업지원",
        "노원·도봉·강북권 청년 구직자",
        "취업 프로그램, 공간 이용, 채용정보 탐색 경로를 안내합니다.",
        "상시",
        "서울 노원구",
        "서울시 일자리카페 정보",
        "https://data.seoul.go.kr/",
        ["청년", "취업", "노원구", "시설"],
    ),
    (
        "[일자리카페/관악] 대학가 취업지원 공간",
        "관악 권역 대학생, 취준생, 청년 구직자",
        "스터디 공간, 취업특강, 멘토링 프로그램을 안내합니다.",
        "상시",
        "서울 관악구",
        "서울시 일자리카페 정보",
        "https://data.seoul.go.kr/",
        ["청년", "취업", "관악구", "시설"],
    ),
    (
        "[일자리카페/영등포] 서남권 취업지원",
        "영등포·구로·금천 권역 청년 구직자",
        "일자리 상담, 공간 이용, 면접 준비 프로그램을 안내합니다.",
        "상시",
        "서울 영등포구",
        "서울시 일자리카페 정보",
        "https://data.seoul.go.kr/",
        ["청년", "취업", "영등포구", "시설"],
    ),
    (
        "[고용/상담] 서울 고용복지플러스센터",
        "실업급여, 취업알선, 직업훈련, 복지상담을 한 번에 확인하려는 시민",
        "고용센터와 복지상담 창구를 통해 신청 가능한 지원을 정리합니다.",
        "상시",
        "서울",
        "고용복지플러스센터",
        "https://www.workplus.go.kr/",
        ["취업", "상담", "복지", "서울"],
    ),
    (
        "[취업/정보] 워크넷 구직지원",
        "채용정보, 직업훈련, 직무정보, 구직 등록이 필요한 사람",
        "워크넷 채용정보와 고용센터 상담을 연결해 구직 경로를 안내합니다.",
        "상시",
        "전국",
        "워크넷",
        "https://www.work.go.kr/",
        ["취업", "구직", "전국", "상담"],
    ),
    (
        "[상권/생활] 소상공인 상권정보",
        "주거지 주변 생활 인프라, 상가업종, 지역 시설 분포를 확인하려는 사람",
        "상호명, 업종, 주소, 경위도 데이터를 바탕으로 생활권 정보를 탐색합니다.",
        "실시간/분기 갱신",
        "전국",
        "소상공인시장진흥공단 상가정보",
        "https://www.data.go.kr/data/15012005/openapi.do",
        ["생활인프라", "상권", "전국", "시설"],
    ),
    (
        "[안전/귀가] 서울 안심귀가 지원",
        "야간 귀가 불안, 1인가구 안전, 안심시설 정보가 필요한 시민",
        "안심이 앱, 안심귀가 스카우트, 안전시설 확인 경로를 안내합니다.",
        "상시",
        "서울",
        "서울시 안심이",
        "https://www.seoul.go.kr/",
        ["안전", "1인가구", "서울", "생활지원"],
    ),
    (
        "[주거급여] 저소득 가구 주거급여",
        "임차료 또는 주택수선 지원이 필요한 저소득 가구",
        "소득인정액, 임차가구/자가가구 여부, 신청서류를 점검합니다.",
        "상시",
        "전국",
        "복지로, 주민센터",
        "https://www.bokjiro.go.kr/",
        ["주거", "저소득", "복지", "전국"],
    ),
    (
        "[긴급복지] 긴급생계지원",
        "실직, 질병, 화재, 소득상실 등 갑작스러운 위기 상황",
        "긴급 생계비, 의료비, 주거비 지원 가능성과 증빙서류를 안내합니다.",
        "상시",
        "전국",
        "보건복지상담센터 129, 주민센터",
        "https://www.bokjiro.go.kr/",
        ["긴급지원", "저소득", "복지", "전국"],
    ),
    (
        "[교육/훈련] 국민내일배움카드",
        "직업훈련, 전직 준비, 역량 개발이 필요한 구직자와 재직자",
        "훈련비 지원, HRD-Net 과정 검색, 고용센터 상담 경로를 안내합니다.",
        "상시",
        "전국",
        "HRD-Net",
        "https://www.hrd.go.kr/",
        ["취업", "교육", "전국", "청년"],
    ),
    (
        "[1인가구/서울] 서울 1인가구 포털",
        "혼자 사는 시민 중 주거, 안전, 건강, 관계망 지원을 찾는 사람",
        "1인가구 프로그램, 병원동행, 안심장비, 생활상담을 안내합니다.",
        "상시",
        "서울",
        "서울 1인가구 포털",
        "https://1in.seoul.go.kr/",
        ["1인가구", "서울", "생활지원", "상담"],
    ),
]


def _support_card_content(
    *,
    target: str,
    support: str,
    period: str,
    region: str,
    contact: str,
    source_url: str,
) -> str:
    return f"""지원대상: {target}
지원내용: {support}
신청기간: {period}
지역: {region}
문의처: {contact}
출처 URL: {source_url}"""


SUPPORT_CARDS = [
    {
        "title": title,
        "content": _support_card_content(
            target=target,
            support=support,
            period=period,
            region=region,
            contact=contact,
            source_url=source_url,
        ),
        "tags": tags,
    }
    for title, target, support, period, region, contact, source_url, tags in SUPPORT_CARD_SOURCES
]


def seed_support_cards(database_engine) -> None:
    with Session(database_engine) as db:
        admin_user = db.scalar(select(User).where(User.email == "admin@sprint.local"))
        if admin_user is None:
            seed_demo_users(database_engine)
            admin_user = db.scalar(select(User).where(User.email == "admin@sprint.local"))

        if admin_user is None:
            return

        _delete_legacy_sprint_cards(db)

        for card in SUPPORT_CARDS:
            tags = [_get_or_create_tag(db, tag_name) for tag_name in card["tags"]]
            existing_post = _find_existing_support_card(db, card)
            if existing_post is not None:
                existing_post.title = card["title"]
                existing_post.content = card["content"]
                existing_post.author_name = "data-bot"
                existing_post.user_id = admin_user.id
                existing_post.tags = tags
                _ensure_post_embedding(db, existing_post)
                continue

            post = Post(
                title=card["title"],
                content=card["content"],
                author_name="data-bot",
                user_id=admin_user.id,
                tags=tags,
            )
            db.add(post)
            db.flush()
            _ensure_post_embedding(db, post)

        db.commit()


def normalize_support_card_record(
    *,
    title: str,
    target: str = "",
    support: str = "",
    period: str = "",
    region: str = "",
    contact: str = "",
    source_url: str = "",
    tags: list[str] | None = None,
) -> dict[str, object]:
    """Normalize one public-data row into the Post-shaped support card format."""
    return {
        "title": title.strip(),
        "content": _support_card_content(
            target=target,
            support=support,
            period=period,
            region=region,
            contact=contact,
            source_url=source_url,
        ),
        "tags": tags or [],
    }


def _find_existing_support_card(db: Session, card: dict[str, object]) -> Post | None:
    return db.scalar(
        select(Post).where(
            Post.author_name == "data-bot",
            Post.title == str(card["title"]),
        )
    )


def _delete_legacy_sprint_cards(db: Session) -> None:
    legacy_posts = db.scalars(
        select(Post).where(
            Post.author_name == "Sprint Team",
            Post.title.like("Sprint %.%"),
        )
    ).all()
    for post in legacy_posts:
        db.delete(post)
    if legacy_posts:
        db.flush()


def _get_or_create_tag(db: Session, tag_name: str) -> Tag:
    normalized_name = tag_name.strip().lower().lstrip("#")
    with db.no_autoflush:
        tag = db.scalar(select(Tag).where(Tag.name == normalized_name))
    if tag is not None:
        return tag

    dialect_name = db.get_bind().dialect.name
    if dialect_name == "postgresql":
        statement = (
            postgresql_insert(Tag)
            .values(name=normalized_name)
            .on_conflict_do_nothing(index_elements=["name"])
        )
        db.execute(statement)
    elif dialect_name == "sqlite":
        statement = (
            sqlite_insert(Tag)
            .values(name=normalized_name)
            .on_conflict_do_nothing(index_elements=["name"])
        )
        db.execute(statement)
    else:
        db.add(Tag(name=normalized_name))

    db.flush()
    with db.no_autoflush:
        tag = db.scalar(select(Tag).where(Tag.name == normalized_name))
    if tag is None:
        raise RuntimeError(f"Failed to create or load tag: {normalized_name}")
    return tag


def _ensure_post_embedding(db: Session, post: Post) -> None:
    source_text = f"{post.title}\n{post.content}\n{' '.join(tag.name for tag in post.tags)}".strip()
    vector = embed_text_local(source_text)

    embedding = db.get(PostEmbedding, post.id)
    if embedding is None:
        db.add(
            PostEmbedding(
                post_id=post.id,
                source_text=source_text,
                vector_json=json.dumps(vector),
            )
        )
        db.flush()
        return

    embedding.source_text = source_text
    embedding.vector_json = json.dumps(vector)
