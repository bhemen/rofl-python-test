FROM docker.io/alpine:3.21.2

# Add some dependencies.
RUN apk add --no-cache curl jq

# Install uv for faster package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

RUN uv venv
RUN uv init
RUN uv add web3 eth-account httpx

COPY app.py .
COPY oracle.abi .
COPY RoflUtility.py .
COPY rofl.py .

# The entire application is defined as a shell script.
ENTRYPOINT ["uv", "run", "app.py"]
