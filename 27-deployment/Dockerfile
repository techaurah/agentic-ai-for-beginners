# The whole deployment in one file. Read it top to bottom:
#
# 1. Start from a small official Python image. "slim" leaves out the
#    compilers and docs the service will never use, which means a
#    smaller image and a smaller attack surface.
FROM python:3.12-slim

# 2. Work in a dedicated folder, not the filesystem root.
WORKDIR /app

# 3. Copy only the two files the service needs. The lesson code has no
#    dependencies beyond the standard library, so there is no
#    requirements install step. The day you add one, it goes here,
#    before the COPY, so Docker can cache the slow layer.
COPY agent.py server.py ./

# 4. Inside a container the service must listen on all interfaces, and
#    the platform, not the image, chooses the port. server.py reads
#    both from the environment, so nothing here is edited per deploy.
ENV HOST=0.0.0.0 PORT=8000

# 5. Say which port the service uses (documentation for the platform).
EXPOSE 8000

# 6. Run as the image's unprivileged user, not root. If the process is
#    ever compromised, it should not own the container.
USER nobody

# 7. One process, in the foreground, logging to stdout. The platform
#    collects the logs, restarts the process when /health fails, and
#    scales by starting more containers. The app does none of that
#    itself, on purpose.
CMD ["python3", "server.py"]
