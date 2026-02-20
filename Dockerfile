FROM astral/uv:alpine

WORKDIR /app

COPY pyproject.toml .python-version ./
RUN uv sync

COPY main.py .

CMD ["uv", "run", "main.py"]
