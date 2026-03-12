import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

class SpherePacker:
    def __init__(self, width, depth, height, radius):
        self.W = width
        self.D = depth
        self.H = height
        self.R = radius
        self.spheres = []  # List of (x, y, z) coordinates

    def is_valid(self, x, y, z, spheres):
        # Check boundary constraints
        if not (self.R <= x <= self.W - self.R and 
                self.R <= y <= self.D - self.R and 
                self.R <= z <= self.H - self.R):
            return False
        
        # Check collisions with existing spheres
        for sx, sy, sz in spheres:
            dist = np.sqrt((x - sx)**2 + (y - sy)**2 + (z - sz)**2)
            if dist < 2 * self.R - 1e-7: # Small epsilon for float precision
                return False
        return True

    def get_z_at(self, pos, existing_spheres):
        """Finds the lowest possible z for a given (x, y)"""
        x, y = pos
        min_z = self.R
        
        for sx, sy, sz in existing_spheres:
            horizontal_dist_sq = (x - sx)**2 + (y - sy)**2
            if horizontal_dist_sq < (2 * self.R)**2:
                # Calculate z using Pythagorean theorem: dz^2 + dxy^2 = (2R)^2
                z_contact = sz + np.sqrt((2 * self.R)**2 - horizontal_dist_sq)
                min_z = max(min_z, z_contact)
        return min_z

    def add_sphere(self):
        # 1. Start at a random x, y
        start_x = np.random.uniform(self.R, self.W - self.R)
        start_y = np.random.uniform(self.R, self.D - self.R)
        
        # 2. Minimize Z by adjusting X and Y (Simulating 'rolling' down)
        res = minimize(
            self.get_z_at, 
            x0=[start_x, start_y],
            args=(self.spheres,),
            bounds=[(self.R, self.W - self.R), (self.R, self.D - self.R)],
            method='L-BFGS-B'
        )
        
        final_x, final_y = res.x
        final_z = self.get_z_at((final_x, final_y), self.spheres)
        
        if final_z + self.R <= self.H:
            self.spheres.append((final_x, final_y, final_z))
            return True
        return False

    def visualize(self):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw the spheres
        for x, y, z in self.spheres:
            u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
            xs = x + self.R * np.cos(u) * np.sin(v)
            ys = y + self.R * np.sin(u) * np.sin(v)
            zs = z + self.R * np.cos(v)
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
packer = SpherePacker(width=10, depth=10, height=10, radius=1)

# Try to add 50 spheres
for _ in range(50):
    packer.add_sphere()

if packer.spheres:
    max_top_height = max(s[2] for s in packer.spheres) + packer.R
    
    # Calculate Filling Ratio
    total_spheres_vol = len(packer.spheres) * (4/3 * np.pi * packer.R**3)
    box_vol_at_max_height = packer.W * packer.D * max_top_height
    filling_ratio = total_spheres_vol / box_vol_at_max_height
    
    print(f"Maximum height reached: {max_top_height:.2f}")
    print(f"Filling ratio: {filling_ratio:.4f} ({filling_ratio*100:.2f}%)")
else:
    print("No spheres were packed.")

packer.visualize()