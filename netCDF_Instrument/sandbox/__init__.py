# '''import numpy as np
# import matplotlib.pyplot as plt
# 
# a = [1,2,3,4,5]
# b = [3,1,5,2,7]
# 
# d,e,c = np.polyfit(a,b,deg=2)
# 
# plt.scatter(a,b)
# 
# 
# yhat = [c + e*x + d*x**2 for x in a]
# 
# plt.plot(a,yhat)
# 
# plt.show()
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# 
# import numpy as np
# # 
# # fig = plt.figure()
# # ax = fig.add_subplot(111, projection='3d')
# # ax.plot([1,2,3],[1,2,3],[1,2,3])
# 
# a = np.array([1,2,1,4])
# 
# b = np.where(a<2)
# print(len(b[0]))
# print(a[b])
# 
# # for x in range(0,100):
# #     print(x,np.sinh(x*10),x*10)

# plt.show()

# import numpy as np
# 
# print(np.fft.rfftfreq(100, .25))