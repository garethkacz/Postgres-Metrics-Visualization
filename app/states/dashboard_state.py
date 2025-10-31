import reflex as rx
from .db_state import DatabaseState, TableInfo
from .query_state import QueryState


class DashboardState(rx.State):
    """Manages the state for the dashboard UI."""

    selected_table: str = ""

    @rx.event
    def set_selected_table(self, table_name: str):
        """Set the selected table and trigger data fetch."""
        from .viz_state import VizState

        self.selected_table = table_name
        yield QueryState.fetch_data(table_name)
        yield VizState.update_viz_data

    @rx.var
    async def selected_table_info(self) -> TableInfo | None:
        """Get the schema for the selected table."""
        db_state = await self.get_state(DatabaseState)
        for table in db_state.tables:
            if table["name"] == self.selected_table:
                return table
        return None

    @rx.var
    async def numeric_columns(self) -> list[str]:
        """Get numeric columns for the selected table."""
        table_info = await self.selected_table_info
        if not table_info:
            return []
        numeric_types = ["integer", "bigint", "numeric", "double precision", "real"]
        return [
            col["name"]
            for col in table_info["columns"]
            if any((t in col["type"] for t in numeric_types))
        ]

    @rx.var
    async def time_columns(self) -> list[str]:
        """Get timestamp columns for the selected table."""
        table_info = await self.selected_table_info
        if not table_info:
            return []
        time_types = ["timestamp", "date"]
        return [
            col["name"]
            for col in table_info["columns"]
            if any((t in col["type"] for t in time_types))
        ]

    @rx.var
    async def categorical_columns(self) -> list[str]:
        """Get categorical columns (text, varchar) for the selected table."""
        table_info = await self.selected_table_info
        if not table_info:
            return []
        cat_types = ["character varying", "text", "char"]
        return [
            col["name"]
            for col in table_info["columns"]
            if any((t in col["type"] for t in cat_types))
        ]