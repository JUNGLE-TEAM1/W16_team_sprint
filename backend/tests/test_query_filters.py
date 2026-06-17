from app.services.query_filters import build_retrieval_query, extract_search_filters


def test_extracts_king_and_reign_year_from_arabic_number() -> None:
    filters = extract_search_filters("태조 3년에 궁궐 관련 기록이 있어?")

    assert filters.king == "태조"
    assert filters.reign_year == 3
    assert filters.source_prefix == "waa"
    assert filters.source_file == "2nd_waa_103.xml"


def test_extracts_king_alias_and_korean_reign_year() -> None:
    filters = extract_search_filters("이방원 십년에 외교 기록을 찾아줘")

    assert filters.king == "태종"
    assert filters.reign_year == 10
    assert filters.source_prefix == "wca"
    assert filters.source_file == "2nd_wca_110.xml"


def test_retrieval_query_removes_answer_format_numbers() -> None:
    filters = extract_search_filters("태조 역대 업적 best 3 꼽아줘")
    retrieval_query = build_retrieval_query("태조 역대 업적 best 3 꼽아줘", filters)

    assert "best" not in retrieval_query.lower()
    assert "3" not in retrieval_query
    assert "태조" in retrieval_query
    assert "조선 건국" in retrieval_query
    assert "한양 천도" in retrieval_query


def test_retrieval_query_uses_reign_year_as_filter_not_search_text() -> None:
    filters = extract_search_filters("태조 3년에 궁궐 관련 기록이 있어?")
    retrieval_query = build_retrieval_query("태조 3년에 궁궐 관련 기록이 있어?", filters)

    assert filters.source_file == "2nd_waa_103.xml"
    assert "3년" not in retrieval_query
    assert "궁궐" in retrieval_query
    assert "경복궁" in retrieval_query
