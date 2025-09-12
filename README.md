# git tb - git toolbox

This repository provide git helpers subcommands to enhance the management of all
your git repositories.

In terms of organization, the script understand that all your repositories are
in a base starting path, referenced by the WORKSPACE environment variables. If
it is not specified, it set the default value "$HOME/workspace".


# Current operations

- List: All the found git repositories, starting at the WORKSPACE directory.
- Check: Make some checks into the git repositories to display a summary for the
  ones that have pending changes (local changes, pending commits, not syn with
  remotes). This help us to do not forget sync properly the changes.
- Backup: Generate a workspace.yaml file with all the repositories found and the
  remote information.
- Restore: Given a workspace.yaml file allow to restore your workspace.
- Pull: Try to pull all the repositories, to keep them on sync with remote.
- Push: Try to push your changes to keep your remote on sync.

## TODO

- Enhance backup to merge information, and detect some changes as renamed
  repositories. Order the items to make easier to detect changes; this should
  allow that same state does not evoke differences.
- Enhance restore to do not restore not enabled repositories.
- Implement push operation.
