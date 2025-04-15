# Makefile for multiprocessing benchmark Docker container

IMAGE_NAME = mp-benchmark-test
CONTAINER_NAME = mp-benchmark-container
MEMORY_LIMIT = 6g
CPU_LIMIT = 4

.PHONY: help build run clean upgrade-helm

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build     		Build the Docker image ($(IMAGE_NAME))"
	@echo "  run       		Run the container with limits: memory=$(MEMORY_LIMIT), cpus=$(CPU_LIMIT)"
	@echo "  clean     		Remove the built Docker image ($(IMAGE_NAME))"
	@echo "  upgrade-helm    upgrade and install ray cluster by helm"
	@echo ""
	@echo "Variables:"
	@echo "  IMAGE_NAME       Name of the Docker image to build and run"
	@echo "  CONTAINER_NAME   Name used for the running Docker container"
	@echo "  MEMORY_LIMIT     Memory limit passed to 'docker run' (e.g., 6g)"
	@echo "  CPU_LIMIT        CPU limit passed to 'docker run' (e.g., 4)"

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm --name $(CONTAINER_NAME) -m $(MEMORY_LIMIT) --cpus=$(CPU_LIMIT) $(IMAGE_NAME)

clean:
	docker rmi $(IMAGE_NAME) || true

upgrade-helm:
	helm upgrade --install raycluster .\helm\ray-cluster\ -f .\helm\ray-cluster\my-values.yaml