##
# Private variables
# Copy this file to secrets/private.mk and
# customize there
##

# Container private variables
DOCKER_USER := $(USER)
DOCKER_TOKEN :=

QUAY_USER := $(USER)
QUAY_TOKEN :=

CONTAINER_REGISTRY ?= quay.io
CONTAINER_REGISTRY_USER ?= $(QUAY_USER)
CONTAINER_REGISTRY_TOKEN ?= $(QUAY_TOKEN)

