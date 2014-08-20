import sys
import matplotlib.pyplot as plt
files = sys.argv[1:]
d = dict()
for afile in files:
    with open(afile) as f:
        for line in f:
            tokens = line.split()
            for token in tokens:
                if token in d:
                    d[token] += 1
                else:
                     d[token] = 1


clean = dict()
for key in d:
    if d[key] > 4:
        clean[key] = d[key]

plt.bar(range(len(clean)), list(clean.values()), align='center')
plt.xticks(range(len(clean)), list(clean.keys()), rotation='vertical')

plt.show()
