"""
Objective: Provide lightweight utilities to parse SQL statements (DDL/DML)
and extract simplified data lineage: which tables are read (SELECT/JOIN) and which tables are written (INSERT/UPDATE/DELETE).
This module is intentionally minimal and not a full SQL parser, but good enough for reverse-engineering stored procedures.
"""

import re
from collections import defaultdict
from typing import List, Dict

# Constants for SQL pattern matching
READ_TABLE_PATTERN = r"(?:from|join)\s+([a-zA-Z0-9_]+)"
WRITE_TABLE_PATTERNS = [
    r"insert\s+into\s+([a-zA-Z0-9_]+)",
    r"update\s+([a-zA-Z0-9_]+)",
    r"delete\s+from\s+([a-zA-Z0-9_]+)"
]

def normalize_sql(sql_text: str) -> str:
    """
        Objective: Clean up SQL text by:
        - Lowercasing
        - Removing extra whitespace
        Returns a simplified string for downstream regex search.
    """
    if not sql_text:
        return ""
    sql = sql_text.lower()
    sql = re.sub(r"\s+", " ", sql)
    return sql.strip()


def _extract_tables_by_patterns(sql: str, patterns: List[str]) -> List[str]:
    """
        Helper method to extract table names using multiple regex patterns.
        Returns a sorted list of unique table names.
    """
    tables = []
    for pattern in patterns:
        tables.extend(re.findall(pattern, sql))
    return sorted(set(tables))


def extract_read_tables(sql_text: str) -> List[str]:
    """
        Objective: Use regex patterns to find table names after FROM or JOIN.
        Returns a list of table names (unique, lowercased).
        Limitations: does not handle subqueries deeply or schema prefixes.
    """
    sql = normalize_sql(sql_text)
    matches = re.findall(READ_TABLE_PATTERN, sql)
    return sorted(set(matches))


def extract_write_tables(sql_text: str) -> List[str]:
    """
        Objective: Use regex patterns to find table names in write contexts.
        - INSERT INTO <table>
        - UPDATE <table>
        - DELETE FROM <table>
        Returns a list of table names (unique, lowercased).
    """
    sql = normalize_sql(sql_text)
    return _extract_tables_by_patterns(sql, WRITE_TABLE_PATTERNS)


def parse_lineage(sql_text: str) -> Dict[str, List[str]]:
    """
        Objective: High-level API. Given raw SQL text (e.g., from SHOW CREATE PROCEDURE),
        return a dictionary with:
            {"reads": [...], "writes": [...]}
    """
    return {
        "reads": extract_read_tables(sql_text),
        "writes": extract_write_tables(sql_text)
    }


def analyze_procedures(procedures: Dict[str, str]) -> Dict[str, Dict]:
    """
           Objective: Given a dictionary of procedures {proc_name: sql_text},
           extracts a map of all table written / read by each procedure (and vice versa).
    """

    proc_lineage = {}
    table_lineage = defaultdict(lambda: {"read_by": [], "written_by": []})
    for proc, sql in procedures.items():
        lineage = parse_lineage(sql)
        proc_lineage[proc] = lineage

        for table in lineage["reads"]:
            table_lineage[table]["read_by"].append(proc)
        for table in lineage["writes"]:
            table_lineage[table]["written_by"].append(proc)

    return {
        "procedures": proc_lineage,
        "tables": dict(table_lineage)
    }
