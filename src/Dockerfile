FROM astral/uv:alpine

WORKDIR /app

COPY pyproject.toml .python-version ./
RUN uv sync

COPY main.py .
COPY modules/ ./modules/

CMD ["uv", "run", "main.py"]
