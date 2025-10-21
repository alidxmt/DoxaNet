const svg = document.getElementById("svgCanvas");
const radius = 25;
const centerX = 300;
const centerY = 300;
const gap = 10; // minimum gap between circles

let circleCounter = 1; // for unique IDs

function drawCircle() {
    const nProps = parseInt(document.getElementById("n_props").value);

    // If no circles exist, draw initial W
    if (svg.querySelectorAll("circle").length === 0) {
        const center = getCenter();
        drawCircleAt(center.x, center.y, radius, "W", "W");
    }

    // Select all circles with ID and split them
    const circles = Array.from(svg.querySelectorAll("circle[id]"));
    circles.forEach(c => {
        const id = c.getAttribute("id");
        if (id) splitCircle(id, nProps);
    });
}

function splitCircle(circleId, depthRemaining) {
    if (depthRemaining <= 0) return;

    const original = document.getElementById(circleId);
    if (!original) return;

    const cx = parseFloat(original.getAttribute("cx"));
    const cy = parseFloat(original.getAttribute("cy"));
    const r = parseFloat(original.getAttribute("r"));
    const fill = original.getAttribute("fill");
    const stroke = original.getAttribute("stroke");

    // Remove original
    svg.removeChild(original);

    // Create two children with unique IDs
    const c1 = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    const c2 = document.createElementNS("http://www.w3.org/2000/svg", "circle");

    c1.setAttribute("id", "c" + circleCounter++);
    c2.setAttribute("id", "c" + circleCounter++);

    [c1, c2].forEach(c => {
        c.setAttribute("cx", cx);
        c.setAttribute("cy", cy);
        c.setAttribute("r", r);
        c.setAttribute("fill", fill);
        c.setAttribute("stroke", stroke);
        c.setAttribute("stroke-width", 2);
        svg.appendChild(c);
    });

    // Labels
    const t1 = document.createElementNS("http://www.w3.org/2000/svg", "text");
    const t2 = document.createElementNS("http://www.w3.org/2000/svg", "text");

    [t1, t2].forEach(t => {
        t.setAttribute("x", cx);
        t.setAttribute("y", cy + r + 5);
        t.setAttribute("dominant-baseline", "hanging");
        t.textContent = "W";
        svg.appendChild(t);
    });

    // Animate separation
    const dx = 60;
    const steps = 60;
    let step = 0;

    function animate() {
        if (step <= steps) {
            const progress = step / steps;
            c1.setAttribute("cx", cx - dx * progress / 2);
            c2.setAttribute("cx", cx + dx * progress / 2);
            t1.setAttribute("x", cx - dx * progress / 2);
            t2.setAttribute("x", cx + dx * progress / 2);
            step++;
            requestAnimationFrame(animate);
        } else {
            // After animation, recursively split children
            splitCircle(c1.getAttribute("id"), depthRemaining - 1);
            splitCircle(c2.getAttribute("id"), depthRemaining - 1);
        }
    }

    animate();
}




// Recursive split function
function splitCircle(circleId) {
    const original = document.getElementById(circleId);
    if (!original) return;

    const cx = parseFloat(original.getAttribute("cx"));
    const cy = parseFloat(original.getAttribute("cy"));
    const r = parseFloat(original.getAttribute("r"));
    const fill = original.getAttribute("fill");
    const stroke = original.getAttribute("stroke");

    // Remove original circle
    svg.removeChild(original);

    // Create two new circles
    const c1 = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    const c2 = document.createElementNS("http://www.w3.org/2000/svg", "circle");

    [c1, c2].forEach(c => {
        c.setAttribute("cx", cx);
        c.setAttribute("cy", cy);
        c.setAttribute("r", r);
        c.setAttribute("fill", fill);
        c.setAttribute("stroke", stroke);
        c.setAttribute("stroke-width", 2);
        svg.appendChild(c);
    });

    // Labels
    const t1 = document.createElementNS("http://www.w3.org/2000/svg", "text");
    const t2 = document.createElementNS("http://www.w3.org/2000/svg", "text");

    [t1, t2].forEach(t => {
        t.setAttribute("x", cx);
        t.setAttribute("y", cy + r + 5);
        t.setAttribute("dominant-baseline", "hanging");
        t.textContent = "W";
        svg.appendChild(t);
    });

    // Animate moving apart
    const dx = 60;
    const steps = 60;
    let step = 0;

    function animate() {
        if (step <= steps) {
            const progress = step / steps;
            c1.setAttribute("cx", cx - dx * progress / 2);
            c2.setAttribute("cx", cx + dx * progress / 2);
            t1.setAttribute("x", cx - dx * progress / 2);
            t2.setAttribute("x", cx + dx * progress / 2);
            step++;
            requestAnimationFrame(animate);
        }
    }

    animate();
}


// Animate a circle from its starting position to target
function animateMove(circle, targetX, targetY, duration = 400, callback) {
    const c = drawSingleCircle(circle.x, circle.y, circle.r);
    const startTime = performance.now();
    const startX = circle.x;
    const startY = circle.y;

    function animate(time) {
        let t = (time - startTime) / duration;
        if (t > 1) t = 1;

        const currentX = startX + (targetX - startX) * t;
        const currentY = startY + (targetY - startY) * t;

        c.setAttribute("cx", currentX);
        c.setAttribute("cy", currentY);

        if (t < 1) {
            requestAnimationFrame(animate);
        } else if (callback) {
            callback();
        }
    }

    requestAnimationFrame(animate);
}

// Draw a single circle and return the element
function drawSingleCircle(x, y, r) {
    const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("cx", x);
    c.setAttribute("cy", y);
    c.setAttribute("r", r);
    c.setAttribute("fill", "lightblue");
    c.setAttribute("stroke", "darkblue");
    c.setAttribute("stroke-width", 1);
    svg.appendChild(c);
    return c;
}




function splitCircle(circleId) {
    const original = document.getElementById(circleId);
    if (!original) return;

    const cx = parseFloat(original.getAttribute("cx"));
    const cy = parseFloat(original.getAttribute("cy"));
    const r = parseFloat(original.getAttribute("r"));
    const fill = original.getAttribute("fill");
    const stroke = original.getAttribute("stroke");

    // Remove original circle
    svg.removeChild(original);

    // Create two new circles at the same position initially
    const c1 = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    const c2 = document.createElementNS("http://www.w3.org/2000/svg", "circle");

    [c1, c2].forEach(c => {
        c.setAttribute("cx", cx);
        c.setAttribute("cy", cy);
        c.setAttribute("r", r);
        c.setAttribute("fill", fill);
        c.setAttribute("stroke", stroke);
        c.setAttribute("stroke-width", 2);
        svg.appendChild(c);
    });

    // Labels
    const t1 = document.createElementNS("http://www.w3.org/2000/svg", "text");
    const t2 = document.createElementNS("http://www.w3.org/2000/svg", "text");

    [t1, t2].forEach(t => {
        t.setAttribute("x", cx);
        t.setAttribute("y", cy + r + 5);
        t.setAttribute("dominant-baseline", "hanging");
        t.textContent = "W";
        svg.appendChild(t);
    });

    // Animation parameters
    const dx = 60; // horizontal separation
    const steps = 60;
    let step = 0;

    function animate() {
        if (step <= steps) {
            const progress = step / steps;
            c1.setAttribute("cx", cx - dx * progress / 2);
            c2.setAttribute("cx", cx + dx * progress / 2);
            t1.setAttribute("x", cx - dx * progress / 2);
            t2.setAttribute("x", cx + dx * progress / 2);
            step++;
            requestAnimationFrame(animate);
        }
    }

    animate();
}
