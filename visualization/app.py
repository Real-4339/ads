import os
import json
import logging
import plotly.graph_objs as go

from statistics import mean
from datetime import datetime
from flask import Flask, request
from dash import Dash, dcc, html, callback_context, no_update, State, Input, Output

LOG_FILE = "logs.json"
MESSAGE_LIST_HEIGHT = "400px"

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

logs = {}
last_update_server = None


def load_logs():
    """Loads logs from a JSON file"""
    global logs, last_update_server
    if os.path.exists(LOG_FILE):
        print(f"Loading logs from: {os.path.abspath(LOG_FILE)}")
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                processed_logs = {}
                latest_timestamp = None
                total_loaded = 0  # Counter for debugging
                for source, log_list in loaded_data.items():
                    if not isinstance(log_list, list):
                        print(
                            f"Warning: Expected list for source '{source}', got {type(log_list)}. Skipping."
                        )
                        continue
                    processed_logs[source] = []
                    source_loaded_count = 0
                    for log_entry in log_list:
                        if not isinstance(log_entry, dict):
                            print(
                                f"Warning: Expected dict for log entry in source '{source}', got {type(log_entry)}. Skipping."
                            )
                            continue

                        # from timestamp to datetime
                        ts_str = log_entry.get("timestamp")
                        timestamp_obj = None
                        if isinstance(ts_str, str):
                            try:
                                # Attempting to parse ISO format (including Z and fractions of seconds)
                                if ts_str.endswith("Z"):
                                    ts_str = ts_str[:-1] + "+00:00"
                                timestamp_obj = datetime.fromisoformat(ts_str)
                            except ValueError:
                                print(
                                    f"Warning: Could not parse ISO timestamp '{ts_str}' for source '{source}'. Using current time."
                                )
                                timestamp_obj = (
                                    datetime.now()
                                )  # Or another default value
                        elif isinstance(ts_str, (int, float)):
                            try:
                                timestamp_obj = datetime.fromtimestamp(ts_str)
                            except Exception:
                                print(
                                    f"Warning: Could not parse numeric timestamp '{ts_str}' for source '{source}'. Using current time."
                                )
                                timestamp_obj = datetime.now()
                        elif isinstance(ts_str, datetime):
                            timestamp_obj = ts_str  # Already datetime
                        else:
                            print(
                                f"Warning: Unexpected timestamp type '{type(ts_str)}' for source '{source}'. Using current time."
                            )
                            timestamp_obj = datetime.now()  # Default value

                        log_entry["timestamp"] = timestamp_obj  # Save as datetime
                        processed_logs[source].append(log_entry)
                        source_loaded_count += 1
                        total_loaded += 1

                        # UPdate last_update_server
                        if timestamp_obj and (
                            latest_timestamp is None or timestamp_obj > latest_timestamp
                        ):
                            latest_timestamp = timestamp_obj

                    # Sorting source logs by time
                    processed_logs[source].sort(
                        key=lambda x: x.get("timestamp", datetime.min)
                    )
                    # print(f"Loaded {source_loaded_count} logs for source '{source}'.")

                logs = processed_logs
                # print(f"Total logs loaded: {total_loaded}")
                # Set last_update_server based on the most recent log OR the current time
                last_update_server = (
                    latest_timestamp.isoformat()
                    if latest_timestamp
                    else datetime.now().isoformat()
                )

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {LOG_FILE}: {e}. Initializing empty logs.")
            logs, last_update_server = {}, datetime.now().isoformat()
        except Exception as e:
            print(f"Error loading logs from {LOG_FILE}: {e}. Initializing empty logs.")
            logs, last_update_server = {}, datetime.now().isoformat()
    else:
        print(f"Log file {LOG_FILE} not found. Initializing empty logs.")
        logs, last_update_server = (
            {},
            datetime.now().isoformat(),
        )  # Initialize if there is no file


