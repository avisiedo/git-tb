Module git_tb.git_tb
====================
Provide git toolbox helper functions to manage git repositories at
scale on your local workstation, for keeping the track of them and let you
focus which repositories need some attention.

Functions
---------

`get_priority_git_remotes()`
:   Return the prioritary remote names read from GIT_REMOTES environment
    variable; each remote name is separated by ',' character. The order matter
    as the push operation make the operation with the first valid found.

`get_subcommands_map()`
:   Return the composed map between subcommand and the entry point function.
    
    :return: A dictionary {"subcommand" -> function}.

`git(*args, **kargs)`
:   Wrapper to invoke git commands

`git_read_local_branches(cwd: str) ‑> list`
:   Read the list of local branches and return as a list of strings.
    
    :param cwd: The path for the analyzed repository.
    
    :return: List of local branches.

`git_read_remote_branches(cwd: str, remotes: list) ‑> list`
:   Read all the remote branches for all the remotes.
    
    :param cwd: The current work directory for the working repository.
    :param remotes: List of remote names.
    
    :return: A list kind of ('origin/1-feature', 'origin/2-fix-typo') and so on.

`git_read_remotes(path: str) ‑> list`
:   Read remotes for a given repository located at path.
    
    :param path: A valid path to a git repository using as base directory the
    WORKSPACE value.
    
    :return: A list with a remote-name -> url key value pairs.

`git_remote_list(path)`
:   Get the name list of remote repositories for a given git repository
    located at path.
    
    :param path: The relative location of the git repository using WORKSPACE as
    the base repository.

`git_tb_all(basedir, f, *args, **kargs)`
:   Traverse file system to find git repositories starting at the specific
    directory, and for each repository detected, run the function with the
    passing the arguments. It does not find submodules, it stop depth searching
    when the first repository is found.
    
    :param basedir: This is the path where start to traverse the file system.
    :param f: It is the reference to the function to call when a git repository
    is detected.
    :param *args: It is the positional arguments when invoking f.
    :param **kargs: It is the no positional arguments when invoking f.

`git_tb_args()`
:   Configure argument parser and return it.

`git_tb_backup()`
:   Generate workspace.yml as a backup source. Keep in mind if some branch
    is not on sync with the remote ones, you could lost information if you
    remove some repository locally. Check with 'git tb check' before delete
    the repository.

`git_tb_backup_helper(*args, **kargs)`
:   Helper which allow to fill the context information for the current
    repository during the traverse of WORKSPACE.
    
    :param *args: positional arguments.
    :param **kargs: no positional arguments.
      - _.KEY_CONTEXT store the dictionary that represent the workspace.yaml
        file.
      - _.KEY_CWD is the current working directory for the actual repository.

`git_tb_check()`
:   Check subcommand by traversing the repositories and running
    git_tb_check_helper for every detected repository in the WORKSPACE.

`git_tb_check_helper(*args, **kargs)`
:   Helper to check the current repository. This generates a summary
    dictionary with the detected indicators, and then print the results
    for the current repository.

`git_tb_check_print(summary: dict)`
:   Print summary of indicators of interest detected for a git repository.
    
    :param summary: dictionary filled with _.CHECK_* keys when the condition
    was detected for the git repository.

`git_tb_check_proc_general(summary: dict, cwd: str)`
:   General checks based on 'git status --ignore-submodules --porcelain'
    
    :param summary: Dictionary where to update the different keys about the states.
    :param cwd: is the current working directory for the git repository to analyze.

`git_tb_check_proc_remotes(summary: dict, cwd: str)`
:   Verify if the repository has any remote, and if the remotes are on sync.
    
    :param summary: is set _.CHECK_NO_REMOTES when no remotes, and
    _.CHECK_NO_ON_SYNC_REMOTES when some local branch is not on sync with the
    tracked remote branch, or no remote branch associated.
    :param cwd: is the path to the git repo being analyzed.
    
    :return: the modified summary dictionary, just to allow concatenate some
    operation with the result.

`git_tb_list()`
:   It represent the 'list' subcommand to traverse and print the path for
    the git repositories found.

`git_tb_list_helper(*args, **kargs)`
:   Helper function to print the name of the repository when traversing
    the file system.
    
    :param *args: The positional arguments. Not used.
    :param **kargs: The no positional arguments. Not used.

`git_tb_pull(*args, **kargs)`
:   Pull remote repositories for all the traversed repositories. The
    arguments are propagated to the helper function.

`git_tb_pull_helper(*args, **kargs)`
:   Helper for the pull operation so this one operate in the current
    repository.
    
    :param *args: positional arguments. Not used here.
    :param **kargs: no positional arguments. It is used the current working dir
    which represent where the repository is located in the file system.

`git_tb_push()`
:   Push subcommand which traverse all the git repositories and try to push
    the changes to remotes for syncing the information.

`git_tb_push_helper(*args, **kargs)`
:   Helper to traverse repositories and push to the remotes to sync the
    current

`git_tb_restore()`
:   Restore a workspace cloning repositories and fetching all the remote
    repositories.

`git_tb_restore_helper(name, path, repo)`
:   Helper to restore a specific repository given the name, path and
    repository.
    
    :param name: Only used for printing.
    :param path: The path where to clone the repository.
    :param repo: The HTTPS or SSH git remote reference for the repository.

`helper_path_to_name(path: str) ‑> str`
:   Translate a repository path in a valid name to use for the workspace.yaml
    file. In other words, replace ("/", " ") by the "-" character.
    
    :param path: A valid repository path.
    
    :return: The repository name.

`is_invalid_repo_path(path: str) ‑> bool`
:   Check when a path is an invalid repository path. It evaluates that it
    is not an absolute path (it is relative to WORKSPACE variable). If the path
    is None or an empty string. If the path try to go up directory, at the
    begin or in the middle.
    
    :param path: The string with the path to the repository.
    
    :return: True if the path is invalid, else False.

`main()`
:   Entry point for git toolbox.

`setup_logs(args)`
:   Setup the logs and DEBUG level if it was specified by parameters.