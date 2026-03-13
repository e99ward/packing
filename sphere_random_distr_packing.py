import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

class SpherePacker:
    def __init__(self, width, depth, height, mean_radius, std_radius):
        self.W = width
        self.D = depth
        self.H = height
        self.mean_R = mean_radius
        self.std_R = std_radius
        self.spheres = []  # List of (x, y, z, r) coordinates

    def is_valid(self, x, y, z, r, spheres):
        # Check boundary constraints
        if not (r <= x <= self.W - r and 
                r <= y <= self.D - r and 
                r <= z <= self.H - r):
            return False
        
        # Check collisions with existing spheres
        for sx, sy, sz, sr in spheres:
            dist = np.sqrt((x - sx)**2 + (y - sy)**2 + (z - sz)**2)
            if dist < (r + sr) - 1e-7: # Small epsilon for float precision
                return False
        return True

    def get_z_at(self, pos, current_r, existing_spheres):
        """Finds the lowest possible z for a given (x, y) and radius current_r"""
        x, y = pos
        min_z = current_r
        
        for sx, sy, sz, sr in existing_spheres:
            horizontal_dist_sq = (x - sx)**2 + (y - sy)**2
            if horizontal_dist_sq < (current_r + sr)**2:
                # Calculate z using Pythagorean theorem: dz^2 + dxy^2 = (R1+R2)^2
                z_contact = sz + np.sqrt((current_r + sr)**2 - horizontal_dist_sq)
                min_z = max(min_z, z_contact)
        return min_z

    def add_sphere(self):
        # 1. Generate a random radius from Gaussian distribution
        # Ensure radius is positive
        r = -1
        while r <= 0:
            r = np.random.normal(self.mean_R, self.std_R)

        # 2. Start at a random x, y
        start_x = np.random.uniform(r, self.W - r)
        start_y = np.random.uniform(r, self.D - r)
        
        # 3. Minimize Z by adjusting X and Y (Simulating 'rolling' down)
        res = minimize(
            self.get_z_at, 
            x0=[start_x, start_y],
            args=(r, self.spheres,),
            bounds=[(r, self.W - r), (r, self.D - r)],
            method='L-BFGS-B'
        )
        
        final_x, final_y = res.x
        final_z = self.get_z_at((final_x, final_y), r, self.spheres)
        
        if final_z + r <= self.H:
            self.spheres.append((final_x, final_y, final_z, r))
            return True
        return False

    def visualize(self):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw the spheres
        for x, y, z, r in self.spheres:
            u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
            xs = x + r * np.cos(u) * np.sin(v)
            ys = y + r * np.sin(u) * np.sin(v)
            zs = z + r * np.cos(v)
            ax.plot_surface(xs, ys, zs, color='skyblue', edgecolor='k', alpha=0.6)

        ax.set_xlim(0, self.W)
        ax.set_ylim(0, self.D)
        ax.set_zlim(0, self.H)
        # ax.set_box_aspect((self.W, self.D, self.H))
        ax.set_aspect('equal')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.title(f"Sphere Packing (Count: {len(self.spheres)})")
        plt.show()

# --- Execution ---
packer = SpherePacker(width=10, depth=10, height=10, mean_radius=1, std_radius=0.2)

# Try to add 50 spheres
for _ in range(50):
    packer.add_sphere()

if packer.spheres:
    max_top_height = max(s[2] + s[3] for s in packer.spheres)
    
    # Calculate Filling Ratio
    total_spheres_vol = sum(4/3 * np.pi * s[3]**3 for s in packer.spheres)
    box_vol_at_max_height = packer.W * packer.D * max_top_height
    filling_ratio = total_spheres_vol / box_vol_at_max_height
    
    print(f"Maximum height reached: {max_top_height:.2f}")
    print(f"Filling ratio: {filling_ratio:.4f} ({filling_ratio*100:.2f}%)")
else:
    print("No spheres were packed.")

packer.visualize()