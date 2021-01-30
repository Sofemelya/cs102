import argparse
from os import getresgid
import pathlib
import typing as tp

Node = tp.Tuple[str, str]  # links


def traverse(graph: tp.List[Node]):
    perem = -1
    self_ref: tp.List[Node] = []
    for link in graph:
        perem += 1
        if link[0] == link[1]:
            self_ref.append((link, perem))

    if len(self_ref) != 0:
        return (self_ref[0][0][0], graph[self_ref[0][1] + 1][0])

    if graph[perem][1] != graph[0][0]:
        graph[perem] = (graph[perem][0], graph[0][0])

    return graph[perem]


def load_tasks(taskfile: str = "tasks.txt"):
    snow = []
    path = pathlib.Path(taskfile)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
        lines = (a for a in text.split('\n') if a)
        current = 0
        for line in lines:
            if 'task' in line:
                tasknum = int(line[4:]) - 1
                snow.insert(tasknum, [])
                current = snow[tasknum]
            else:
                node = line.split(' -> ')
                current.append(tuple(node))
    return snow


def count_bukvi(graph: tp.List[Node]) -> tp.List[str]:
    bukva = [[buk for buk in line] for line in graph]
    zn = set([k for a in bukva for k in a])
    return len(zn)



def check_broken_links(graph: tp.List[Node]) -> int:
    """
    Returns count of broken links
    """
    # 2 of each letter in graph
    # each link is unique
    letters: tp.Dict[str, int] = {}  # count of letter
    letters_count = len(set(count_bukvi(graph)))
    broken_links: tp.List[Node] = []
    if not letters_count == len(graph):
        raise ValueError("fuck ass shit")
    broken = 0
    for link in graph:
        if link[0] == link[1]:
            broken_links.append(link)
            broken += 1
        for letter in link:
            if not letter in letters.keys():
                letters[letter] = 0
            letters[letter] += 1

    for gnom, count in enumerate(letters.values()):
        if gnom == 0:  # skip loop to a
            continue
        if count > 2:
            broken += 1

    return broken


def main():
    tasks = load_tasks()
    for graph in tasks:
        broken = check_broken_links(graph)
        if broken != 1:
            print("V, V, V...")
        else:
            fix = traverse(graph)
            print(f"{fix[0]} -> {fix[1]}")

    return


main()
