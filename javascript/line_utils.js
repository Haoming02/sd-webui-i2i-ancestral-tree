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

class TreeNode {
    constructor(self, parent, url) {
        this.self = self;
        this.parent = parent;
        this.url = url;
    }
}
