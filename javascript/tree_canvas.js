let treeSVG = null;

function apply_transform(x, y, s) {
    treeSVG.style.transform = `translate(${x}px, ${y}px) scale(${s})`;
}

function register_dragging(canvas, SVG) {
    const regex = /translate\((-?\d+)px, (-?\d+)px\)/;

    var isDragging = false;
    var startX, startY;
    var posX = 0.0, posY = 0.0;
    var scale = 1.0;

    canvas.addEventListener('mousedown', (e) => {
        if (e.which !== 2)
            return;
        e.preventDefault();

        startX = e.clientX;
        startY = e.clientY;

        isDragging = true;
        canvas.classList.add('mouse_down');
    });

    canvas.addEventListener('mousemove', (e) => {
        if (!isDragging) return;

        const offsetX = e.clientX - startX;
        const offsetY = e.clientY - startY;

        posX += offsetX;
        posY += offsetY;

        startX = e.clientX;
        startY = e.clientY;

        apply_transform(posX, posY, scale);
    });

    canvas.addEventListener('mouseup', (e) => {
        if (e.which !== 2)
            return;
        e.preventDefault();

        isDragging = false;
        canvas.classList.remove('mouse_down');
    });

    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        scale -= 0.1 * Math.sign(e.deltaY);
        apply_transform(posX, posY, scale);
    });
}

function tree_init() {
    const tab = document.getElementById('tab_sd-webui-i2i-ancestral-tree');

    const canvas = document.createElement('div');
    canvas.id = 'tree_canvas';

    const SVG = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    SVG.style.transform = 'translate(0px, 0px)';

    SVG.setAttributeNS(null, 'width', "100%");
    SVG.setAttributeNS(null, 'height', "100%");
    SVG.setAttributeNS(null, 'viewBox', "0 0 1920 640");

    register_dragging(canvas, SVG);

    tab.appendChild(canvas);
    canvas.appendChild(SVG);

    return SVG;
}

function construct_hierarchy(imgs) {
    const l = imgs.length;
    const nodeList = [];
    const sourceList = [];

    for (let i = 0; i < l; i++) {
        const hash = imgs[i].alt;
        const [self, parent] = hash.split('-');

        if (parent === 'None')
            sourceList.push(new TreeNode(self, null, imgs[i].src));
        else
            nodeList.push(new TreeNode(self, parent, imgs[i].src));
    }

    return [nodeList, sourceList];
}

function i2i_construct_tree() {
    if (treeSVG === null)
        treeSVG = tree_init();

    const gallery = document.getElementById('i2i_tree_nodes');
    const imgs = gallery.querySelectorAll('img');

    if (imgs.length == 0)
        return;

    const [nodeList, sourceList] = construct_hierarchy(imgs);

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
            alert('Image Clicked~');
        });

        treeSVG.appendChild(image);
        i++;
    });
}
