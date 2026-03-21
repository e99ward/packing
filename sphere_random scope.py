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

    def shake(self, magnitude=0.5):
        """Simulates shaking by perturbing spheres and re-settling them to minimize Z."""
        new_spheres = []
        # Re-settle each sphere in the order they were added
        for x, y, z, r in self.spheres:
            # small perturbation
            if z < r + 1e-7: # Small epsilon for float precision
                pertub_x = np.random.normal(0.0, magnitude)
                if x + pertub_x > r and x + pertub_x < self.W - r:
                    x = x + pertub_x
                pertub_y = np.random.normal(0.0, magnitude)
                if y + pertub_y > r and y + pertub_y < self.D - r:
                    y = y + pertub_y
            # Re-optimize (x, y) within a small neighborhood to find a lower Z
            res = minimize(
                self.get_z_at, 
                x0=[x, y],
                args=(r, new_spheres,),
                bounds=[(max(r, x - magnitude), min(self.W - r, x + magnitude)), 
                        (max(r, y - magnitude), min(self.D - r, y + magnitude))],
                method='L-BFGS-B'
            )
            nx, ny = res.x
            nz = self.get_z_at((nx, ny), r, new_spheres)
            new_spheres.append((nx, ny, nz, r))
        
        self.spheres = new_spheres

    def condense(self, ceiling=1.0):
        """condensing spheres to maximize Z."""
        new_spheres = []
        # condense each sphere in the reverse order they were added
        # before that make the height up-side down
        for x, y, z, r in self.spheres:
            z = ceiling - z
        for x, y, z, r in reversed(self.spheres):
            # Re-optimize (x, y) within a small neighborhood to find a lower Z
            res = minimize(
                self.get_z_at, 
                x0=[x, y],
                args=(r, new_spheres,),
                bounds=[(r, self.W - r), (r, self.D - r)],
                method='L-BFGS-B'
            )
            nx, ny = res.x
            nz = self.get_z_at((nx, ny), r, new_spheres)
            new_spheres.append((nx, ny, nz, r))

        self.spheres = new_spheres

    def calculate_scoping_density(self, x_range, y_range, z_range, grid_res=40):
        """Calculates filling density in a sub-cube, accounting for truncated spheres."""
        x_min, x_max = x_range
        y_min, y_max = y_range
        z_min, z_max = z_range
        
        # Create a grid of points within the scoping cube
        x = np.linspace(x_min, x_max, grid_res)
        y = np.linspace(y_min, y_max, grid_res)
        z = np.linspace(z_min, z_max, grid_res)
        xv, yv, zv = np.meshgrid(x, y, z, indexing='ij')
        points = np.stack([xv.ravel(), yv.ravel(), zv.ravel()], axis=1)
        
        # Check how many points are inside any sphere
        inside_mask = np.zeros(len(points), dtype=bool)
        for sx, sy, sz, sr in self.spheres:
            # Optimization: only check spheres that could overlap the scoping cube
            if (sx + sr < x_min or sx - sr > x_max or
                sy + sr < y_min or sy - sr > y_max or
                sz + sr < z_min or sz - sr > z_max):
                continue
                
            dists_sq = (points[:, 0] - sx)**2 + (points[:, 1] - sy)**2 + (points[:, 2] - sz)**2
            inside_mask |= (dists_sq <= sr**2)
            
        filling_ratio = np.mean(inside_mask)
        return filling_ratio

    def visualize(self, scoping_cube=None):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw the spheres
        for x, y, z, r in self.spheres:
            u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
            xs = x + r * np.cos(u) * np.sin(v)
            ys = y + r * np.sin(u) * np.sin(v)
            zs = z + r * np.cos(v)
            ax.plot_surface(xs, ys, zs, color='skyblue', edgecolor='k', alpha=0.6)

        # Draw scoping cube if provided
        if scoping_cube:
            x_r, y_r, z_r = scoping_cube
            # Draw edges of the scoping cube
            for s, e in [((x_r[0], y_r[0], z_r[0]), (x_r[1], y_r[0], z_r[0])),
                         ((x_r[0], y_r[1], z_r[0]), (x_r[1], y_r[1], z_r[0])),
                         ((x_r[0], y_r[0], z_r[1]), (x_r[1], y_r[0], z_r[1])),
                         ((x_r[0], y_r[1], z_r[1]), (x_r[1], y_r[1], z_r[1])),
                         ((x_r[0], y_r[0], z_r[0]), (x_r[0], y_r[1], z_r[0])),
                         ((x_r[1], y_r[0], z_r[0]), (x_r[1], y_r[1], z_r[0])),
                         ((x_r[0], y_r[0], z_r[1]), (x_r[0], y_r[1], z_r[1])),
                         ((x_r[1], y_r[0], z_r[1]), (x_r[1], y_r[1], z_r[1])),
                         ((x_r[0], y_r[0], z_r[0]), (x_r[0], y_r[0], z_r[1])),
                         ((x_r[1], y_r[0], z_r[0]), (x_r[1], y_r[0], z_r[1])),
                         ((x_r[0], y_r[1], z_r[0]), (x_r[0], y_r[1], z_r[1])),
                         ((x_r[1], y_r[1], z_r[0]), (x_r[1], y_r[1], z_r[1]))]:
                ax.plot([s[0], e[0]], [s[1], e[1]], [s[2], e[2]], color='red', linewidth=2)

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

def report_stats(packer, label, scoping_cube=None) -> float:
    if packer.spheres:
        max_top_height = max(s[2] + s[3] for s in packer.spheres)

        # Calculate Global Filling Ratio
        total_spheres_vol = sum(4/3 * np.pi * s[3]**3 for s in packer.spheres)
        box_vol_at_max_height = packer.W * packer.D * max_top_height
        filling_ratio = total_spheres_vol / box_vol_at_max_height
        print(f"\n[{label}]")
        print(f"Maximum height reached: {max_top_height:.2f}")
        print(f"Global filling ratio: {filling_ratio:.4f} ({filling_ratio*100:.2f}%)")
        
        if scoping_cube:
            s_density = packer.calculate_scoping_density(*scoping_cube)
            print(f"Scoping cube density: {s_density:.4f} ({s_density*100:.2f}%)")
    else:
        print(f"\n[{label}] No spheres were packed.")

    return max_top_height

# Define a scoping cube (x_range, y_range, z_range)
scope = ([2.5, 7.5], [2.5, 7.5], [1.0, 5.0])

max_height = report_stats(packer, "Initial Packing", scope)
packer.visualize(scoping_cube=scope)

print("\nShaking the box...")
packer.shake(magnitude=0.5)
max_height = report_stats(packer, "After Shaking", scope)
packer.visualize(scoping_cube=scope)

print("\nCondensing the box...")
packer.condense(ceiling=max_height)
max_height = report_stats(packer, "After Condensing", scope)
packer.visualize(scoping_cube=scope)
