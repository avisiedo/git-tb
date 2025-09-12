##
# General rules for interacting with container
# manager (podman or docker).
##

ifneq (,$(shell command podman -v 2>/dev/null))
CONTAINER_ENGINE ?= podman
else
ifneq (,$(shell command docker -v 2>/dev/null))
CONTAINER_ENGINE ?= docker
else
CONTAINER_ENGINE ?= false
endif
endif
export CONTAINER_ENGINE

CONTAINER_HEALTH_PATH ?= .State.Health.Status

ifneq (,$(shell(selinuxenabled 2>/dev/null)))
CONTAINER_VOL_SUFFIX ?= :Z
else
CONTAINER_VOL_SUFFIX ?=
endif

CONTAINER_REGISTRY_USER ?= $(USER)
CONTAINER_REGISTRY ?= quay.io
CONTAINER_CONTEXT_DIR ?= .
CONTAINER_FILE ?= build/Dockerfile
CONTAINER_IMAGE_BASE ?= $(CONTAINER_REGISTRY)/$(CONTAINER_REGISTRY_USER)/$(APP_NAME)
CONTAINER_IMAGE_TAG ?= $(shell git rev-parse --short HEAD)
CONTAINER_IMAGE ?= $(CONTAINER_IMAGE_BASE):$(CONTAINER_IMAGE_TAG)
# CONTAINER_BUILD_OPTS
# CONTAINER_ENGINE_OPTS
# CONTAINER_RUN_ARGS
CONTAINER_LABEL ?= hello-world

.PHONY: container-registry-login
container-registry-login:  ## Login on CONTAINER_REGISTRY using CONTAINER_REGISTRY_USER and CONTAINER_REGISTRY_TOKEN (see scripts/mk/private.template.mk)
	$(CONTAINER_ENGINE) login -u "$(CONTAINER_REGISTRY_USER)" -p "$(CONTAINER_REGISTRY_TOKEN)" $(CONTAINER_REGISTRY)

# QUAY_EXPIRATION allow to auto-remove the images when they are pushed to
# the registry. It is useful for keeping the registry clean for images we
# want to use only for a short period of time (developer images)
.PHONY: container-build
container-build: QUAY_EXPIRATION ?= never
container-build:  ## Build image CONTAINER_IMAGE from CONTAINER_FILE using the CONTAINER_CONTEXT_DIR
	$(CONTAINER_ENGINE) build \
	  --label "quay.expires-after=$(QUAY_EXPIRATION)" \
	  $(CONTAINER_BUILD_OPTS) \
	  -t "$(CONTAINER_IMAGE)" \
	  $(CONTAINER_CONTEXT_DIR) \
	  -f "$(CONTAINER_FILE)"
	@# prune builder container
	$(CONTAINER_ENGINE) image prune --filter label=$(CONTAINER_LABEL)=builder --force

.PHONY: container-push
container-push:  ## Push image to remote registry
	$(CONTAINER_ENGINE) push "$(CONTAINER_IMAGE)"

.PHONY: container-clean
container-clean:  ## Remove all local images with label=$(CONTAINER_LABEL)
	$(CONTAINER_ENGINE) image prune --filter label=$(CONTAINER_LABEL) --force
	$(CONTAINER_ENGINE) image list --filter label=$(CONTAINER_LABEL) --format "{{.ID}}" | xargs -r $(CONTAINER_ENGINE) image rm

# TODO Indicate in the options the IP assigned to the postgres container
# .PHONY: container-run
# container-run: CONTAINER_ENGINE_OPTS += --env-file .env
# container-run:  ## Run with CONTAINER_ENGINE_OPTS the CONTAINER_IMAGE using CONTAINER_RUN_ARGS as arguments (eg. make container-run CONTAINER_ENGINE_OPTS="-p 9000:9000")
# 	$(CONTAINER_ENGINE) run $(CONTAINER_ENGINE_OPTS) $(CONTAINER_IMAGE) $(CONTAINER_RUN_ARGS)
