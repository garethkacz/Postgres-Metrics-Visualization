import reflex as rx
import datetime
import random
from typing import Any
from .query_state import QueryState


class VizState(rx.State):
    """State for managing visualizations and chart data."""

    faults_data: list[dict[str, str | int | float]] = []
    jobs_data: list[dict[str, str | int | float]] = []
    bots_data: list[dict[str, str | int | float]] = []

    @rx.event
    def generate_sample_data(self):
        """Generate sample time-series data for different tables."""
        now = datetime.datetime.now(datetime.timezone.utc)
        self.faults_data = [
            {
                "timestamp": (now - datetime.timedelta(days=i)).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                "count": random.randint(0, 10),
            }
            for i in range(30)
        ][::-1]
        self.jobs_data = [
            {
                "timestamp": (now - datetime.timedelta(days=i)).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                "completed": random.randint(50, 100),
                "failed": random.randint(0, 20),
            }
            for i in range(30)
        ][::-1]
        self.bots_data = [
            {
                "timestamp": (now - datetime.timedelta(days=i)).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                "online": random.randint(80, 100),
                "offline": random.randint(0, 10),
            }
            for i in range(30)
        ][::-1]

    @rx.event
    async def update_viz_data(self):
        from .dashboard_state import DashboardState

        qs = await self.get_state(QueryState)
        if not qs.query_results:
            return
        ds = await self.get_state(DashboardState)
        if ds.selected_table == "faults":
            self.faults_data = qs.query_results
        elif ds.selected_table == "jobs":
            self.jobs_data = qs.query_results
        elif ds.selected_table == "bots":
            self.bots_data = qs.query_results