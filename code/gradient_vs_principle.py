import numpy as np
import matplotlib.pyplot as plt

# Set headless backend for Matplotlib
plt.switch_backend('Agg')

def generate_comparison_plot():
    # 1. Create a 2D domain simulating a phase-field crack tip
    nx, ny = 200, 200
    x = np.linspace(-2, 2, nx)
    y = np.linspace(-2, 2, ny)
    X, Y = np.meshgrid(x, y)

    # Characteristic crack length scale l
    l = 0.4

    # Pre-crack along negative x-axis (y=0, x <= 0) and crack tip at (0,0)
    # Analytical diffuse crack profile phi_c(x,y)
    dist_crack = np.where(X <= 0, np.abs(Y), np.sqrt(X**2 + Y**2))
    phi_c = np.exp(-dist_crack / l)

    # Compute spatial gradient of phase-field grad(phi_c)
    dphi_dy, dphi_dx = np.gradient(phi_c, y - y, x - x)
    grad_mag = np.sqrt(dphi_dx**2 + dphi_dy**2)

    # Gradient Method: r_grad = grad(phi_c) / |grad(phi_c)|
    eps = 1e-4
    r_grad_x = np.where(grad_mag > eps, dphi_dx / grad_mag, 0.0)
    r_grad_y = np.where(grad_mag > eps, dphi_dy / grad_mag, 0.0)

    # Principal Strain Method: r_principal = n1 (Mode-I tension along y-axis -> n1 =)
    r_principal_x = np.zeros_like(X)
    r_principal_y = np.ones_like(Y)

    # Subsample grid for vector quiver display
    sub = 10
    X_sub = X[::sub, ::sub]
    Y_sub = Y[::sub, ::sub]

    u_grad = r_grad_x[::sub, ::sub]
    v_grad = r_grad_y[::sub, ::sub]

    u_princ = r_principal_x[::sub, ::sub]
    v_princ = r_principal_y[::sub, ::sub]

    # Create 2-panel figure
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.5), sharex=True, sharey=True)
    fig.suptitle('Crack Orientation Vector Field Comparison:\nGradient Method vs. Principal Strain Method',
                 fontsize=14, fontweight='bold', y=0.99)

    # Panel 1: Gradient Method
    ax1 = axes
    im1 = ax1.imshow(phi_c, extent=[-2, 2, -2, 2], origin='lower', cmap='viridis', aspect='equal')
    q1 = ax1.quiver(X_sub, Y_sub, u_grad, v_grad, color='red', scale=22, width=0.005, headwidth=3.5)
    ax1.set_title(r'Gradient Method:  $\mathbf{r} = \nabla\phi_c / |\nabla\phi_c|$' + '\n' + r'(Fails in broken core $\phi_c=1$ & at tip)',
                  fontsize=10.5, fontweight='semibold', color='darkred', pad=12)
    ax1.set_xlabel(r'$x / l$', fontsize=11)
    ax1.set_ylabel(r'$y / l$', fontsize=11)
    ax1.grid(True, linestyle=':', alpha=0.4, color='white')

    # Highlight Failure Annotations in Panel 1
    ax1.annotate(r'UNDEFINED / NULL' + '\n' + r'($\nabla \phi_c = \mathbf{0}$)', xy=(-1.0, 0.0), xytext=(-1.8, 0.8),
                 arrowprops=dict(facecolor='yellow', shrink=0.05, width=1.5, headwidth=6),
                 fontsize=9, fontweight='bold', color='yellow', bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="yellow", lw=1.5))

    ax1.annotate(r'MISALIGNED TIP' + '\n' + r'(Radial Spread)', xy=(0.0, 0.0), xytext=(0.3, -1.2),
                 arrowprops=dict(facecolor='orange', shrink=0.05, width=1.5, headwidth=6),
                 fontsize=9, fontweight='bold', color='orange', bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="orange", lw=1.5))

    # Panel 2: Principal Strain Method
    ax2 = axes
    im2 = ax2.imshow(phi_c, extent=[-2, 2, -2, 2], origin='lower', cmap='viridis', aspect='equal')
    q2 = ax2.quiver(X_sub, Y_sub, u_princ, v_princ, color='cyan', scale=22, width=0.005, headwidth=3.5)
    ax2.set_title(r'Principal Strain Method:  $\mathbf{r} \parallel \mathbf{n}_1$' + '\n' + r'(Well-defined & continuous across domain)',
                  fontsize=10.5, fontweight='semibold', color='darkgreen', pad=12)
    ax2.set_xlabel(r'$x / l$', fontsize=11)
    ax2.grid(True, linestyle=':', alpha=0.4, color='white')

    # Highlight Advantage Annotation in Panel 2
    ax2.annotate(r'UNIFORM & WELL-DEFINED' + '\n' + r'(Aligns with $\mathbf{n}_1$ everywhere)', xy=(0.0, 0.0), xytext=(-1.8, 1.0),
                 arrowprops=dict(facecolor='cyan', shrink=0.05, width=1.5, headwidth=6),
                 fontsize=9, fontweight='bold', color='cyan', bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="cyan", lw=1.5))

    # Colorbar
    fig.subplots_adjust(right=0.88, top=0.86)
    cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.68])
    cbar = fig.colorbar(im1, cax=cbar_ax)
    cbar.set_label(r'Crack Phase-Field $\phi_c$', fontsize=11, fontweight='semibold')

    # Save figure
    output_path = 'gradient_vs_principal_strain.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Comparison plot saved successfully as '{output_path}'.")

if __name__ == '__main__':
    generate_comparison_plot()
