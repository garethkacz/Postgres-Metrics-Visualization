import reflex as rx
from .db_state import DatabaseState
import logging
import pandas as pd
from typing import Any
import json


class QueryState(rx.State):
    """Handles querying the database and storing results."""

    is_loading: bool = False
    is_downloading_all: bool = False
    query_results: list[dict] = []
    query_error: str = ""

    @rx.var
    def columns(self) -> list[str]:
        """Get column names from query results."""
        if not self.query_results:
            return []
        return list(self.query_results[0].keys())

    @rx.event
    def download_data(self):
        """Download the current query results as a JSON file."""
        from .dashboard_state import DashboardState

        if not self.query_results:
            return rx.toast.error("No data to download.")
        filename = f"{DashboardState.selected_table}.json"
        data = json.dumps(self.query_results, indent=2)
        return rx.download(data=data, filename=filename)

    @rx.event
    async def download_all_data(self):
        """Download all tables and their schemas from the database as a single JSON file."""
        self.is_downloading_all = True
        yield
        db_state = await self.get_state(DatabaseState)
        if not db_state.is_connected:
            self.is_downloading_all = False
            yield rx.toast.error("Not connected to any database.")
            return
        all_data = {}
        conn = await db_state._get_db_conn()
        if not conn:
            self.is_downloading_all = False
            yield rx.toast.error(f"Connection failed: {db_state.connection_error}")
            return
        try:
            for table_info in db_state.tables:
                table_name = table_info["name"]
                try:
                    query = f'SELECT * FROM "{table_name}";'
                    df = pd.read_sql_query(query, conn)
                    df = df.astype(str)
                    all_data[table_name] = {
                        "schema": table_info["columns"],
                        "data": df.to_dict("records"),
                    }
                except Exception as e:
                    logging.exception(
                        f"Error fetching data for table {table_name} during all-data download: {e}"
                    )
                    yield rx.toast.error(
                        f"Skipping table {table_name} due to an error."
                    )
            if not all_data:
                yield rx.toast.warning("No data could be fetched from any table.")
                self.is_downloading_all = False
                return
            filename = f"database_export.json"
            data_str = json.dumps(all_data, indent=2)
            yield rx.download(data=data_str, filename=filename)
        except Exception as e:
            logging.exception(f"Error during all-data download: {e}")
            yield rx.toast.error("An unexpected error occurred.")
        finally:
            if conn:
                conn.close()
            if db_state._tunnel:
                db_state._tunnel.stop()
                db_state._tunnel = None
            self.is_downloading_all = False

    @rx.event
    async def handle_data_upload(self, files: list[rx.UploadFile]):
        """Handle upload of a JSON data file."""
        if not files:
            yield rx.toast.error("No file selected for upload.")
            return
        file = files[0]
        try:
            data = await file.read()
            json_data = json.loads(data)
            if not isinstance(json_data, list) or not all(
                (isinstance(item, dict) for item in json_data)
            ):
                raise ValueError("JSON must be an array of objects.")
            self.query_results = json_data
            self.is_loading = False
            self.query_error = ""
            yield rx.toast.success(f"Successfully loaded {file.name}")
            yield QueryState.download_data
        except Exception as e:
            logging.exception(f"Failed to process uploaded file: {e}")
            yield rx.toast.error(f"Invalid JSON file: {e}")

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