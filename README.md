# streamlit-app-by-rk
exploring and testing a streamlit app

# Distroless Streamlit + Prometheus Package


This repo includes a Streamlit app that exposes Prometheus metrics and three Docker artifacts:


- `Dockerfile.distroless` — production-ready distroless image (small, non-root, healthcheck)
- `Dockerfile.debug` — debug-friendly image with shell and tools
- `docker-compose.yml` — bring up the app locally (distroless image)


## Build & Run (distroless)


```bash
# Build
docker build -f Dockerfile.distroless -t my-mlapp:3.10.19-distroless .


# Run
docker run --rm -p 8501:8501 -p 8000:8000 my-mlapp:3.10.19-distroless
```

UI: http://localhost:8501 Prometheus metrics: http://localhost:8000/metrics

Debugging

If you need to debug interactively, build & run the debug image:  
```
# Build debug image
docker build -f Dockerfile.debug -t my-mlapp-debug:3.10.19 .


# Run with shell
docker run --rm -it -p 8501:8501 -p 8000:8000 my-mlapp-debug:3.10.19
# inside container: source /opt/venv/bin/activate
# run: streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

>[!NOTE] Along with 8051 for app, app.py exposes metrics at port 8000. This is where /metrics live. So prometheus uses this port internally for prometheus server to scrape metrics. To visualize the metrics in standalone prometheus UI --> that UI is exposed at port 9090 using docker-compose.yml file.
> ```docker run --rm``` tells Docker to automatically delete the container after it stops. Containers remain on your system even after they exit.
> --rm argument needs to be passed only when we need it short-term, testing/experimenting and using in CLI tools as part of migration. In production, as we need to persist logs and inspect files. Thus, we skip that argument.
