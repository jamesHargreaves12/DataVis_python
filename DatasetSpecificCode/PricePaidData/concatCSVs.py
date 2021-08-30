import os

from helpers import BASE_FILEPATH

BASE = '/Users/james_hargreaves/PycharmProjects/dataplay_a2/data/raw/pricePaidData'

entityToInputFileNames = {
    'price_paid_18-20': ['pp-2020.csv',
                         'pp-2019.csv',
                         'pp-2018.csv'],
    'price_paid_15-17': ['pp-2015-part1.csv',
                         'pp-2015-part2.csv',
                         'pp-2016-part1.csv',
                         'pp-2016-part2.csv',
                         'pp-2017-part1.csv',
                         'pp-2017-part2.csv'],
    'price_paid_12-14': ['pp-2014-part1.csv',
                         'pp-2014-part2.csv',
                         'pp-2013-part1.csv',
                         'pp-2013-part2.csv',
                         'pp-2012-part1.csv',
                         'pp-2012-part2.csv'],
    'price_paid_09-11': ['pp-2011-part1.csv',
                         'pp-2011-part2.csv',
                         'pp-2010-part1.csv',
                         'pp-2010-part2.csv',
                         'pp-2009-part1.csv',
                         'pp-2009-part2.csv'],
    'price_paid_06-08': ['pp-2008-part1.csv',
                         'pp-2008-part2.csv',
                         'pp-2007-part1.csv',
                         'pp-2007-part2.csv',
                         'pp-2006-part1.csv',
                         'pp-2006-part2.csv'],
    'price_paid_03-05': ['pp-2005-part1.csv',
                         'pp-2005-part2.csv',
                         'pp-2004-part1.csv',
                         'pp-2004-part2.csv',
                         'pp-2003-part1.csv',
                         'pp-2003-part2.csv'],
    'price_paid_00-02': ['pp-2002-part1.csv',
                         'pp-2002-part2.csv',
                         'pp-2001-part1.csv',
                         'pp-2001-part2.csv',
                         'pp-2000-part1.csv',
                         'pp-2000-part2.csv'],
    'price_paid_97-99': ['pp-1999-part1.csv',
                         'pp-1999-part2.csv',
                         'pp-1998-part1.csv',
                         'pp-1998-part2.csv',
                         'pp-1997-part1.csv',
                         'pp-1997-part2.csv'],
}

for entityName in entityToInputFileNames.keys():
    with open(os.path.join(BASE_FILEPATH, 'data/postcode', entityName + '.csv'), 'w+') as outFp:
        for filename in entityToInputFileNames[entityName]:
            with open(os.path.join(BASE, filename), 'r') as inFp:
                outFp.write(inFp.read().strip('\n'))
            outFp.write('\n')
