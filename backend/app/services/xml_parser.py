from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET


WHITESPACE_RE = re.compile(r"\s+")
KING_NAME_MAP = {
    "太祖": "태조",
    "定宗": "정종",
    "太宗": "태종",
    "世宗": "세종",
    "文宗": "문종",
    "端宗": "단종",
    "世祖": "세조",
    "睿宗": "예종",
    "成宗": "성종",
    "燕山君": "연산군",
    "中宗": "중종",
    "仁宗": "인종",
    "明宗": "명종",
    "宣祖": "선조",
    "光海君": "광해군",
    "仁祖": "인조",
    "孝宗": "효종",
    "顯宗": "현종",
    "肅宗": "숙종",
    "景宗": "경종",
    "英祖": "영조",
    "正祖": "정조",
    "純祖": "순조",
    "憲宗": "헌종",
    "哲宗": "철종",
}


@dataclass(frozen=True)
class ParsedAnnalsArticle:
    article_id: str
    source_file: str
    title: str
    king: str | None
    reign_date: str | None
    date: str | None
    content: str
    official_url: str
    subject_classes: list[str]


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return WHITESPACE_RE.sub(" ", value).strip()


def _child_text(element: ET.Element, path: str) -> str:
    found = element.find(path)
    return normalize_text("".join(found.itertext())) if found is not None else ""


def _date_value(element: ET.Element, date_type: str) -> str | None:
    for date_element in element.findall(".//dateOccured"):
        if date_element.attrib.get("type") == date_type:
            return date_element.attrib.get("date") or normalize_text(date_element.text)
    return None


def _king_from_title(title: str) -> str | None:
    if not title:
        return None
    for hanja_name, korean_name in KING_NAME_MAP.items():
        if hanja_name in title:
            return korean_name
    first_token = title.split()[0]
    return first_token.rstrip("가이은는")


def official_sillok_url(article_id: str) -> str:
    return f"https://sillok.history.go.kr/id/{article_id}"


def parse_annals_file(xml_path: Path, limit: int | None = None) -> list[ParsedAnnalsArticle]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    articles: list[ParsedAnnalsArticle] = []
    file_king = _king_from_title(_child_text(root, "./front/biblioData/title/mainTitle"))

    for level5 in root.findall(".//level5"):
        article_id = level5.attrib.get("id")
        if not article_id:
            continue

        title = _child_text(level5, "./front/biblioData/title/mainTitle")
        content = normalize_text(" ".join(level5.itertext()))
        paragraph = _child_text(level5, "./text/content/paragraph")
        if paragraph:
            content = paragraph

        if not title or not content:
            continue

        subject_classes = [
            normalize_text(subject.text)
            for subject in level5.findall("./front/biblioData/subjectClass")
            if normalize_text(subject.text)
        ]

        articles.append(
            ParsedAnnalsArticle(
                article_id=article_id,
                source_file=xml_path.name,
                title=title,
                king=file_king or _king_from_title(title),
                reign_date=_date_value(level5, "재위연도"),
                date=_date_value(level5, "서기"),
                content=content,
                official_url=official_sillok_url(article_id),
                subject_classes=subject_classes,
            )
        )

        if limit and len(articles) >= limit:
            break

    return articles
