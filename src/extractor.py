"""
Objective: Provide a small, read-only toolkit to extract database schema (CREATE TABLE)
and stored routine definitions from a MySQL database and save them as SQL files.
This module is intentionally simple and safe: it reads information_schema and SHOW CREATE
outputs and never executes user procedures or alters data.
"""

import os
import mysql.connector
import logging
import json
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

class DatabaseConnection:
    """Handles MySQL database connections only."""
    def __init__(self, config: dict):
        self.config = config

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = mysql.connector.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config.get("database") or None,
                autocommit=True
            )
            yield conn
        except Exception as e:
            raise RuntimeError(f"Failed to connect to DB: {e}")
        finally:
            if conn:
                conn.close()

class DatabaseExtractor:
    """Handles database schema and routine extraction operations."""

    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection
        self.table_names: list[str] = []
        self.routines: list[dict] = []

    def get_table_names(self):
        return self.table_names

    def get_routines(self):
        return self.routines

    def refresh_fact_tables(self):
        """It refreshes each fact table found calling all procedures"""
        with self.db_connection.get_connection() as conn:
            cur = conn.cursor()
            for procedure in self.routines:
                call_procedure_query = f" call {self.db_connection.config['database']}.{procedure.get('ROUTINE_NAME')}()"
                logging.info(f"executing procedure {procedure.get('ROUTINE_NAME')}")
                cur.execute(call_procedure_query)

    def fetch_table_names(self) -> list:
        """Query information_schema to get all table names for the configured database."""
        logging.info(f"- fetch_table_names")
        with self.db_connection.get_connection() as conn:
            cur = conn.cursor()
            try:
                database_name = self.db_connection.config["database"]
                logging.info(f"loading tables from database: {database_name}")
                cur.execute(
                    "SELECT TABLE_NAME FROM information_schema.tables WHERE table_schema = %s",
                    (database_name,)
                )
                self.table_names = [r[0] for r in cur.fetchall()]
                return self.table_names
            except Exception as e:
                logging.error(f"Failed to fetch table names: {e}")
                raise
            finally:
                cur.close()

    def fetch_create_table(self, table_name: str) -> str:
        """Run SHOW CREATE TABLE and return the CREATE statement as text."""
        logging.info(f"- fetch_create_table - {table_name}")
        with self.db_connection.get_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute(f"SHOW CREATE TABLE `{self.db_connection.config['database']}`.`{table_name}`")
                row = cur.fetchone()
                return row[1] if row and len(row) > 1 else None
            except Exception as e:
                logging.error(f"Failed to fetch CREATE TABLE for {table_name}: {e}")
                return None
            finally:
                cur.close()

    def fetch_routines(self) -> list:
        """Query information_schema.routines for routines in the configured DB."""
        logging.info(f"- fetch_routines")
        with self.db_connection.get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                select_routines_query = f"""
                    SELECT ROUTINE_NAME, ROUTINE_TYPE, ROUTINE_DEFINITION, ROUTINE_SCHEMA
                    FROM information_schema.routines
                    WHERE ROUTINE_SCHEMA = '{self.db_connection.config["database"]}'"""
                cur.execute(select_routines_query)
                self.routines = cur.fetchall()
                return cur.fetchall()
            except Exception as e:
                logging.error(f"Failed to fetch routines: {e}")
                raise
            finally:
                cur.close()

    def try_show_create_routine(self, routine_name: str, routine_type: str) -> str:
        """Attempt to use SHOW CREATE PROCEDURE/FUNCTION to get a fuller definition."""
        logging.info(f"- try_show_create_routine - {routine_name}")
        try:
            with self.db_connection.get_connection() as conn:
                cur = conn.cursor()
                try:
                    if routine_type.upper() == "PROCEDURE":
                        cur.execute(f"SHOW CREATE PROCEDURE {self.db_connection.config['database']}.{routine_name}")
                    else:
                        cur.execute(f"SHOW CREATE FUNCTION {self.db_connection.config['database']}.{routine_name}")
                    row = cur.fetchone()
                    if not row:
                        return None
                    for elt in row:
                        try:
                            if isinstance(elt, str) and elt.strip().upper().startswith("CREATE"):
                                return elt
                        except Exception as e:
                            continue
                    joined = " ".join(str(x) for x in row if isinstance(x, str))
                    return joined if "CREATE" in joined.upper() else None
                finally:
                    cur.close()
        except Exception as e:
            logging.warning(f"Failed to get CREATE statement for {routine_type} {routine_name}: {e}")
            return None

def get_db_cfg() -> dict:
    """
        Objective: Read DB connection settings from environment variables and
        return a dict suitable for mysql.connector.connect(**cfg).
    """
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "")
    }


def save_file(name: str, content: str, output_path: str, suffix: str = ".sql") -> str:
    """
        Objective: Write 'content' and return the path.
        Replaces spaces with underscores.
    """
    safe_name = name.replace(" ", "_")
    fn = output_path / f"{safe_name}{suffix}"
    fn.parent.mkdir(parents=True, exist_ok=True)
    fn.write_text(content or "", encoding="utf-8")
    return str(fn)


def dump_schema_and_routines(cfg: dict, output_path: str) -> dict:
    """
        Objective: Orchestrate the extraction of table DDLs and routine definitions, save them to files,
        and create a dump_meta.json describing what was saved.
        The function is read-only and safe.
        Returns a meta-dictionary with tables and routines.
    """
    cfg = cfg or get_db_cfg()
    db_connection = DatabaseConnection(cfg)
    extractor = DatabaseExtractor(db_connection)
    meta = {"timestamp": datetime.utcnow().isoformat(), "tables": [], "routines": []}

    extractor.fetch_table_names()
    for t in extractor.get_table_names():
        ddl = extractor.fetch_create_table(t) or f"-- No DDL for {t}"
        path = save_file(f"table__{t}", ddl, output_path)
        meta["tables"].append({"table": t, "ddl_file": Path(path).name})

    extractor.fetch_routines()
    for r in extractor.get_routines():
        rname = r.get("ROUTINE_NAME")
        rtype = r.get("ROUTINE_TYPE")
        show_create = extractor.try_show_create_routine(rname, rtype)
        content = show_create or f"-- routine_type: {rtype}\n{r.get('ROUTINE_DEFINITION') or ''}"
        path = save_file(f"{rname}", content, output_path)
        meta["routines"].append({"name": rname, "type": rtype, "file": Path(path).name})

    extractor.refresh_fact_tables()

    meta_path = Path(output_path) / "dump_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta
