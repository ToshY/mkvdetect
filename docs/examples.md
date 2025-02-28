# Examples

## Basic

Add your files to the input directory of the mounted container.

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  ghcr.io/toshy/mkvdetect:latest
```

By default, it will find all files from the `/app/input` directory (recursively).

## Specific file

Detect stream order for a specific file.

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  ghcr.io/toshy/mkvdetect:latest \
  -i "input/rick-astley-never-gonna-give-you-up.mkv"
```

## Specific subdirectory

Detect stream order for files in a specific subdirectory.

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  ghcr.io/toshy/mkvdetect:latest \
  -i "input/hits"
```

## Multiple inputs

Detect stream order for files in multiple input subdirectories.

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  ghcr.io/toshy/mkvdetect:latest \
  -i "input/dir1" \
  -i "input/dir2" \
  -i "input/dir3" \
  -i "input/dir4" \
  -i "input/dir5"
```
