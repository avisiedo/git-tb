##
# The target for this file is just to enumerate which partial
# makefile we want to use to compose our final Makefile.
#
# Unless you are not using conditional assignment within
# the different variable files, this would be the priority:
# - The values indicated at 'configs/config.yaml' file.
# - The values indicated at 'mk/variables.mk' file. This
#   file is included into the repository and define the
#   default values for the variables, if not assigned yet.
# - The 'mk/meta-*.mk' files just contain the comment to
#   print out the group text for the help content. They
#   are into independent files, because the order they
#   appear into this include file matters, and provide
#   the flexibility to print out the group text exactly
#   where we want just changing the order into this file.
#
# This file set the 'help' rule as the default one when
# no arguments are indicated.
##
include scripts/mk/projectdir.mk
-include secrets/private.mk
include scripts/mk/variables.mk
# commands
include scripts/mk/help.mk
include scripts/mk/meta-general.mk
include scripts/mk/python-rules.mk
include scripts/mk/printvars.mk
# container and compose
include scripts/mk/meta-container.mk
include scripts/mk/container.mk
# tools