def save_logs():
    """Saves the current state of the logs to a JSON file"""
    global logs
    logs_to_save = {}
    for source, log_list in logs.items():
        logs_to_save[source] = []
        for log_entry in log_list:
            entry_copy = log_entry.copy()
            # Convert datetime back to ISO string before saving
            if isinstance(entry_copy.get("timestamp"), datetime):
                entry_copy["timestamp"] = entry_copy["timestamp"].isoformat()
            logs_to_save[source].append(entry_copy)
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs_to_save, f, indent=4)
    except Exception as e:
        print(f"Error saving logs to {LOG_FILE}: {e}")


# initialization
server = Flask(__name__)
app = Dash(__name__, server=server, title="Log Dashboard")
load_logs()


@server.route("/logs", methods=["POST"])
def receive_logs_endpoint():
    global logs, last_update_server
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return {"status": "error", "message": "Invalid or No JSON data"}, 400

    message = data.get("message", "")
    level = data.get(
        "level", "INFO"
    ).upper()  # Приводим к верхнему регистру для надежности
    source = data.get("source", "unknown")
    timestamp_str = data.get("timestamp", datetime.now().isoformat())

    # Timestamp handling (important for sorting and display)
    try:
        # ISO format support with or without 'Z'
        if isinstance(timestamp_str, str):
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1] + "+00:00"
            timestamp = datetime.fromisoformat(timestamp_str)
        elif isinstance(timestamp_str, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp_str)
        else:
            print(
                f"Warning: Received unexpected timestamp type {type(timestamp_str)}. Using current time."
            )
            timestamp = datetime.now()
    except (ValueError, TypeError) as e:
        print(f"Error parsing timestamp '{timestamp_str}': {e}. Using current time.")
        timestamp = datetime.now()

    if not source:
        source = "unknown"  # Default source if not provided

    # Adding an entry to the log dictionary
    if source not in logs:
        logs[source] = []

    new_log_entry = {
        "timestamp": timestamp,  # save as datetime
        "level": level,
        "message": message,
    }

    logs[source].append(new_log_entry)
    # Sort the logs of this source AFTER adding a new one
    logs[source].sort(key=lambda x: x.get("timestamp", datetime.min))

    # Update the time of the last server update
    last_update_server = datetime.now().isoformat()
    # Save logs (can be optimized and done not at every request)
    save_logs()
    return {"status": "ok", "message": "Log received"}, 200


# Dash Layout
app.layout = html.Div(
    [
        html.H1("Log Visualization Dashboard"),
        dcc.Store(id="last-update-client", storage_type="memory"),
        dcc.Interval(id="interval-checker", interval=1000, n_intervals=0),
        dcc.Tabs(id="source-tabs", children=[]),
        html.Div(id="content-container"),
    ]
)

# Dash Callbacks ---------------------------


# Check Updates Callback
@app.callback(
    Output("last-update-client", "data"),
    Input("interval-checker", "n_intervals"),
    State("last-update-client", "data"),
)
def check_for_updates(n, client_timestamp):
    global last_update_server
    if client_timestamp is None and last_update_server is not None:
        return last_update_server
    if last_update_server != client_timestamp:
        return last_update_server
    return no_update


# Update Tabs Callback
@app.callback(
    Output("source-tabs", "children"),
    Output("source-tabs", "value"),
    Input("last-update-client", "data"),
    State("source-tabs", "value"),
    prevent_initial_call=True,
)
def update_tabs(client_update_data, current_active_tab):
    if not callback_context.triggered or not callback_context.triggered[0][
        "prop_id"
    ].startswith("last-update-client"):
        return no_update, no_update
    if not logs:
        return [], None
    sorted_sources = sorted(logs.keys())
    tabs = [dcc.Tab(label=source, value=source) for source in sorted_sources]
    new_active_tab = current_active_tab
    if not sorted_sources:
        new_active_tab = None
    elif current_active_tab not in sorted_sources:
        new_active_tab = sorted_sources[0]
    return tabs, new_active_tab


