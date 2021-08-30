import os

filenames = os.listdir('/Users/james_hargreaves/PycharmProjects/dataplay_a2/data/obj')
print('\n'.join([f.split('.')[0] for f in sorted(filenames)]))