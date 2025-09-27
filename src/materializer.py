"""
Objective:
Provide functionality for creating and managing materialized database views. 
This module handles the creation and replacement of views defined in SQL, focusing on 
summarizing booking information, revenue data, and occupancy statistics for cruise operations.
"""

import logging
from src.extractor import get_db_cfg, DatabaseConnection

# Extract constants for view definitions
VIEW_DEFINITIONS = {
    "vw_bookings_summary": """
        SELECT p.first_name, p.last_name, 
            p1.name AS departure_port, p2.name AS arrival_port, 
            v.start_date, v.end_date, b.booking_date, b.price
        FROM fact_bookings b
        JOIN dim_passenger p ON b.passenger_id = p.passenger_id
        JOIN dim_segment s ON b.segment_id = s.segment_id
        JOIN dim_voyage v ON v.voyage_id = s.voyage_id
        JOIN dim_port p1 ON p1.port_id = s.start_port_id
        JOIN dim_port p2 ON p2.port_id = s.end_port_id
        ORDER BY v.start_date, b.booking_date
    """,
    "vw_revenue_summary": """
        SELECT r.voyage_id, s.name AS ship_name, c.name AS company_name, r.total_revenue
        FROM fact_revenue r 
        JOIN dim_ship s ON r.ship_id = s.ship_id
        JOIN dim_cruise_companies c ON s.company_id = c.company_id 
    """,
    "vw_occupancy_summary": """
        SELECT o.voyage_id, s.name AS ship_name, c.name AS company_name, o.capacity, o.occupancy_rate
        FROM fact_occupancy o
        JOIN dim_ship s ON o.ship_id = s.ship_id
        JOIN dim_cruise_companies c ON s.company_id = c.company_id
    """
}


def create_or_replace_view(db_connection: DatabaseConnection, view_name: str, sql_body: str):
    """Create or replace a database view using the provided connection."""
    with db_connection.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"CREATE OR REPLACE VIEW {view_name} AS {sql_body}")
        conn.commit()


def create_views_from_definitions(db_connection: DatabaseConnection, view_definitions: dict):
    """Extract method to create multiple views from a definitions dictionary."""
    for view_name, sql_body in view_definitions.items():
        create_or_replace_view(db_connection, view_name, sql_body)


def materialize_all():
    """Create or replace all materialized views."""
    logging.info('Creating views...')
    db_connection = DatabaseConnection(get_db_cfg())
    create_views_from_definitions(db_connection, VIEW_DEFINITIONS)
    logging.info("All views created or replaced.")
