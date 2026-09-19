FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 0.0.0.0 (not 127.0.0.1) is required here because 127.0.0.1 only accepts
# connections originating from *inside* the same network namespace as the
# process itself. Inside a container, the container has its own isolated
# network namespace -- traffic arriving from the host machine (via Docker's
# port mapping, e.g. -p 8000:8000) is NOT "from localhost" as far as the
# container's network stack is concerned; it looks like it's coming from
# an external interface. Binding to 0.0.0.0 tells Uvicorn to listen on
# ALL network interfaces inside the container, including the one Docker
# uses to forward host traffic in. Binding to 127.0.0.1 would make the
# server literally unreachable from outside the container, even with
# correct port mapping -- requests would just time out.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]