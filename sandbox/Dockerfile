# sandbox/Dockerfile — minimal image for running untrusted kata solutions
FROM python:3.11-slim

# Baked-in pytest so each run is a fast container start, not a pip install.
RUN pip install --no-cache-dir "pytest==8.*"

# Run as a non-root user — defense in depth if code tries something nasty.
RUN useradd --create-home --uid 1000 runner
# Switches the active user from root to the newly created runner user.
USER runner

# Creates and sets /work as the default working directory inside the container.
WORKDIR /work

# Run "docker build -t minidgm-sandbox:latest sandbox" in project root (rsi)

# Verify it - three quick checks:
# docker run --rm minidgm-sandbox:latest python --version
# docker run --rm minidgm-sandbox:latest python -m pytest --version
# docker run --rm minidgm-sandbox:latest whoami