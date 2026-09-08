import torch
import numpy as np

print(f"✅ PyTorch version: {torch.__version__}")
print(f"✅ NumPy version: {np.__version__}")

# تست ساده
a = torch.tensor([1, 2, 3])
b = a.numpy()
print(f"✅ Tensor to NumPy: {b}")

# تست سریع
x = np.array([1, 2, 3])
y = torch.from_numpy(x)
print(f"✅ NumPy to Tensor: {y}")