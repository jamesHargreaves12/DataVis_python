import re


decimalRe = re.compile(r"[-0-9]+\.\d+")
def roundAllNumbersTo5dp(s):
    return re.sub(decimalRe, lambda x: '{:.5f}'.format(float(x.group())), s)

# WARNING THIS WILL PRODUCE INVALID POLYGONS SO DO NOT USE

with open('./data/tmp/test.csv', 'r') as fp:
    s = fp.read()
    out = roundAllNumbersTo5dp(s)
    with open('./data/tmp/testRounded.csv', 'w+') as fpOut:
        fpOut.write(out)