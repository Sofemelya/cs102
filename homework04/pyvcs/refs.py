import pathlib
import typing as tp


def update_ref(gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str) -> None:
    with open((gitdir / ref), "w") as file:
        file.write(new_value)


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    ref_file = gitdir / name
    with (ref_file).open("w") as file:
        file.write(ref)


def ref_resolve(gitdir: pathlib.Path, refname: str) -> tp.Optional[str]:
    if refname == "HEAD" and not is_detached(gitdir):
        return resolve_head(gitdir)
    if (gitdir / refname).exists():
        with open(gitdir / refname) as file:
            return file.read().strip()
    return None


def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    return ref_resolve(gitdir, get_ref(gitdir))


def is_detached(gitdir: pathlib.Path) -> bool:
    HEAD = "HEAD"
    with open(gitdir / HEAD) as file:
        return len(file.read()) == 40


def get_ref(gitdir: pathlib.Path) -> str:
    HEAD = "HEAD"
    with open(gitdir / HEAD) as file:
        return file.read().split()[1].strip()
