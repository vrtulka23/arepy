import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('output.dat',skiprows=1).T
labels = ['step','time','Spitzer','Hosokawa-Inutsuka','Raga-I','Raga-II','StarBench']

plt.figure(figsize=(8,4))
for i in range(2,7):
    plt.plot(data[1],data[i],label=labels[i])
plt.xlabel('t (Myr)')
plt.ylabel('R (pc)')
plt.legend()

plt.savefig('dtype.png')
plt.show()
