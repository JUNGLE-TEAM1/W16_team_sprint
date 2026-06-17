from backend.tests.db_reset import APP_RESET_TABLES, RAG_PROTECTED_TABLES


def test_app_reset_tables_do_not_include_rag_protected_tables() -> None:
    assert RAG_PROTECTED_TABLES.isdisjoint(APP_RESET_TABLES)
