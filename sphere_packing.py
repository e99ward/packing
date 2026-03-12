import math

def get_hcp_packing(W, H, D, r):
    """
    Computes sphere positions using Hexagonal Close-Packing (HCP).
    This is the densest packing for spheres (approx 74% density).
    """
    spheres = []
    
    # Constants for HCP geometry
    layer_height = math.sqrt(8/3) * r
    row_spacing = math.sqrt(3) * r
    
    nz = int((D - 2*r) // layer_height) + 1
    
    for k in range(nz):
        z = r + k * layer_height
        
        # Layer type A or B
        is_layer_b = (k % 2 == 1)
        
        # Vertical offset for rows within the layer
        y_offset = (math.sqrt(3)/3 * r) if is_layer_b else 0
        ny = int((H - 2*r - y_offset) // row_spacing) + 1
        
        for j in range(ny):
            y = r + y_offset + j * row_spacing
            
            # Horizontal offset for spheres within the row
            # In HCP, row shifting alternates based on layer AND row index
            if is_layer_b:
                x_offset = r if (j % 2 == 0) else 0
            else:
                x_offset = r if (j % 2 == 1) else 0
                
            nx = int((W - 2*r - x_offset) // (2*r)) + 1
            
            for i in range(nx):
                x = r + x_offset + i * 2 * r
                spheres.append((x, y, z))
                
    return spheres

def generate_threejs_html(W, H, D, r, spheres, filename="sphere_packing.html"):
    """
    Generates an HTML file with Three.js for 3D visualization.
    """
    sphere_data = ", ".join([f"{{x: {s[0]}, y: {s[1]}, z: {s[2]}}}" for s in spheres])
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>3D Sphere Packing</title>
    <style>
        body {{ margin: 0; overflow: hidden; font-family: sans-serif; background: #111; }}
        #info {{
            position: absolute; top: 10px; left: 10px; color: white;
            background: rgba(0,0,0,0.7); padding: 15px; border-radius: 8px;
            pointer-events: none;
        }}
        canvas {{ display: block; }}
    </style>
</head>
<body>
    <div id="info">
        <h2>3D Sphere Packing</h2>
        <p>Box: {W} x {H} x {D}</p>
        <p>Radius: {r}</p>
        <p>Total Spheres: {len(spheres)}</p>
        <p><small>Left click to rotate | Scroll to zoom</small></p>
    </div>
    <script type="importmap">
        {{
            "imports": {{
                "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
                "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
            }}
        }}
    </script>
    <script type="module">
        import * as THREE from 'three';
        import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a1a);

        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
        camera.position.set({W*1.5}, {H*1.5}, {D*1.5});

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // Add Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(1, 1, 1).normalize();
        scene.add(directionalLight);

        // Draw Box Wireframe
        const boxGeometry = new THREE.BoxGeometry({W}, {H}, {D});
        const boxWireframe = new THREE.EdgesGeometry(boxGeometry);
        const boxMaterial = new THREE.LineBasicMaterial({{ color: 0x00ff00 }});
        const boxLine = new THREE.LineSegments(boxWireframe, boxMaterial);
        // Center the box
        boxLine.position.set({W/2}, {H/2}, {D/2});
        scene.add(boxLine);

        // InstancedMesh for performance
        const sphereRadius = {r};
        const spheresData = [{sphere_data}];
        const geometry = new THREE.SphereGeometry(sphereRadius, 32, 16);
        const material = new THREE.MeshPhongMaterial({{ 
            color: 0x4682B4, 
            transparent: true, 
            opacity: 0.8,
            shininess: 100
        }});

        const instancedMesh = new THREE.InstancedMesh(geometry, material, spheresData.length);
        const dummy = new THREE.Object3D();

        spheresData.forEach((pos, i) => {{
            dummy.position.set(pos.x, pos.y, pos.z);
            dummy.updateMatrix();
            instancedMesh.setMatrixAt(i, dummy.matrix);
        }});

        scene.add(instancedMesh);
        controls.target.set({W/2}, {H/2}, {D/2});

        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});

        animate();
    </script>
</body>
</html>
"""
    with open(filename, "w") as f:
        f.write(html_template)
    print(f"Generated {filename} with {len(spheres)} spheres.")

if __name__ == "__main__":
    # Parameters (Width, Height, Depth, Radius)
    BOX_W, BOX_H, BOX_D = 400, 300, 200
    R = 15

    spheres = get_hcp_packing(BOX_W, BOX_H, BOX_D, R)
    generate_threejs_html(BOX_W, BOX_H, BOX_D, R, spheres)
