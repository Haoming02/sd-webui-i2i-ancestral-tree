class TreeNode {
    constructor(self, parent, url, path) {
        this.self = self;
        this.parent = parent;
        this.url = url;
        this.path = path;
    }
}

function apply_transform(delta_x, delta_y, delta_s, SVG) {
    let [x, y, w, h] = SVG.getAttributeNS(null, 'viewBox').split(' ').map(parseFloat);

    if (delta_s === 0.0) {
        x -= delta_x * (w / 1000.0);
        y -= delta_y * (w / 1000.0);
    }
    else {
        delta_s += 1.0;

        const og_x = x + w / 2.0;
        const og_y = y + h / 2.0;

        if (delta_s > 1.0) {
            if (w > 3840)
                return;
        } else {
            if (w < 64)
                return;
        }

        w *= delta_s;
        h *= delta_s;

        x = og_x - w / 2.0;
        y = og_y - h / 2.0;
    }

    SVG.setAttributeNS(null, 'viewBox', `${x} ${y} ${w} ${h}`);
}

function register_dragging(canvas, SVG) {
    var isDragging = false;
    var startX = 0, startY = 0;

    canvas.setAttribute('tabindex', 0);

    canvas.addEventListener('keydown', (e) => {
        if (e.key === ' ')
            SVG.setAttributeNS(null, 'viewBox', '0 0 1280 640');
    });

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
        canvas.focus();
        if (!isDragging) return;

        const offsetX = e.clientX - startX;
        const offsetY = e.clientY - startY;

        apply_transform(offsetX, offsetY, 0.0, SVG);

        startX = e.clientX;
        startY = e.clientY;
    });

    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        apply_transform(0.0, 0.0, Math.sign(e.deltaY) * 0.1, SVG);
    });

    canvas.addEventListener('mouseup', (e) => {
        if (e.which !== 2)
            return;
        e.preventDefault();

        isDragging = false;
        canvas.classList.remove('mouse_down');
    });

    canvas.addEventListener('mouseleave', (e) => {
        if (e.which !== 2)
            return;
        e.preventDefault();

        isDragging = false;
        canvas.classList.remove('mouse_down');
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
    SVG.setAttributeNS(null, 'viewBox', "0 0 1280 640");

    register_dragging(canvas, SVG);

    tab.appendChild(canvas);
    canvas.appendChild(SVG);

    return SVG;
}

function drawLine(p1x, p1y, p2x, p2y) {
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const offset = (Math.abs(p2x - p1x) + Math.abs(p2x - p1x)) / 4;

    // mid-point of line:
    const mpx = (p2x + p1x) * 0.5;
    const mpy = (p2y + p1y) * 0.5;

    // angle of perpendicular to line:
    const theta = Math.atan2(p2y - p1y, p2x - p1x) - Math.PI / 2;

    // location of control point:
    const c1x = mpx + offset * Math.cos(theta);
    const c1y = mpy + offset * Math.sin(theta);

    // construct the command to draw a quadratic curve
    const curve = `M${p1x} ${p1y} Q${c1x} ${c1y} ${p2x} ${p2y}`;

    line.setAttributeNS(null, 'd', curve);
    line.setAttributeNS(null, 'stroke', 'cyan');
    line.setAttributeNS(null, 'stroke-width', '2');
    line.setAttributeNS(null, 'fill', 'none');

    return line;
}
