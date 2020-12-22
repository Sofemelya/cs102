import os
import pathlib
import typing as tp

from pyvcs.index import read_index, update_index  # type: ignore
from pyvcs.objects import commit_parse  # type: ignore
from pyvcs.objects import find_object  # type: ignore
from pyvcs.objects import find_tree_files  # type: ignore
from pyvcs.objects import read_object  # type: ignore
from pyvcs.objects import read_tree  # type: ignore
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref  # type: ignore
from pyvcs.tree import commit_tree, write_tree  # type: ignore


def add(gitdir: pathlib.Path, paths: tp.List[pathlib.Path]) -> None:
    for path in paths:
        if path.is_file():
            update_index(gitdir, [path], write=True)
        if path.is_dir():
            add(gitdir, list(path.glob("*")))


def commit(gitdir: pathlib.Path, message: str, author: tp.Optional[str] = None) -> str:
    tree = write_tree(gitdir, read_index(gitdir))
    com = commit_tree(gitdir, tree, message, author=author)
    return com


def checkout(gitdir: pathlib.Path, obj_name: str) -> None:
    for entry in read_index(gitdir):
        try:
            os.remove(entry.name)
        except FileNotFoundError:
            pass
    com = commit_parse(read_object(obj_name, gitdir)[1])
    stopped = False
    while not stopped:
        trees: tp.List[tp.Tuple[pathlib.Path, tp.List[tp.Tuple[int, str, str]]]]
        trees = [(gitdir.parent, read_tree(read_object(com["tree"], gitdir)[1]))]
        while trees:
            tree_path, tree_content = trees[-1]
            del trees[-1]
            for file_data in tree_content:
                fmt, data = read_object(file_data[2], gitdir)
                if fmt == "tree":
                    trees.append((tree_path / file_data[1], read_tree(data)))
                    if not (tree_path / file_data[1]).exists():
                        (tree_path / file_data[1]).mkdir()
                else:
                    if not (tree_path / file_data[1]).exists():
                        with (tree_path / file_data[1]).open("wb") as f:
                            f.write(data)
                        (tree_path / file_data[1]).chmod(int(str(file_data[0]), 8))
        if "parent" in com:
            parse = commit_parse((read_object(com["parent"], gitdir)[1]))
            com[parse[0]] = parse[1]
        else:
            stopped = True
    for dir in gitdir.parent.glob("*"):
        if dir != gitdir and dir.is_dir():
            try:
                os.removedirs(dir)
            except OSError:
                continue
