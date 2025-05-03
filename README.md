# Anomaly detection system (ADS) 

A thesis project presenting an adaptive system for monitoring and detecting anomalies in log streams using machine learning methods for time series forecasting.

## Description

Modern systems generate vast amounts of logs, making manual analysis and timely problem detection difficult. This system is designed to automatically monitor various log sources, predict the expected arrival time of the next message, and detect anomalies such as unexpected logging termination or significant changes in logging frequency. The system utilizes a modular architecture and Docker containerization for ease of deployment and scalability.

## Key Features

*   **Real-Time Monitoring:** Processes log streams as they arrive.
*   **Multi-Source Support:** Flexible architecture with InputManagers for connecting to CSV/PKL files, Elasticsearch, databases, or any data source.
*   **ML-Based Anomaly Detection:** Uses time series models (TripleES, ARIMA, DeepAnt, etc.) to predict log arrival times.
*   **Adaptive Thresholding:** Dynamically calculates the expected arrival time range based on historical prediction errors (using 25th and 95th percentiles) or fixed coefficients when data is scarce.
*   **Asynchronous Processing:** Utilizes Celery and Redis for efficient task execution (log verification, logging) without blocking the main process.
*   **Containerization:** Fully ready to run using Docker and Docker Compose.
*   **Visualization:** Interactive monitoring dashboard built with Dash/Plotly to track system status and results.

## Technology Stack

*   **Language:** Python 3.11-3.12
*   **Data Processing:** Pandas, NumPy
*   **Machine Learning:** Statsmodels, pmdarima, Scikit-learn, pywt, or any other ML library
*   **Asynchronous Tasks:** Celery
*   **Message Broker / State Store:** Redis, or any other message broker
*   **Visualization:** Dash, Plotly
*   **Containerization:** Docker, Docker Compose
*   **Dependency Management:** Poetry (for `ads_celery`), pip (`requirements.txt` for `ads`, `visualization`)

## System Requirements

*   [Git](https://git-scm.com/)
    [Make](https://www.gnu.org/software/make/)
*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)
*   Operating System: Tested on Linux (Ubuntu), Windows 10 22H2, but should work on macOS with Docker installed.

## Installation and Running

### Environment Variables

The project inputs can may require setting the following environment variables, an example of default values are in .env_example but for work .env file is nesessary. 

### Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Real-4339/your-repository.git # Replace with your repository URL
    cd your-repository
    ```

2.  **Run the system using Docker Compose:**
    
    *Note: The builds might take some time.*

    This command will build the Docker image (if not already built). \
    For celery worker: `ads_celery`.
    ```bash
    docker build --no-cache -t celery-image:1.2.1 -f ./ads_celery/ci/Dockerfile .
    ```

    For visualization dashboard `dashboard`:
    ```bash
    docker build --no-cache -t log-visualizer-image:1.0.0 -f ./visualization/Dockerfile .
    ```

    For main application `ads`:
    ```bash
    docker build --no-cache -t ads-image:2.1.6 -f ./ads/ci/Dockerfile .
    ```

    Then, run the Docker Compose to start the `ads_celery`, `redis`, and `visualization` services:
    ```bash
    docker-compose -f ./docker-compose.yml up -d
    ```

    And lastly, run the main application `ads`:
    ```bash
    docker run --name ads-container -it --rm\
		--network code_ads-network \
		--env-file .env \
		-v $(shell pwd):/app \
		ads-image:2.1.6
    ```

    *Note: The `ads` service will be started in the foreground, and you can stop it using `Ctrl+C`.*

- *Alternatively, Run the system using `Makefile`:* \
    To build and start the Docker containers, you can use the provided `Makefile` for convenience. This will build the necessary images and start the containers with a single command.

    For `ads_celery`, `redis`, and `visualization` services, run: 

    ```bash
    make start_docker
    ```

    And to run the main application `ads`, build:

    ```bash
    make build_main
    ```

    And run:
    ```bash
    make start_main
    ```

1.  **Access the Visualization Dashboard:**
    Open your web browser and navigate to: `http://localhost:8050`


5.  **Stop the system:**
    ```bash
    docker-compose -f ./docker-compose.yml down -v --remove-orphans
    ```
    *Alternatively, with the `Makefile`:*
    ```bash
    make down 
    ```

6.  **Stop and clean (Remove from the system)**
    ```bash
    make stop_docker 
    ```
    ```bash
    make clean_main
    ```

For help, use:

```bash
make help
```

### Guide

The complete user guide for ADS is available in the [User Guide](docs/user_guide.md) file.

## License

Apache License 2.0 or see [LICENSE](LICENSE) file.

## Contact

*   **Author:** Vadym Tilihuzov
*   **Email:** qvadym@stuba.sk or vad.tili@gmail.com
*   **GitHub:** [Real-4339](https://github.com/Real-4339)