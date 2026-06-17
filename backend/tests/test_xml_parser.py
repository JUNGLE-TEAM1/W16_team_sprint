from pathlib import Path

from app.services.xml_parser import parse_annals_file


def test_parse_real_annals_file_extracts_level5_articles() -> None:
    xml_path = Path(
        "/Users/jungilyou/Downloads/"
        "교육부 국사편찬위원회_"
        "조선왕조실록 정보_"
        "실록원문_20221103/2nd_waa_101.xml"
    )
    articles = parse_annals_file(xml_path, limit=2)

    assert len(articles) == 2
    assert articles[0].article_id == "waa_10107017_001"
    assert "태조" in articles[0].title
    assert articles[0].king == "태조"
    assert "太祖" in articles[0].content
    assert articles[0].official_url.endswith("/waa_10107017_001")


def test_parse_sejong_file_extracts_king_from_file_title() -> None:
    xml_path = Path(
        "/Users/jungilyou/Downloads/"
        "교육부 국사편찬위원회_"
        "조선왕조실록 정보_"
        "실록원문_20221103/2nd_wda_125.xml"
    )
    articles = parse_annals_file(xml_path, limit=1)

    assert articles[0].king == "세종"
