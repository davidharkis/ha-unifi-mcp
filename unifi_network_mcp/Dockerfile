FROM python:3.13-slim
ARG BUILD_VERSION
LABEL io.hass.version="${BUILD_VERSION}" \
      io.hass.type="app" \
      io.hass.arch="amd64"
LABEL org.opencontainers.image.source="https://github.com/davidharkis/ha-unifi-mcp"
LABEL org.opencontainers.image.description="Home Assistant UniFi Network MCP app"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip check
COPY gateway.py upstream_http.py ./
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 9443
CMD ["python", "/app/gateway.py"]
