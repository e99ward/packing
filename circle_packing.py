import math

def get_square_packing(W, H, r):
    """
    Computes square packing circle positions.
    """
    circles = []
    nx = int(W // (2 * r))
    ny = int(H // (2 * r))
    for i in range(nx):
        for j in range(ny):
            circles.append((r + i * 2 * r, r + j * 2 * r))
    return circles

def get_hexagonal_packing(W, H, r):
    """
    Computes hexagonal packing circle positions.
    """
    circles = []
    # Vertical distance between row centers
    dy = math.sqrt(3) * r
    ny = int((H - 2 * r) // dy) + 1
    
    for row in range(ny):
        y = r + row * dy
        # Even rows start at x=r, odd rows at x=2r (offset by r)
        offset = r if (row % 2 == 1) else 0
        nx = int((W - 2 * r - offset) // (2 * r)) + 1
        for col in range(nx):
            x = r + offset + col * 2 * r
            circles.append((x, y))
    return circles

def generate_svg_html(W, H, r, circles, filename="circle_packing.html"):
    """
    Generates an HTML file containing an SVG visualization of the packing.
    """
    svg_content = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="border: 2px solid black; background: #f0f0f0;">'
    ]
    for x, y in circles:
        svg_content.append(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="rgba(70, 130, 180, 0.6)" stroke="steelblue" stroke-width="1" />')
    svg_content.append('</svg>')
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Circle Packing Visualization</title>
    <style>
        body {{ font-family: sans-serif; display: flex; flex-direction: column; align-items: center; padding: 20px; background: #fafafa; }}
        h1 {{ color: #333; }}
        .info {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background: white; }}
        .container {{ box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <h1>Circle Packing Results</h1>
    <div class="info">
        <p><strong>Box Size:</strong> {W} x {H}</p>
        <p><strong>Circle Radius:</strong> {r}</p>
        <p><strong>Total Circles:</strong> {len(circles)}</p>
    </div>
    <div class="container">
        {"".join(svg_content)}
    </div>
</body>
</html>
"""
    with open(filename, "w") as f:
        f.write(html_template)
    print(f"Generated {filename} with {len(circles)} circles.")

if __name__ == "__main__":
    # Parameters
    BOX_WIDTH = 600
    BOX_HEIGHT = 400
    CIRCLE_RADIUS = 20

    # Try both packing methods
    sq_circles = get_square_packing(BOX_WIDTH, BOX_HEIGHT, CIRCLE_RADIUS)
    hex_circles = get_hexagonal_packing(BOX_WIDTH, BOX_HEIGHT, CIRCLE_RADIUS)

    # Choose the better one
    if len(hex_circles) >= len(sq_circles):
        print(f"Hexagonal packing is better ({len(hex_circles)} vs {len(sq_circles)})")
        best_circles = hex_circles
    else:
        print(f"Square packing is better ({len(sq_circles)} vs {len(hex_circles)})")
        best_circles = sq_circles

    generate_svg_html(BOX_WIDTH, BOX_HEIGHT, CIRCLE_RADIUS, best_circles)
