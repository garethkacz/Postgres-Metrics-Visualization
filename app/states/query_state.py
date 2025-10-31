import reflex as rx
from .db_state import DatabaseState
import logging
import pandas as pd
from typing import Any


class QueryState(rx.State):
    """Handles querying the database and storing results."""

    is_loading: bool = False
    query_results: list[dict] = []
    query_error: str = ""

    @rx.var
    def columns(self) -> list[str]:
        """Get column names from query results."""
        if not self.query_results:
            return []
        return list(self.query_results[0].keys())

    @rx.event
    async def fetch_data(self, table_name: str):
        """Fetch all data from the specified table."""
        if not table_name:
            return
        self.is_loading = True
        self.query_error = ""
        self.query_results = []
        yield
        db_state = await self.get_state(DatabaseState)
        conn = await db_state._get_db_conn()
        if not conn:
            db_state = await self.get_state(DatabaseState)
            self.query_error = db_state.connection_error
            self.is_loading = False
            return
        try:
            query = f'SELECT * FROM "{table_name}";'
            df = pd.read_sql_query(query, conn)
            df = df.astype(str)
            self.query_results = df.to_dict("records")
        except Exception as e:
            logging.exception(f"Error fetching data for table {table_name}: {e}")
            self.query_error = f"Failed to fetch data: {e}"
        finally:
            if conn:
                conn.close()
            self.is_loading = False