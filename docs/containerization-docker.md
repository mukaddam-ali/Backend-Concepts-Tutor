# Containerization & Docker

Containers solve a problem every backend developer eventually hits: "it works on my machine" but breaks on the server, because the two environments have different OS versions, library versions, or configuration.

## What a container is

A container packages an application together with everything it needs to run — code, runtime, system libraries, configuration — into a single, portable unit. Unlike a full virtual machine, a container doesn't include its own operating system kernel; it shares the host machine's kernel while keeping its own isolated filesystem and processes. This makes containers much lighter and faster to start than virtual machines.

## Docker

Docker is the most widely used tool for building and running containers.

- A **Dockerfile** is a text file with instructions for building an **image**: start from a base image (e.g. `python:3.12`), copy in your application code, install dependencies, and specify the command to run.
- An **image** is the packaged, immutable result of building a Dockerfile — a snapshot of everything the application needs.
- A **container** is a running instance of an image. You can run multiple containers from the same image.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## Why containers matter for backend development

- **Consistency**: the same image runs identically on a developer's laptop, a CI server, and production — eliminating "works on my machine" bugs caused by environment differences.
- **Isolation**: each container has its own filesystem and dependencies, so different applications (or different versions of the same application) can run on the same host without conflicting.
- **Portability**: an image built once can run on any machine with a container runtime installed, regardless of the underlying OS specifics.
- **Fast startup**: containers start in seconds, compared to the minutes a full virtual machine can take to boot.

## Orchestration

Running one container is simple; running dozens or hundreds across multiple machines, handling failures, and scaling up and down automatically requires an **orchestrator**. Kubernetes is the dominant tool for this: it schedules containers onto available machines, restarts ones that crash, and can automatically add more instances of a service under load — conceptually similar to what a load balancer plus auto-scaling would provide for a non-containerized deployment.
