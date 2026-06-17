from dataclasses import asdict, dataclass
import re


KING_PREFIX_MAP = {
    "태조": "waa",
    "정종": "wba",
    "태종": "wca",
    "세종": "wda",
    "문종": "wea",
    "단종": "wfa",
    "세조": "wga",
    "예종": "wha",
    "성종": "wia",
    "연산군": "wja",
    "중종": "wka",
    "인종": "wla",
    "명종": "wma",
    "선조": "wna",
    "광해군": "woa",
    "인조": "wpa",
    "효종": "wqa",
    "현종": "wra",
    "숙종": "wsa",
    "경종": "wta",
    "영조": "wua",
    "정조": "wva",
    "순조": "wwa",
    "헌종": "wxa",
    "철종": "wya",
}

KING_ALIASES = {
    "이성계": "태조",
    "이방과": "정종",
    "이방원": "태종",
    "세종대왕": "세종",
}

KOREAN_DIGITS = {
    "일": 1,
    "한": 1,
    "이": 2,
    "두": 2,
    "삼": 3,
    "세": 3,
    "사": 4,
    "네": 4,
    "오": 5,
    "육": 6,
    "륙": 6,
    "칠": 7,
    "팔": 8,
    "구": 9,
}


@dataclass(frozen=True)
class SearchFilters:
    king: str | None = None
    reign_year: int | None = None
    source_prefix: str | None = None
    source_file: str | None = None

    def to_trace(self) -> dict:
        return {key: value for key, value in asdict(self).items() if value is not None}


ANSWER_FORMAT_PATTERNS = [
    r"\bbest\s*\d+\b",
    r"\btop\s*\d+\b",
    r"베스트\s*\d+",
    r"상위\s*\d+",
    r"\d+\s*(?:가지|개|건|명)",
    r"[한두세네]\s*가지",
    r"역대",
    r"꼽아\s*줘",
    r"뽑아\s*줘",
    r"추천해\s*줘",
    r"알려\s*줘",
    r"정리해\s*줘",
    r"찾아\s*줘",
    r"설명해\s*줘",
    r"요약해\s*줘",
]

TOPIC_EXPANSIONS = {
    "업적": "조선 건국 즉위 교서 도읍 한양 천도 경복궁 종묘 사직 관제 제도 법령 군제",
    "궁궐": "궁궐 궁성 경복궁 수창궁 종묘 사직",
    "즉위": "즉위 왕위 등극 수창궁 백관 추대 공양왕 폐위",
    "정책": "정책 제도 법령 관제 세금 군제 외교 민생",
    "외교": "외교 명나라 사신 예부 조공 표전",
}


def _parse_korean_number(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    if value.isdigit():
        return int(value)
    if value in {"원", "원년"}:
        return 1
    if value in {"즉위", "즉위년"}:
        return 0
    if value in KOREAN_DIGITS:
        return KOREAN_DIGITS[value]
    if "십" not in value:
        return None

    left, _, right = value.partition("십")
    tens = KOREAN_DIGITS.get(left, 1 if left == "" else 0)
    ones = KOREAN_DIGITS.get(right, 0) if right else 0
    number = tens * 10 + ones
    return number or None


def _extract_king(query: str) -> str | None:
    for alias, king in KING_ALIASES.items():
        if alias in query:
            return king
    for king in KING_PREFIX_MAP:
        if king in query:
            return king
    return None


def _extract_reign_year(query: str) -> int | None:
    match = re.search(r"(즉위년|원년|[0-9]+|[일한이두삼세사네오육륙칠팔구십]+)\s*년", query)
    if not match:
        return None
    return _parse_korean_number(match.group(1))


def source_file_for_reign_year(source_prefix: str, reign_year: int) -> str:
    file_number = 100 if reign_year == 0 else 100 + reign_year
    return f"2nd_{source_prefix}_{file_number:03d}.xml"


def extract_search_filters(query: str) -> SearchFilters:
    king = _extract_king(query)
    source_prefix = KING_PREFIX_MAP.get(king or "")
    reign_year = _extract_reign_year(query)
    source_file = None
    if source_prefix and reign_year is not None:
        source_file = source_file_for_reign_year(source_prefix, reign_year)
    return SearchFilters(
        king=king,
        reign_year=reign_year,
        source_prefix=source_prefix,
        source_file=source_file,
    )


def build_retrieval_query(query: str, filters: SearchFilters | None = None) -> str:
    filters = filters or extract_search_filters(query)
    cleaned = query

    for pattern in ANSWER_FORMAT_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    if filters.reign_year is not None:
        cleaned = re.sub(
            r"(즉위년|원년|[0-9]+|[일한이두삼세사네오육륙칠팔구십]+)\s*년",
            " ",
            cleaned,
        )

    cleaned = re.sub(r"[?!？!.,，。]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    expanded_terms = []
    for trigger, expansion in TOPIC_EXPANSIONS.items():
        if trigger in query:
            expanded_terms.append(expansion)

    retrieval_query = " ".join(part for part in [cleaned, *expanded_terms] if part).strip()
    return retrieval_query or query
