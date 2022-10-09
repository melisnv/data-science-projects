import numpy as np

a = np.array([2,3,4,5])
b = np.array([9,8,7,6])

print(a*b)

rand = np.random.randint(10,size=9)
print(rand)
print(rand.ndim)
print(rand.shape)
print(rand.size)
print(rand.dtype)
new_shape = rand.reshape(3,3)
print(new_shape)

m = np.random.randint(10,size=(4,4))
print(m)
print(m[2,3])

# Conditional Operations

print(m[m<2])