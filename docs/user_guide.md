# User Documentation for ADS

## Introduction

This guide describes the resources available and how to interact with 
the developed log anomaly detection system. It is important to note that 
this academic project did not create an exhaustive graphical user guide 
aimed at non-technical people. Instead, the documentation and interaction 
interfaces are aimed at users with technical knowledge (developers, 
researchers) who need to run the system, understand its operation, 
reproduce experiments, or potentially extend its functionality.

## Basic Manual

The centerpiece of the user documentation is the README.md file located in the root directory of the project.

## System configuration

The user can influence the system behavior through available configuration files 
and environment variables.

- **Log Filters**: Filtering rules are configured by editing the JSON 
file `ads/filter/filters.json`. The format and features are described in the 
`ads/filter/doc/help.md` helper file.

- **Connections**: (if necessary) If the system is deployed outside of the 
provided Docker environment, the user may need to configure environment variables 
CELERY\_BROKER\_URL, CELERY\_RESULT\_BACKEND (for Celery) or similar to connect to Elasticsearch. if it is not used with default settings, more specific information can be found in the appropriate module.

- **Source Data**: To use custom source, create own appropriate logic based on `InputManager` interface and connect it on the `ads/__main__.py` file. 

## Testing

Two main tests were conducted as part of the thesis work:
1.  **Test 1:** Used simulated data to verify the handling of various temporal patterns (`ads/input/simulation/`).
2.  **Test 2:** Used data regenerated based on real logs (BGL, Secrepo, Brute Force) to check performance under realistic conditions (`ads/input/csv/`).

A detailed description of the tests, procedures, and results is available in Chapter 8 of the thesis document.

To run the tests, use the following command:
```bash
make start_main
```
This command starts the main ads system, which now for scientific purposes only runs 2 tests. The system uses users console to get the input, which test should be run. Test explanation and their numbers are told in the work and are repeated at this subsection.

## Logging

The system generates several log files for monitoring and debugging:
*   `ads/logs/logger.log`: Logs from the main `ads` application.
*   `ads_celery/logs/app.log`: General logs from the Celery workers.
*   `ads_celery/logs/prediction_anomalies.log`: Records of detected anomalies (logs arriving too early or missed logs).