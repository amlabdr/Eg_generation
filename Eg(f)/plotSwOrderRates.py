import matplotlib.pyplot as plt
import numpy as np

final_distance = 200
distances = list(range(1, final_distance + 1, 10))

# Load rates from the file

rates1e5L2R = np.loadtxt('Eg(f)/rates/L2R/2Routers/1e5.txt')
rates1e5R2L = np.loadtxt('Eg(f)/rates/R2L/2Routers/1e5.txt')



#

# Plotting the moving average curve
fig, ax = plt.subplots()
ax.set_xscale('linear')
ax.set_yscale('log')
ax.set_ylim([10 ** (0), 10 ** 4])
#ax.set_yticks([10**-4,10**-2,10**0, 10**2, 10**4])




#ax.plot(distances, rates100ms, label='rates100ms')
#ax.plot(distances, rates900ms, label='rates900ms')
#ax.plot(distances, rates1s, label='rates1s')
#ax.plot(distances, rates10s, label='rates10s')
ax.plot(distances, rates1e5L2R, linestyle='--',label='Swapping strategy (i)')
ax.plot(distances, rates1e5R2L, linestyle='--',label='Swapping strategy (ii)')

#ax.plot(distances, rates2e6, label='rates 2e6')
#ax.plot(distances, ratesinf, label='rates inf')
# Add labels and titles
ax.set_xlabel('Distance in Km')
ax.set_ylabel('Rate (entanglement per second)')
ax.set_title('Rates vs. Distance')
ax.legend()

# Show the plot
plt.show()
