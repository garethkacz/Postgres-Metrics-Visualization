import reflex as rx
from app.states.db_state import DatabaseState
from app.states.dashboard_state import DashboardState
from app.states.query_state import QueryState


def sidebar() -> rx.Component:
    """The sidebar component for table selection."""
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("database", class_name="h-6 w-6 text-blue-600"),
                rx.el.span("Postgres Dashboard", class_name="text-lg font-semibold"),
                class_name="flex h-16 items-center gap-3 border-b px-4",
            ),
            rx.el.nav(
                rx.foreach(
                    DatabaseState.table_names,
                    lambda table_name: rx.el.a(
                        rx.el.span(table_name),
                        on_click=lambda: DashboardState.set_selected_table(table_name),
                        href="#",
                        class_name=rx.cond(
                            DashboardState.selected_table == table_name,
                            "flex items-center gap-3 rounded-lg bg-gray-100 px-3 py-2 text-gray-900 transition-all hover:text-gray-900",
                            "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900",
                        ),
                    ),
                ),
                class_name="flex flex-col gap-2 p-4 text-sm font-medium",
            ),
            class_name="flex-1 overflow-auto",
        ),
        class_name="flex flex-col min-h-0 border-r w-64 h-screen shrink-0 bg-white",
    )


def main_content() -> rx.Component:
    """The main content area for displaying charts and stats."""
    return rx.el.main(
        rx.el.header(
            rx.el.h1(
                rx.cond(
                    DashboardState.selected_table,
                    f"Dashboard: {DashboardState.selected_table}",
                    "Select a table to get started",
                ),
                class_name="text-2xl font-bold",
            ),
            class_name="border-b p-4",
        ),
        rx.el.div(
            rx.cond(
                DatabaseState.is_connected,
                rx.cond(
                    DashboardState.selected_table,
                    rx.cond(
                        QueryState.is_loading,
                        rx.el.div(
                            rx.el.div(
                                class_name="h-8 w-full bg-gray-200 rounded animate-pulse"
                            ),
                            rx.el.div(
                                class_name="h-8 w-full bg-gray-200 rounded animate-pulse mt-2"
                            ),
                            rx.el.div(
                                class_name="h-8 w-full bg-gray-200 rounded animate-pulse mt-2"
                            ),
                            rx.el.div(
                                class_name="h-8 w-full bg-gray-200 rounded animate-pulse mt-2"
                            ),
                            class_name="p-4",
                        ),
                        data_table(),
                    ),
                    rx.el.div(
                        rx.el.p("Select a table from the sidebar to view its data."),
                        class_name="flex items-center justify-center h-full text-gray-500",
                    ),
                ),
                connection_error_card(),
            ),
            class_name="flex-1 overflow-auto bg-gray-50",
        ),
        class_name="flex flex-col flex-1",
    )


def data_table() -> rx.Component:
    """The data table component."""
    return rx.el.div(
        rx.cond(
            QueryState.query_results.length() > 0,
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.foreach(
                            QueryState.columns,
                            lambda col: rx.el.th(
                                col, class_name="p-2 text-left border-b"
                            ),
                        ),
                        class_name="bg-gray-100",
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        QueryState.query_results,
                        lambda row: rx.el.tr(
                            rx.foreach(
                                row.values(),
                                lambda val: rx.el.td(
                                    rx.el.span(val.to_string()),
                                    class_name="p-2 border-b",
                                ),
                            ),
                            class_name="hover:bg-gray-50",
                        ),
                    )
                ),
                class_name="w-full text-sm",
            ),
            rx.el.div(
                rx.el.p("No data found for this table."), class_name="p-4 text-gray-500"
            ),
        ),
        class_name="p-4",
    )


def connection_error_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3("Connection Error", class_name="font-semibold text-red-800"),
            rx.el.p(
                DatabaseState.connection_error, class_name="text-sm text-red-700 mt-1"
            ),
            class_name="rounded-lg border border-red-200 bg-red-50 p-4",
        ),
        class_name="p-4",
    )


def index() -> rx.Component:
    """The main page of the application."""
    return rx.el.div(
        sidebar(),
        main_content(),
        on_mount=DatabaseState.fetch_schema,
        class_name="flex min-h-screen w-screen font-['Inter']",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)