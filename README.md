# streamlit-app-by-rk
exploring and testing a streamlit app


## Comparision Table:  
| Aspect                     |                                                             Streamlit | Flask                                      | Django                                            |
| -------------------------- | --------------------------------------------------------------------: | ------------------------------------------ | ------------------------------------------------- |
| Primary use                |                                       Data apps, dashboards, ML demos | General web services, APIs, small web apps | Full-featured web apps, complex sites, enterprise |
| Programming model          |                      Declarative script, auto re-run on widget events | Request-response, route functions          | Request-response, MTV pattern, structured apps    |
| Templating                 |                                       Not needed (widgets + markdown) | Jinja2 templates available                 | Django templates                                  |
| State                      |                                   `st.session_state` (session-scoped) | manage via cookies/sessions                | sessions, auth, middleware                        |
| Routing & URLs             |                                         Basic multipage (via sidebar) | Full control over routes                   | Full control, URL dispatching                     |
| Authentication, ORM, Admin |                                     Not built-in (3rd-party patterns) | Not built-in (extensions available)        | Built-in auth, ORM, admin, migrations             |
| Concurrency & scaling      | Suited for moderate loads; use multiple processes/containers to scale | Highly scalable with proper deployment     | Scalable; built for production complexity         |
| Learning curve             |                                             Very low for Python users | Low–medium (web concepts)                  | Higher (convention and features)                  |
| Best for                   |                            Prototypes, analytics dashboards, ML demos | APIs, microservices, custom web flows      | Complex sites, data models, multi-user apps       |


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
