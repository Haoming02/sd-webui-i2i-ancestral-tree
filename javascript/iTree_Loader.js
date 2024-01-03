const iTree_Node_Size = 100;

class iTree {
    static treeSVG = null;
    static treeGallery = null;
    static img2open_text = null;
    static img2open_btn = null;

    static hashMap = null;

    static nodeTree = null;
    static nodeList = null;
    static sourceList = null;
}

function construct_hierarchy(imgs) {
    const l = imgs.length;
    const nodeList = [];
    const sourceList = [];

    for (let i = 0; i < l; i++) {
        const hash = imgs[i].alt;
        const [path, self, parent] = hash.split('_-');

        if (parent === 'None')
            sourceList.push(new iTreeNode(self, null, imgs[i].src, path));
        else
            nodeList.push(new iTreeNode(self, parent, imgs[i].src, path));
    }

    return [nodeList, sourceList];
}

function prune_unused(nodeList, sourceList) {
    const srcs = new Set(nodeList.map(node => node.parent));
    sourceList = sourceList.filter(item => srcs.has(item.self));

    const selfs = new Set([...nodeList, ...sourceList].map(node => node.self));
    nodeList = nodeList.filter(item => selfs.has(item.parent));

    return [nodeList, sourceList];
}

function recursive_mapping(parent, rank, layer) {
    const ret = {};
    var childCount = 0;

    iTree.nodeList.forEach((node) => {
        if (node.parent !== parent.self)
            return;

        var delta = 0;

        node.rank = rank;
        node.layer = layer;
        [delta, ret[node.self]] = recursive_mapping(node, rank, layer + 1);
        rank += (delta > 1 ? delta - 1 : delta);
        childCount += delta;
    });

    return [Math.max(childCount, 1), ret];
}

function forward_pass() {
    iTree.nodeTree = {};

    var rank = 0;
    var childCount = 0;

    iTree.sourceList.forEach((node) => {
        node.rank = rank;
        node.layer = 0;

        [childCount, iTree.nodeTree[node.self]] = recursive_mapping(node, rank, 1);
        rank += childCount;
    });
}

function get_xCoord(layer) {
    return 25 + 250 * layer;
}

function get_yCoord(layer, rank) {
    return 200 * rank - 100 * layer;
}

function draw_connections(tree) {
    for (const [key, value] of Object.entries(tree)) {

        if (value === null || Object.keys(value).length === 0)
            continue;

        const from = iTree.hashMap[key];
        const x1 = get_xCoord(from.layer) + iTree_Node_Size * 0.85;
        const y1 = get_yCoord(from.layer, from.rank) + iTree_Node_Size / 2;

        for (let i = 0; i < Object.keys(value).length; i++) {
            const to = iTree.hashMap[Object.keys(value)[i]];
            const x2 = get_xCoord(to.layer) + iTree_Node_Size * 0.15;
            const y2 = get_yCoord(to.layer, to.rank) + iTree_Node_Size / 2;

            const l = drawLine(x1, y1, x2, y2);
            iTree.treeSVG.appendChild(l);
        }

        draw_connections(value);
    }
}

function i2i_construct_tree() {
    while (iTree.treeSVG.firstChild)
        iTree.treeSVG.removeChild(iTree.treeSVG.lastChild);

    const imgs = iTree.treeGallery.querySelectorAll('img');
    if (imgs.length == 0)
        return;

    const [allNodeList, allSourceList] = construct_hierarchy(imgs);
    [iTree.nodeList, iTree.sourceList] = prune_unused(allNodeList, allSourceList);

    // console.log(iTree.nodeList);
    // console.log(iTree.sourceList);

    iTree.hashMap = {};
    [...iTree.sourceList, ...iTree.nodeList].forEach((node) => {
        iTree.hashMap[node.self] = node;
    });

    // console.log(iTree.hashMap);

    forward_pass();

    // console.log(iTree.nodeTree);

    draw_connections(iTree.nodeTree);

    [...iTree.sourceList, ...iTree.nodeList].forEach((node) => {
        const image = document.createElementNS("http://www.w3.org/2000/svg", "image");
        image.classList.add('img');

        image.setAttribute("href", node.url);
        image.setAttribute("x", get_xCoord(node.layer));
        image.setAttribute("y", get_yCoord(node.layer, node.rank));
        image.setAttribute("width", iTree_Node_Size);
        image.setAttribute("height", iTree_Node_Size);

        image.addEventListener('click', () => {
            iTree.img2open_text.value = node.path;
            updateInput(iTree.img2open_text);
            iTree.img2open_btn.click();
        });

        iTree.treeSVG.appendChild(image);
    });

}

onUiLoaded(async () => {
    iTree.treeSVG = tree_init();

    iTree.treeGallery = document.getElementById('i2i_tree_nodes');
    iTree.treeGallery.parentElement.style.background = 'var(--block-background-fill)';

    iTree.img2open_text = document.getElementById('i2i_tree_img_open').querySelector('textarea');
    iTree.img2open_btn = document.getElementById('i2i_tree_oimg_btn');
});
