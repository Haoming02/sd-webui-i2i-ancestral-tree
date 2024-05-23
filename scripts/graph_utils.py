"""Script that generates the relationships"""


class iTreeNode:

    def __init__(
        self,
        img_url: str,
        img_path: str,
        parent_path: str,
        i2i_mode: str,
    ):

        self.img_url: str = img_url
        self.img_path: str = img_path
        self.parent_path: str = parent_path
        self.i2i_mode: str = i2i_mode
        self.layer: int = -1
        self.rank: int = -1

    def to_json(self) -> dict:
        return {
            "url": self.img_url,
            "path": self.img_path,
            "parent": self.parent_path,
            "mode": self.i2i_mode,
            "layer": self.layer,
            "rank": self.rank,
        }


def _dedupe(node_list: list[iTreeNode]) -> list[iTreeNode]:

    history = set()
    pruned_list = []

    for node in node_list:
        if node.img_path not in history:
            history.add(node.img_path)
            pruned_list.append(node)

    return pruned_list


def dedupe(
    result_list: list[iTreeNode], source_list: list[iTreeNode]
) -> tuple[list[iTreeNode], list[iTreeNode]]:

    source_list = _dedupe(source_list)

    pruned_source = [
        sauce
        for sauce in source_list
        if not any(sauce.img_path == res.img_path for res in result_list)
    ]

    return result_list, pruned_source


def recursive_pass(
    node_list: list[iTreeNode], parent_path: str, rank: int, layer: int
) -> tuple[int, dict]:

    ret: dict = {}
    child_count: int = 0

    for node in node_list:
        if node.parent_path != parent_path:
            continue

        node.rank = rank
        node.layer = layer

        delta, ret[node.img_path] = recursive_pass(
            node_list, node.img_path, rank, layer + 1
        )

        rank += delta - 1 if delta > 1 else delta
        child_count += delta

    if not ret:
        ret = None

    return (max(child_count, 1), ret)


def forward_pass(
    result_list: list[iTreeNode], source_list: list[iTreeNode]
) -> dict[str, dict]:

    node_tree: dict[str, dict] = {}

    rank: int = 0

    for node in source_list:
        node.rank = rank
        node.layer = 0

        childCount, node_tree[node.img_path] = recursive_pass(
            result_list, node.img_path, rank, 1
        )

        if childCount > 3:
            node.rank += int((childCount - 0.6) // 2)

        rank += childCount

    return node_tree


def construct_hierarchy(
    result_list: list[iTreeNode], source_list: list[iTreeNode]
) -> tuple[dict, dict]:

    result_list, source_list = dedupe(result_list, source_list)

    tree = forward_pass(result_list, source_list)

    path_mapping: dict[str, iTreeNode] = {}
    for node in result_list + source_list:
        assert not (node.img_path in path_mapping)
        assert node.layer != -1
        assert node.rank != -1

        path_mapping[node.img_path] = node.to_json()

    return tree, path_mapping
