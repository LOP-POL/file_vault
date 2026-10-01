import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex":False,
})

y_data = [i for i in range(10)]
x_data = [i for i in range(10)]
plt.plot(x_data, y_data)
plt.xlabel(r"$\theta$")
plt.ylabel(r"$\sigma_{11}$")
for xi, yi in zip(x_data,y_data):
    plt.text(xi, yi, str(yi), ha='center', va='bottom')
plt.savefig("test_latex_plot.png", dpi=300)
