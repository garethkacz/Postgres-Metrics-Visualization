import reflex as rx
from app.states.db_state import DatabaseState
from app.states.dashboard_state import DashboardState
from app.states.query_state import QueryState
from app.states.credentials_state import CredentialsState, Env
from app.states.viz_state import VizState
from app.components.visualizations import faults_chart, jobs_chart, bots_chart


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
        rx.el.div(
            rx.el.div(class_name="flex-grow"),
            environment_selector(),
            class_name="border-t p-4 flex flex-col",
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
                DashboardState.selected_table != "",
                rx.el.div(
                    rx.match(
                        DashboardState.selected_table,
                        ("faults", faults_chart()),
                        ("jobs", jobs_chart()),
                        ("bots", bots_chart()),
                        rx.el.div(),
                    ),
                    rx.cond(
                        DatabaseState.is_connected,
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
                        connection_error_card(),
                    ),
                    class_name="space-y-4 p-4",
                ),
                rx.el.div(
                    rx.el.p("Select a table from the sidebar to view its data."),
                    class_name="flex items-center justify-center h-full text-gray-500",
                ),
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
            rx.el.button(
                "Manage Connections",
                on_click=CredentialsState.toggle_modal(True),
                class_name="mt-2 text-sm text-blue-600 hover:underline",
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
        credentials_modal(),
        on_mount=[
            CredentialsState.load_credentials,
            DatabaseState.fetch_schema,
            VizState.generate_sample_data,
        ],
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


def environment_selector() -> rx.Component:
    return rx.el.div(
        rx.el.label("Environment", class_name="text-sm font-medium text-gray-700 mb-1"),
        rx.el.select(
            rx.foreach(
                CredentialsState.environments,
                lambda env: rx.el.option(env.name, value=env.name),
            ),
            value=CredentialsState.active_environment,
            on_change=CredentialsState.set_active_environment,
            class_name="w-full p-2 border rounded-md text-sm",
        ),
        rx.el.button(
            rx.icon("settings", class_name="h-4 w-4 mr-2"),
            "Manage",
            on_click=CredentialsState.toggle_modal(True),
            class_name="mt-2 flex items-center justify-center w-full text-sm text-blue-600 hover:underline",
        ),
        class_name="w-full",
    )


def credentials_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(
            rx.el.button("Manage Connections", class_name="hidden")
        ),
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 z-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title("Database Connections"),
                rx.radix.primitives.dialog.description(
                    "Add, edit, or remove your database connection environments.",
                    class_name="mb-4",
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.input(
                            name="name",
                            placeholder="Environment Name",
                            default_value=CredentialsState.current_env.name,
                        ),
                        rx.el.input(
                            name="host",
                            placeholder="Host",
                            default_value=CredentialsState.current_env.host,
                        ),
                        rx.el.input(
                            name="port",
                            placeholder="Port",
                            type="number",
                            default_value=CredentialsState.current_env.port.to_string(),
                        ),
                        rx.el.input(
                            name="database",
                            placeholder="Database",
                            default_value=CredentialsState.current_env.database,
                        ),
                        rx.el.input(
                            name="username",
                            placeholder="Username",
                            default_value=CredentialsState.current_env.username,
                        ),
                        rx.el.input(
                            name="password",
                            placeholder="Password",
                            type="password",
                            default_value=CredentialsState.current_env.password,
                        ),
                        class_name="flex flex-col gap-3",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Save",
                            type="submit",
                            class_name="px-4 py-2 bg-blue-500 text-white rounded",
                        ),
                        class_name="flex justify-end mt-4",
                    ),
                    on_submit=CredentialsState.save_current_environment,
                    reset_on_submit=True,
                ),
                rx.el.div(
                    rx.el.h3(
                        "Saved Environments", class_name="font-semibold mt-4 mb-2"
                    ),
                    rx.foreach(
                        CredentialsState.environments,
                        lambda env: rx.el.div(
                            rx.el.span(env.name, class_name="font-medium"),
                            rx.el.div(
                                rx.el.button(
                                    "Edit",
                                    on_click=CredentialsState.edit_environment(
                                        env.name
                                    ),
                                    class_name="text-blue-500 text-sm",
                                ),
                                rx.el.button(
                                    "Delete",
                                    on_click=CredentialsState.delete_environment(
                                        env.name
                                    ),
                                    class_name="text-red-500 text-sm ml-2",
                                ),
                                class_name="flex gap-2",
                            ),
                            class_name="flex items-center justify-between p-2 border-b",
                        ),
                    ),
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button("Close", class_name="mt-4 px-4 py-2 rounded")
                    ),
                    class_name="flex justify-end",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white p-6 rounded-lg shadow-lg z-50 w-[450px]",
            ),
        ),
        open=CredentialsState.show_modal,
        on_open_change=CredentialsState.toggle_modal,
    )


app.add_page(index)