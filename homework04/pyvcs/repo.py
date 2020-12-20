import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    gitdir_name = os.environ["GIT_DIR"] if "GIT_DIR" in os.environ else ".pyvcs"
    workdir = pathlib.Path(workdir)
    while str(workdir.absolute()) != "/":
        if (workdir / gitdir_name).is_dir():
            return workdir / gitdir_name
        workdir = workdir.parent
    if (workdir / gitdir_name).is_dir():
        return workdir / gitdir_name
    raise Exception("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    gitdir_name = os.environ["GIT_DIR"] if "GIT_DIR" in os.environ else ".pyvcs"
    workdir = pathlib.Path(workdir)
    if workdir.is_file():
        raise Exception(f"{workdir} is not a directory")
    (workdir / gitdir_name).mkdir()
    HEAD = "HEAD"
    with open(workdir / gitdir_name / HEAD, "w") as f:
        f.write("ref: refs/heads/master\n")
    config = "config"
    with open(workdir / gitdir_name / config, "w") as f:
        f.write(
            "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n"
        )
    description = "description"
    with open(workdir / gitdir_name / description, "w") as f:
        f.write("Unnamed pyvcs repository.\n")
    objects = "objects"
    (workdir / gitdir_name / objects).mkdir()
    refs = "refs"
    (workdir / gitdir_name / refs).mkdir()
    heads = "heads"
    (workdir / gitdir_name / refs / heads).mkdir()
    tags = "tags"
    (workdir / gitdir_name / refs / tags).mkdir()
    return workdir / gitdir_name
