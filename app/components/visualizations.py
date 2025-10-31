import reflex as rx
from app.states.viz_state import VizState

TOOLTIP_PROPS = {
    "content_style": {
        "background": "white",
        "border_color": "#E8E8E8",
        "border_radius": "0.75rem",
    },
    "label_style": {"color": "black", "font_weight": "500"},
    "separator": "",
}


def create_gradient(color: str, id_name: str) -> rx.Component:
    return rx.el.svg.defs(
        rx.el.svg.linear_gradient(
            rx.el.svg.stop(offset="5%", stop_color=color, stop_opacity=0.8),
            rx.el.svg.stop(offset="95%", stop_color=color, stop_opacity=0),
            id=id_name,
            x1="0",
            y1="0",
            x2="0",
            y2="1",
        )
    )


def time_series_chart(data, lines: list[dict], y_axis_label: str) -> rx.Component:
    return rx.el.div(
        rx.recharts.area_chart(
            rx.recharts.cartesian_grid(horizontal=True, vertical=False, opacity=0.3),
            rx.recharts.tooltip(**TOOLTIP_PROPS),
            create_gradient("#22c55e", "jobs_completed_grad"),
            create_gradient("#f97316", "jobs_failed_grad"),
            create_gradient("#3b82f6", "bots_online_grad"),
            create_gradient("#6b7280", "bots_offline_grad"),
            create_gradient("#ef4444", "faults_grad"),
            rx.recharts.x_axis(
                data_key="timestamp",
                axis_line=False,
                tick_line=False,
                tick_size=10,
                custom_attrs={"fontSize": "12px"},
            ),
            rx.recharts.y_axis(
                rx.recharts.label(
                    value=y_axis_label,
                    position="left",
                    custom_attrs={"angle": -90, "fontSize": "12px"},
                ),
                axis_line=False,
                tick_line=False,
                tick_size=10,
                custom_attrs={"fontSize": "12px"},
            ),
            rx.foreach(
                lines,
                lambda line: rx.recharts.area(
                    type="natural",
                    data_key=line["key"],
                    stroke=line["color"],
                    fill=f"url(#{line['grad_id']})",
                    stroke_width=2,
                ),
            ),
            data=data,
            height=300,
            width="100%",
            margin={"left": 20, "right": 20, "top": 20, "bottom": 20},
            class_name="[&_.recharts-tooltip-wrapper]:z-50",
        ),
        class_name="rounded-lg border bg-white p-4",
    )


def faults_chart() -> rx.Component:
    lines = [{"key": "count", "color": "#ef4444", "grad_id": "faults_grad"}]
    return time_series_chart(VizState.faults_data, lines, "Faults Count")


def jobs_chart() -> rx.Component:
    lines = [
        {"key": "completed", "color": "#22c55e", "grad_id": "jobs_completed_grad"},
        {"key": "failed", "color": "#f97316", "grad_id": "jobs_failed_grad"},
    ]
    return time_series_chart(VizState.jobs_data, lines, "Jobs Count")


def bots_chart() -> rx.Component:
    lines = [
        {"key": "online", "color": "#3b82f6", "grad_id": "bots_online_grad"},
        {"key": "offline", "color": "#6b7280", "grad_id": "bots_offline_grad"},
    ]
    return time_series_chart(VizState.bots_data, lines, "Bots Status")