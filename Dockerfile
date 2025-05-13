# Install uv
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN apt-get update && apt-get install -y tini && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the lockfile and `pyproject.toml` into the image
COPY --chown=user uv.lock $HOME/app/uv.lock
COPY --chown=user pyproject.toml $HOME/app/pyproject.toml

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the project into the image
COPY --chown=user . $HOME/app

# Sync the project
RUN uv sync --frozen

EXPOSE 8909
ENTRYPOINT [ "tini", "--", "uv", "run", "mini-leaderboard" ]
CMD ["start"]
