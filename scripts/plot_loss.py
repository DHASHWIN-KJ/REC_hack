import matplotlib.pyplot as plt

# Data extracted from terminal logs
epochs = list(range(1, 12))
train_loss = [0.4306, 0.3698, 0.3375, 0.3201, 0.3043, 0.2922, 0.2702, 0.2692, 0.2589, 0.2446, 0.2436]
val_loss = [0.3814, 0.3533, 0.3393, 0.3458, 0.4241, 0.3329, 0.3563, 0.3042, 0.3849, 0.3611, 0.3059]
train_acc = [0.8354, 0.8479, 0.8567, 0.8704, 0.8748, 0.8829, 0.8970, 0.8914, 0.8961, 0.9056, 0.9009]
val_acc = [0.8452, 0.8595, 0.8512, 0.8524, 0.8726, 0.8619, 0.8548, 0.8833, 0.8298, 0.8774, 0.8726]

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('Model Training Metrics (11 Epochs)', fontsize=16)

# Plot Loss
ax1.plot(epochs, train_loss, 'b-o', label='Train Loss', linewidth=2)
ax1.plot(epochs, val_loss, 'r-s', label='Validation Loss', linewidth=2)
ax1.set_title('Loss Curve')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss (Binary Cross Entropy)')
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend()
ax1.set_xticks(epochs)

# Plot Accuracy
ax2.plot(epochs, train_acc, 'b-o', label='Train Accuracy', linewidth=2)
ax2.plot(epochs, val_acc, 'r-s', label='Validation Accuracy', linewidth=2)
ax2.set_title('Accuracy Curve')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy')
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend()
ax2.set_xticks(epochs)

plt.tight_layout()

# Save the plot
output_path = 'docs/training_curves.png'
plt.savefig(output_path, dpi=300)
print(f"Graph saved successfully to {output_path}")
