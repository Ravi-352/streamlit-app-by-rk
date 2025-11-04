```bash
# Build
docker build -f Dockerfile.distroless -t my-streamlit-csv-generator:3.10.19-distroless .


# Run
docker run --rm -p 8501:8501 -p 8000:8000 my-streamlit-csv-generator:3.10.19-distroless
