import random, math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def show_conf(L, sigma, title, fname):
    fig, ax = plt.subplots()
    for [x, y] in L:
        for ix in range(-1, 2):
            for iy in range(-1, 2):
                cir = patches.Circle((x + ix, y + iy), radius=sigma,  fc='r')
                ax.add_patch(cir)
    plt.axis('scaled')
    ax.set_xlabel('axis x')
    ax.set_ylabel('axis y')
    ax.set_title(title)
    #ax.set_axis_on plt.axis([0.0, 1.0, 0.0, 1.0])
    plt.show()

L = []
N = 8 ** 2

for i in range(N):
    posx = float(random.uniform(0, 1))
    posy = float(random.uniform(0, 1))
    L.append([posx, posy])

print(L)

N = 8 ** 2
eta = 0.3
sigma = math.sqrt(eta / (N * math.pi))
Q = 20
ltilde = 5*sigma

N_sqrt = int(math.sqrt(N) + 0.5)


titulo1 = '$N=$'+str(N)+', $\eta =$'+str(eta)
nome1 = 'inicial'+'_N_'+str(N) + '_eta_'+str(eta) + '.png'
show_conf(L, sigma, titulo1, nome1)