# Update Tab Content Callback
@app.callback(
    Output("content-container", "children"),
    Input("source-tabs", "value"),
    Input("last-update-client", "data"),
    prevent_initial_call=True,
)
def update_tab_content(selected_source, client_update_data):

    if not selected_source:
        return html.P("Select a source tab.", style={"padding": "20px"})

    source_logs = logs.get(selected_source, [])

    if not source_logs:
        return html.Div(
            f"No logs found for source: {selected_source}", style={"padding": "10px"}
        )

    content = []

    # Filtering and Parsing DEBUG logs
    error_plot_timestamps = []
    error_values_seconds = []
    error_hover_texts = []
    interval_values = []

    # Logs for activity graph and pie (exclude DEBUG metrics)
    activity_logs_filtered = []

    for log in source_logs:
        level = log.get("level")
        message = log.get("message", "")
        timestamp = log.get("timestamp")

        is_metric_debug = False  # Flag that this is a DEBUG log of our data

        if level == "DEBUG" and isinstance(timestamp, datetime):
            # Trying to parse the error
            if message.startswith("Error - "):
                is_metric_debug = True
                try:
                    # Retrieve the number after “Error - ” (8 characters)
                    value_str = message[8:].strip()
                    error_val = float(value_str)
                    error_plot_timestamps.append(timestamp)
                    error_values_seconds.append(error_val)
                    error_hover_texts.append(
                        f"Time: {timestamp:%Y-%m-%d %H:%M:%S.%f}<br>"
                        f"Error: {error_val:.4f} sec"
                    )
                except (ValueError, IndexError):
                    print(f"Warning: Could not parse DEBUG error message: {message}")

            # Trying to parse the difference
            elif message.startswith("Diff - "):
                is_metric_debug = True
                try:
                    # Extract the number after “Diff - ” (7 characters)
                    value_str = message[7:].strip()
                    diff_val = float(value_str)
                    if diff_val > 0:  # Consider only positive differences
                        interval_values.append(diff_val)
                except (ValueError, IndexError):
                    print(f"Warning: Could not parse DEBUG diff message: {message}")

        # Add to the list for activity/pie graphs if it's not our DEBUG metric
        # and if there is a valid timestamp
        if not is_metric_debug and isinstance(timestamp, datetime):
            activity_logs_filtered.append(log)

    # Activity Graph
    if activity_logs_filtered:
        timestamps = [log["timestamp"] for log in activity_logs_filtered]
        levels = [log.get("level", "UNKNOWN") for log in activity_logs_filtered]
        messages_hover = [log.get("message", "") for log in activity_logs_filtered]
        color_map = {
            "WARNING": "orange",
            "SUCCESS": "green",
            "ERROR": "red",
            "INFO": "blue",
            "DEBUG": "purple",
            "UNKNOWN": "gray",
        }  # DEBUG here will be for ‘normal’ DEBUG logs
        trace_activity = go.Scatter(
            x=timestamps,
            y=[1] * len(timestamps),
            mode="markers+text",
            text=levels,
            textposition="top center",
            marker=dict(
                size=10, color=[color_map.get(level, "gray") for level in levels]
            ),
            customdata=messages_hover,
            hovertemplate="<b>%{customdata}</b><br>%{x|%Y-%m-%d %H:%M:%S}<br>Level: %{text}<extra></extra>",
        )
        layout_activity = go.Layout(
            title=f"Log Activity Timeline (excluding metric DEBUGs): {selected_source}",
            xaxis_title="Time",
            yaxis=dict(visible=False),
            height=200,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        content.append(
            dcc.Graph(
                id=f"graph-activity-{selected_source}",
                figure={"data": [trace_activity], "layout": layout_activity},
            )
        )
    else:
        content.append(
            html.Div(
                "No suitable logs found for activity graph.",
                style={"marginTop": "15px"},
            )
        )

    # Time prediction error from DEBUG "Error - " logs
    if error_plot_timestamps:
        trace_pred_error_time = go.Scatter(
            x=error_plot_timestamps,
            y=error_values_seconds,
            mode="lines+markers",
            name="Timestamp Prediction Error",
            hovertext=error_hover_texts,
            hoverinfo="text",
        )
        layout_pred_error_time = go.Layout(
            title=f"Timestamp Prediction Error Trend (from DEBUG 'Error - ' logs): {selected_source}",
            xaxis_title="Time DEBUG Log Recorded",
            yaxis_title="Absolute Error (seconds)",
            margin=dict(l=40, r=20, t=50, b=40),
        )
        content.append(
            dcc.Graph(
                id=f"graph-pred-time-error-{selected_source}",
                figure={
                    "data": [trace_pred_error_time],
                    "layout": layout_pred_error_time,
                },
            )
        )
    else:
        content.append(
            html.Div(
                "No 'DEBUG Error - ...' data found for error graph.",
                style={"marginTop": "15px"},
            )
        )

    # Average time between Events from DEBUG "Error - " logs
    avg_interval_str = "N/A"
    if interval_values:
        try:
            avg_interval = mean(interval_values)
            avg_interval_str = f"{avg_interval:.2f} seconds (based on {len(interval_values)} intervals from DEBUG 'Diff - ' logs)"
        except Exception as e:
            print(f"Error calculating mean interval: {e}")
            avg_interval_str = "Error calculating average"
    else:
        avg_interval_str = "N/A (No 'DEBUG Diff - ...' data with positive values)"

    content.append(
        html.Div(
            [
                html.H4("Average Time Between Events (from DEBUG 'Diff - ' logs):"),
                html.P(avg_interval_str),
            ],
            style={"padding": "10px", "border": "1px solid #eee", "marginTop": "15px"},
        )
    )

    # Distribution of log levels
    level_counts = {}
    for log in activity_logs_filtered:  # Count only non-DEBUG metrics
        level = log.get("level", "UNKNOWN")
        level_counts[level] = level_counts.get(level, 0) + 1

    if level_counts:
        labels, values = list(level_counts.keys()), list(level_counts.values())
        color_map_pie = {
            "SUCCESS": "green",
            "WARNING": "orange",
            "ERROR": "red",
            "INFO": "blue",
            "DEBUG": "purple",
            "UNKNOWN": "gray",
        }
        colors = [color_map_pie.get(label, "lightgrey") for label in labels]
        trace_level_pie = go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            name="Log Levels",
            hole=0.3,
        )
        layout_level_pie = go.Layout(
            title=f"Log Level Distribution (excluding metric DEBUGs): {selected_source}",
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        content.append(
            dcc.Graph(
                id=f"graph-level-pie-{selected_source}",
                figure={"data": [trace_level_pie], "layout": layout_level_pie},
            )
        )

    # Message List
    content.append(html.H3("All Log Messages:"))
    messages_items = []
    # Display all logs from the SOURCE list in reverse order
    for log in reversed(source_logs):
        ts_str = (
            log["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            if isinstance(log.get("timestamp"), datetime)
            else "Invalid Timestamp"
        )
        level_str = log.get("level", "N/A")
        msg_str = log.get("message", "")

        messages_items.append(
            html.Li(
                f"{ts_str} - [{level_str}]: {msg_str}",
                style={
                    "paddingBottom": "5px",
                    "borderBottom": "1px solid #eee",
                    "marginBottom": "5px",
                },
            )
        )

    messages_list = html.Ul(
        messages_items,
        style={
            "maxHeight": MESSAGE_LIST_HEIGHT,
            "height": MESSAGE_LIST_HEIGHT,
            "overflowY": "auto",
            "border": "1px solid #ccc",
            "padding": "10px",
            "listStyleType": "none",
            "fontSize": "small",
            "wordBreak": "break-word",
        },
    )
    content.append(messages_list)

    return html.Div(children=content, style={"padding": "10px"})


if __name__ == "__main__":
    print("Starting Flask server for Dash app...")
    try:
        from statistics import mean
    except ImportError:
        print(
            "Warning: `statistics.mean` not found. Average interval calculation will fail."
        )
    app.run(host="0.0.0.0", port=8050, debug=True)
