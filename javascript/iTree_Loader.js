let treeSVG = null;

function construct_hierarchy(imgs) {
    const l = imgs.length;
    const nodeList = [];
    const sourceList = [];

    for (let i = 0; i < l; i++) {
        const hash = imgs[i].alt;
        const [path, self, parent] = hash.split('_-');

        if (parent === 'None')
            sourceList.push(new TreeNode(self, null, imgs[i].src, path));
        else
            nodeList.push(new TreeNode(self, parent, imgs[i].src, path));
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

function i2i_construct_tree() {
    if (treeSVG === null)
        treeSVG = tree_init();
    else
        while (treeSVG.firstChild) treeSVG.removeChild(treeSVG.lastChild);

    document.getElementById('i2i_tree_nodes').parentElement.style.background = 'var(--block-background-fill)';

    const imgs = document.getElementById('i2i_tree_nodes').querySelectorAll('img');
    if (imgs.length == 0)
        return;

    const [allNodeList, allSourceList] = construct_hierarchy(imgs);
    const [nodeList, sourceList] = prune_unused(allNodeList, allSourceList);

    // console.log(nodeList);
    // console.log(sourceList);

    const img2open_text = document.getElementById('i2i_tree_img_open').querySelector('textarea');
    const img2open_btn = document.getElementById('i2i_tree_oimg_btn');

    let i = 1;

    sourceList.forEach((sauce) => {
        const image = document.createElementNS("http://www.w3.org/2000/svg", "image");
        image.setAttribute("href", sauce.url);

        image.setAttribute("x", 128 * i);
        image.setAttribute("y", "128");
        image.setAttribute("width", "64");
        image.setAttribute("height", "64");

        image.classList.add('img');

        image.addEventListener('click', () => {
            img2open_text.value = sauce.path;
            updateInput(img2open_text);
            img2open_btn.click();
        });

        treeSVG.appendChild(image);
        i++;
    });
}
