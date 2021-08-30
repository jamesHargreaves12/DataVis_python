import csv
from math import sqrt, atan, pi, cos, sin
import matplotlib.pyplot as plt



with open('data/xyz_fill_in/iceland.csv','r') as fp:
    sorted_lines_filled_in = sorted(fp.readlines())
    with open('data/tmp/filled_in.csv', 'w+') as outFile:
            outFile.write(''.join(sorted_lines_filled_in))

count = 0
with open('data/xyz_low_res/iceland.csv','r') as fp:
    filledInLines = set(sorted_lines_filled_in)
    sorted_lines_low_res = sorted(fp.readlines())
    with open('data/tmp/low_res.csv', 'w+') as outFile:
        outFile.write('X,Y,Z\n')
        for line in sorted_lines_low_res[:-1]:
            if line not in filledInLines:
                count += 1
                x,y,z = line.split(',')
                line = '{},{},100\n'.format(x,y)
            outFile.write(line)
print(count)
print(len(sorted_lines_low_res))