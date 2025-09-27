"""
cli.py
---------
Provide a command-line interface for the Reverse Engineering Toolkit.
It connects the extractor (SQL dump) and parser (SQL parsing + lineage utils),
allowing the user to run steps individually or the whole pipeline.
"""

import argparse
import os
from pathlib import Path
import json
import logging
from parser import analyze_procedures
from src.extractor import dump_schema_and_routines, get_db_cfg
from src.graph_utils import build_graph, export_graphviz
from src.materializer import materialize_all
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configuration constants
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_FILE = "app.log"
LOG_ENCODING = "utf-8"
PARSED_LINEAGE_FILE = "parsed_lineage.json"
SQL_FILE_PATTERN = "sp_*.sql"


def get_path_env(var_name, default):
    value = os.getenv(var_name)
    return Path(value) if value else Path(default)

# Project structure constants
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = get_path_env("OUTPUTS_DIR", PROJECT_ROOT / "outputs")
GRAPH_DIR = get_path_env("GRAPH_DIR", OUTPUTS_DIR / "graph")
PARSED_SQL_DIR = get_path_env("PARSED_SQL_DIR", OUTPUTS_DIR / "parsed_sql")
SQL_DUMPS_DIR = get_path_env("SQL_DUMPS_DIR", OUTPUTS_DIR / "sql_dumps")

# Full path constants
OUTPUT_GRAPH_DIR = get_path_env("OUTPUT_GRAPH_DIR", GRAPH_DIR)
OUTPUT_PARSED_DIR = get_path_env("OUTPUT_PARSED_DIR", PARSED_SQL_DIR)
OUTPUT_SQL_DUMP_DIR = get_path_env("OUTPUT_SQL_DUMP_DIR", SQL_DUMPS_DIR)

class CLIConfig:
    """Manages CLI configuration and file operations"""
    def __init__(self):
        self.base_dir = PROJECT_ROOT
        self.output_graph_dir = OUTPUT_GRAPH_DIR
        self.output_parsed_dir = OUTPUT_PARSED_DIR
        self.output_sql_dump_dir = OUTPUT_SQL_DUMP_DIR
        self._create_directories()


    def _create_directories(self):
        """Create all necessary output directories"""
        for directory in [self.output_graph_dir, self.output_parsed_dir, self.output_sql_dump_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_sql_files(self):
        """Get all SQL files matching the pattern"""
        return list(self.output_sql_dump_dir.glob(SQL_FILE_PATTERN))

    @staticmethod
    def read_sql_file(sql_file):
        """Read SQL file content"""
        with sql_file.open("r") as f:
            return f.read()

    def save_parsed_lineage(self, result):
        """Save parsed lineage result to JSON file"""
        parsed_file = self.output_parsed_dir / PARSED_LINEAGE_FILE
        with parsed_file.open("w") as out:
            json.dump(result, out, indent=2)


def setup_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE, encoding=LOG_ENCODING)
        ]
    )


def run_extract(config):
    logging.info("Starting extraction...")
    dump_schema_and_routines(get_db_cfg(), OUTPUT_SQL_DUMP_DIR)
    logging.info(f"Extraction completed. Files saved in {config.output_sql_dump_dir}")


def run_parse(config):
    logging.info("Starting parsing of SQL dumps...")
    procedures = {}

    for sql_file in config.get_sql_files():
        logging.info(f"Parsing {sql_file} ...")
        procedures[sql_file.stem] = config.read_sql_file(sql_file)

    result = analyze_procedures(procedures)
    config.save_parsed_lineage(result)
    lineage_path = Path(PARSED_SQL_DIR) / "parsed_lineage.json"

    with open(lineage_path, "r") as file:
        graph = build_graph(json.loads(file.read()))
        export_graphviz(graph, GRAPH_DIR)
    logging.info(f"Parsing completed")


def run_materialize():
    materialize_all()


def run_all(config):
    run_extract(config)
    run_parse(config)
    run_materialize()


def main():
    parser = argparse.ArgumentParser(description="Reverse Engineering Toolkit CLI")
    parser.add_argument("command", choices=["extract", "parse", "materialize", "all"], help="Command to run: extract schema/routines, parse SQL, or run all steps")
    args = parser.parse_args()

    setup_logging()
    config = CLIConfig()

    if args.command == "extract":
        run_extract(config)
    elif args.command == "parse":
        run_parse(config)
    elif args.command == "materialize":
        run_materialize()
    elif args.command == "all":
        run_all(config)


if __name__ == "__main__":
    main()