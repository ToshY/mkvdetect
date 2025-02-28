## Requirements

- 🐋 [Docker](https://docs.docker.com/get-docker/)

## Pull image

```sh
docker pull ghcr.io/toshy/mkvdetect:latest
```

## Run container

### 🐋 Docker

Run with `docker`.

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  ghcr.io/toshy/mkvdetect:latest -h
```

### 🐳 Compose

Create a `compose.yaml` file.

```yaml
services:
  mkvdetect:
    image: ghcr.io/toshy/mkvdetect:latest
    volumes:
      - ./input:/app/input
```

Run with `docker compose`.

```sh
docker compose run -u $(id -u):$(id -g) --rm mkvdetect -h
```

## Volumes

The following volume mounts are **required**: 

- `/app/input`
