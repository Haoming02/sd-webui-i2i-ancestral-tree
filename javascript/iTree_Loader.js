class iTree {
    static treeSVG = null;
    static treeGallery = null;
    static img2open_text = null;

    static hashMap = null;
    static nodeTree = null;

    static iTree_Node_Size = 128;
}

function get_xCoord(layer) {
    return (iTree.iTree_Node_Size * 3) * layer;
}

function get_yCoord(layer, rank) {
    return (iTree.iTree_Node_Size * 1.5) * rank - (iTree.iTree_Node_Size * 1.5 / 2) * layer;
}

function draw_connections(tree) {
    for (const [key, value] of Object.entries(tree)) {

        if (value == null)
            continue;

        const from = iTree.hashMap[key];
        const x1 = get_xCoord(from.layer) + iTree.iTree_Node_Size * 0.85;
        const y1 = get_yCoord(from.layer, from.rank) + iTree.iTree_Node_Size / 2;

        [...Object.keys(value)].forEach((childNode) => {
            const to = iTree.hashMap[childNode];
            const x2 = get_xCoord(to.layer) + iTree.iTree_Node_Size * 0.15;
            const y2 = get_yCoord(to.layer, to.rank) + iTree.iTree_Node_Size / 2;

            iTree.treeSVG.appendChild(drawLine(x1, y1, x2, y2, to.mode));
        })

        draw_connections(value);
    }
}

function i2i_construct_tree() {
    while (iTree.treeSVG.firstChild)
        iTree.treeSVG.removeChild(iTree.treeSVG.lastChild);

    const data = iTree.treeGallery.querySelector('textarea').value;

    const [tree_txt, path_mapping_txt] = data.split("-[=]-");

    iTree.nodeTree = JSON.parse(tree_txt);
    iTree.hashMap = JSON.parse(path_mapping_txt);

    draw_connections(iTree.nodeTree);

    [...Object.values(iTree.hashMap)].forEach((node) => {
        const image = document.createElementNS("http://www.w3.org/2000/svg", "image");
        image.classList.add('img');

        image.setAttribute("href", node.url);
        image.setAttribute("x", get_xCoord(node.layer));
        image.setAttribute("y", get_yCoord(node.layer, node.rank));
        image.setAttribute("width", iTree.iTree_Node_Size);
        image.setAttribute("height", iTree.iTree_Node_Size);

        image.addEventListener('click', () => {
            iTree.img2open_text.value = node.path;
            updateInput(iTree.img2open_text);
        });

        iTree.treeSVG.appendChild(image);
    });

}

onUiLoaded(async () => {
    iTree.treeSVG = tree_init();

    iTree.treeGallery = document.getElementById('i2i_tree_nodes');
    iTree.treeGallery.parentElement.style.background = 'var(--block-background-fill)';

    iTree.img2open_text = document.getElementById('i2i_tree_img_open').querySelector('textarea');
});
