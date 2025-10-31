import reflex as rx
import os
import psycopg2
from typing import TypedDict, Any
import logging


class ColumnInfo(TypedDict):
    name: str
    type: str


class TableInfo(TypedDict):
    name: str
    columns: list[ColumnInfo]


class DatabaseState(rx.State):
    tables: list[TableInfo] = []
    is_connected: bool = False
    connection_error: str = ""

    @rx.var
    def table_names(self) -> list[str]:
        """Return a list of table names."""
        return [table["name"] for table in self.tables]

    def _get_db_conn(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url or "=" in db_url:
            db_url = "postgresql://postgres:postgres@10.20.18.167:5432/director_db"
        try:
            conn = psycopg2.connect(dsn=db_url, connect_timeout=3)
            return conn
        except Exception as e:
            logging.exception(f"Error connecting to database: {e}")
            error_message = str(e).split("""
""")[0]
            self.connection_error = f"Failed to connect: {error_message}"
            self.is_connected = False
            return None

    @rx.event
    def fetch_schema(self):
        """Connect to the database and fetch the schema."""
        conn = self._get_db_conn()
        if not conn:
            return
        self.is_connected = True
        self.connection_error = ""
        self.tables = []
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
                """)
                tables = [row[0] for row in cur.fetchall()]
                table_info_list = []
                for table_name in tables:
                    cur.execute(
                        """
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = %s;
                    """,
                        (table_name,),
                    )
                    columns = cur.fetchall()
                    column_info: list[ColumnInfo] = [
                        {"name": col[0], "type": col[1]} for col in columns
                    ]
                    table_info_list.append({"name": table_name, "columns": column_info})
                self.tables = table_info_list
        except Exception as e:
            logging.exception(f"Error fetching schema: {e}")
            self.connection_error = f"An error occurred while fetching the schema: {e}"
        finally:
            if conn:
                conn.close()