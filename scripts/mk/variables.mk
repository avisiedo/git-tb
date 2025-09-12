##
# TODO Review the whole file and remove the variables that does not make sense
#      for this repository.
# TODO Remove this placeholder and the above when you finish to review the file.
#
# Set default variable values for the project
##
APP_NAME ?= hello
export APP_NAME

BIN ?= bin
PATH := $(CURDIR)/$(BIN):$(PATH)
export PATH

CONTAINER_IMAGE_BASE ?= quay.io/$(firstword $(subst +, ,$(QUAY_USER)))/$(APP_NAME)

# Application specific parameters
# APP_SOMETHING ?= VALUE
# export APP_SOMETHING

