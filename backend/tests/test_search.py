from types import SimpleNamespace

from app.services.search import _keyword_phrases, _score_article, tokenize_query


def test_tokenize_query_keeps_important_one_character_keyword() -> None:
    tokens = tokenize_query("왕자의 난 관련 자료 찾아줘")

    assert "왕자의" in tokens
    assert "난" in tokens
    assert "관련" not in tokens
    assert "자료" not in tokens


def test_keyword_phrases_remove_search_noise() -> None:
    phrases = _keyword_phrases("왕자의 난 관련 자료 찾아줘")

    assert phrases == ["왕자의 난"]


def test_exact_title_phrase_gets_strong_keyword_score() -> None:
    article = SimpleNamespace(
        title="제1차 왕자의 난. 정도전·남은·심효생 등이 숙청되다",
        content="",
        subject_classes=[],
    )

    score = _score_article(article, ["왕자의", "난"], ["왕자의 난"])

    assert score >= 120
