import matplotlib.pyplot as plt
import numpy as np

# Generate example ECG signal
t = np.linspace(0, 10, 1000)  # Time vector from 0 to 10 seconds
ecg_signal = np.sin(2 * np.pi * 1 * t) + np.sin(2 * np.pi * 1.5 * t)  # Example ECG signal

# Plot ECG signal with grid lines
plt.plot(t, ecg_signal)
plt.xlabel('Time (s)')
plt.ylabel('Voltage (mV)')

# Set custom ticks for both x and y axes
x_ticks = np.arange(0, 10, step=100)  # Adjust step value for more grid lines
y_ticks = np.arange(-2, 3, step=0.1)   # Adjust step value for more grid lines

# Add vertical grid lines
#for x in x_ticks:
    #plt.axvline(x, color='red', linestyle='--', linewidth=0.5)

# Add horizontal grid lines
for y in y_ticks:
    plt.axhline(y, color='red', linestyle='--', linewidth=0.5)

plt.grid(True)  # Add grid lines
plt.show()
