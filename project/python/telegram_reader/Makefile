# Makefile

# Derive the first 8 chars of the current Git commit hash
GIT_HASH_VERSION := $(shell git rev-parse --short=8 HEAD)

# Base image name
IMAGE := asia-east1-docker.pkg.dev/homepage-436511/docker-repo/telegram_reader

.PHONY: all build

all: build push

build:
	@echo "Building Docker image $(IMAGE):$(GIT_HASH_VERSION) and $(IMAGE):latest"
	docker build \
		-t $(IMAGE):$(GIT_HASH_VERSION) \
		-t $(IMAGE):latest \
		.

.PHONY: push

push:
	docker push $(IMAGE):$(GIT_HASH_VERSION)
	docker push $(IMAGE):latest