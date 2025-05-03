# Technical dokumentation for the notification system

The notification system used in the project uses `loguru`
module for flexible and scalable logging.
Logging logic is implemented in two modules, where 
each of is responsible for own part of the system.

## Ads (Anomaly Detection System)

`init_logger` function is used to initialize the logger with 3
handlers: one for console output, one for file output and
last one for sending logs to the syslog server.

### Main components

Component | Description
log_file_path | Path to main log file logger.log, located in the logs directory of the project.
SYSLOG_HOST/PORT | Loaded from .env file
Loguru.add(...) | 2 handlers: file and Syslog
Log levels | Color iconography for levels TRACE to CRITICAL

### Log format

```python
{time:YYYY-MM-DD HH:mm:ss} | {name} | {level.icon} {level} | {message}
```

### Features

- Automatic log compression (zip) and rotation every week.
- Syslog port validity check.
- CRITICAL level is also sent to remote Syslog.

### Example

```python
logger.info("All tasks completed")
logger.warning("Anomaly detected in data")
logger.error("Error occurred during processing")
logger.critical("Critical error occurred")
```

## Ads Celery 

Celery module is more complex and bigger. The point was
to show the potential of the logging system of loguru, that
it can be used in a more complex way. The module do next:

- Categorize logs (basic and predictions).
- Sending critical logs to HTTP endpoint.
- Syslog support.

Loguru can be configured to send logs to a remote HTTP endpoint
that was implemented in this module. Additionally, the module
uses categorization of logs, where basic logs are stored in
`app.log` file and prediction logs are stored in
`prediction_anomalies.log` file. To choose the log file
to write to, the specific log function is used. 

Originally, app.log used for celery logs or debugging purposes,
whereas prediction_anomalies.log is used for storing anomalies.
But that is not a rule, and you can use any log file for
any purpose. 

Http Endpoint is Visualization Dashboard app used in the work.

### Main components

Component | Description
basic_log_path | Log file for basic events
predictions_log_path | Log file for anomalies/predictions
log_basic() | Logs events to app.log
log_predictions() | Logs events to prediction_anomalies.log
send_to_endpoint() | Sends CRITICAL logs to HTTP endpoint
Syslog | Same as module 1

### Logical Filtering

Loguru uses `record[“extra”][“basic”]` to direct logs to different files

```python
filter=lambda record: record["extra"]["basic"] is True  # для basic_log_path
filter=lambda record: record["extra"]["basic"] is False # для predictions_log_path
```

### Using Example

```python
log_basic("System started successfully", level="INFO")
log_predictions("Data anomaly detected", level="WARNING")
log_basic("Critical error occurred", level="CRITICAL")
```

### HTTP endpoint Format

```json
{
  "message": "An anomaly has been detected",
  "level": "INFO",
  "source": "prediction module",
  "timestamp": "2025-04-28T14:30:00.123"
}
```

## ENV 

```env
Variable | Destination | Default value
SYSLOG_HOST | Syslog host | localhost
SYSLOG_PORT | Syslog port | 514
USERNAME | username of Elasticsearch | user
USERPASS | password of Elasticsearch | pass
```