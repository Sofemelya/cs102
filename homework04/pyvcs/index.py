import hashlib
import operator
import os
import pathlib
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        return struct.pack(
            "!LLLLLLLLLL20sH"
            + str(len(self.name))
            + "s"
            + str(8 - (62 + len(self.name)) % 8)
            + "x",
            self.ctime_s,
            self.ctime_n,
            self.mtime_s,
            self.mtime_n,
            self.dev,
            self.ino,
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.sha1,
            self.flags,
            self.name.encode(),
        )

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        index_unpacked_things = struct.unpack("!LLLLLLLLLL20sH" + str(len(data) - 62) + "s", data)
        return GitIndexEntry(
            *(
                list(index_unpacked_things[:-1])
                + [index_unpacked_things[-1].rstrip(b"\00").decode()]
            )
        )


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    index = "index"
    if not (gitdir / index).exists():
        return []
    with (gitdir / index).open("rb") as file:
        header = file.read(12)
        main_content = file.read()
    ind = []
    main_content_copy = main_content
    end_position = 0
    for na in range(struct.unpack(">I", header[8:])[0]):
        end_position = len(main_content_copy) - 1
        for uz in range(63, len(main_content_copy), 8):
            if main_content_copy[uz] == 0:
                end_position = uz
                break
        ind += [GitIndexEntry.unpack(main_content_copy[: end_position + 1])]
        if len(main_content_copy) != end_position - 1:
            main_content_copy = main_content_copy[end_position + 1 :]
    return ind


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    signature = b"DIRC"
    version = 2
    header = struct.pack("!4sLL", signature, version, len(entries))
    packed_entries = b""
    for entry in entries:
        packed_entries += entry.pack()
    content = header + packed_entries
    digest = hashlib.sha1(content).digest()

    with open(str(gitdir) + os.path.sep + "index", "wb") as f:
        f.write(content + digest)


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    entries = read_index(gitdir)
    if details:
        for entry in entries:
            print(f"{entry.mode:o} {entry.sha1.hex()} 0\t{entry.name}")
    else:
        for entry in entries:
            print(entry.name)


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    entry = {entry.name: entry for entry in read_index(gitdir)}
    for path in paths:
        if str(path) in entry:
            del entry[str(path)]
        with path.open("rb") as f:
            data = f.read()
        stat = os.stat(path)
        sha1 = hash_object(data, "blob", write=True)
        entry.update(
            {
                str(path): GitIndexEntry(
                    ctime_s=int(stat.st_ctime),
                    ctime_n=stat.st_ctime_ns % len(str(int(stat.st_ctime))),
                    mtime_s=int(stat.st_mtime),
                    mtime_n=stat.st_mtime_ns % len(str(int(stat.st_mtime))),
                    dev=stat.st_dev,
                    ino=stat.st_ino,
                    mode=stat.st_mode,
                    uid=stat.st_uid,
                    gid=stat.st_gid,
                    size=stat.st_size,
                    sha1=bytes.fromhex(sha1),
                    flags=7,
                    name=str(path),
                )
            }
        )
    if write:
        entry_list = []
        for name in sorted(entry.keys()):
            entry_list.append(entry[name])
        write_index(gitdir, entry_list)