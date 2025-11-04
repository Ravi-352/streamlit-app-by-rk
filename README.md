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
