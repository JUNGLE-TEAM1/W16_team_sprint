from mcp.server.fastmcp import FastMCP

from app.database import SessionLocal
from app.services.tools import article_to_tool_payload, get_annals_article as db_get_annals_article


mcp = FastMCP("annals-board")


@mcp.tool()
def get_annals_article(article_id: str) -> dict:
    """Return a Joseon Annals article by its article_id."""
    with SessionLocal() as db:
        article = db_get_annals_article(db, article_id)
        if not article:
            return {"error": "article_not_found", "article_id": article_id}
        return article_to_tool_payload(article)


if __name__ == "__main__":
    mcp.run()
