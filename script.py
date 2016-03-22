#
# Copyright © 2016 Andrea Bianco
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public
# License along with Sipi.  If not, see <http://www.gnu.org/licenses/>.
#

import codecs
import csv
import os
import sys
import glob
import re
import itertools

totPatients = int(sys.argv[1])
walk_dir = sys.argv[2]
outFile_name = sys.argv[3]
print('walk_dir = ' + walk_dir)
# print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

regexp = ['null']
regexpN = ['null']
regexp[0] = 'FRU[01][0-9]_Nback.txt'
regexpN[0] = re.compile('.*\/FRU(.+?)_Nback.txt')
regexp.append('GLU[01][0-9]_Nback.txt')
regexpN.append(re.compile('.*\/GLU(.+?)_Nback.txt'))
regexp.append('H2O[01][0-9]_Nback.txt')
regexpN.append(re.compile('.*\/H2O(.+?)_Nback.txt'))
regexR = re.compile('.*\/(.+?)_Nback.txt')

patientList = ['null']

lastPatient = 0
patient = 1
patientFileList = [['null'] * totPatients, ['null'] * totPatients, ['null'] *
                   totPatients]

for s in range(len(regexp)):
    for filename in glob.iglob(os.path.abspath(walk_dir) + '/' + regexp[s]):
        try:
            patientN = regexpN[s].search(filename).group(1)
            patientFileList[s][int(patientN) - 1] = filename
        except AttributeError:
            print('Error file: '+filename)

print(patientFileList)

fout = open(outFile_name, 'w')
writer = csv.writer(fout, delimiter=',')
writer.writerow([' ', '0-back_corr', '0-back_err', '1-back_corr', '1-back_err',
                 '1-back_corr', '1-back_err'])

for i, j in itertools.product(range(3), range(totPatients)):
    print(i, ' ', j)
    print(patientFileList[i][j])
    if(os.path.isfile(patientFileList[i][j])):
        with codecs.open(patientFileList[i][j], encoding='utf-16') as f:
            flag = 'wait'
            procedure = False
            stimulus = False
            stimulusMix = False
            trialMix = False
            correctAns = False
            running = False
            acc = False
            resp = False
            cresp = False
            nFrame = 0
            nBunch = 0

            zero_back_corr = 0
            zero_back_err = 0
            one_back_corr = 0
            one_back_err = 0
            two_back_corr = 0
            two_back_err = 0

            for line in f:

                if 'LogFrame Start' in line:
                    flag = 'start'
                    stopRelease = True
                elif 'LogFrame End' in line:
                    flag = 'stop'

                if flag == 'start':
                    if ':' in line:
                        valueList = line.split()
                        if len(valueList) > 1:
                            value = line.split()[1]
                        else:
                            value = False
                    if 'Procedure:' in line:
                        procedure = value if value else False
                    elif 'Trial' in line:
                        trialMix = value if value else False
                    elif 'Running' in line:
                        running = value if value else False
                    elif 'Stimulus:' in line:
                        stimulus = value if value else False
                    elif 'CorrectAnswer:' in line:
                        correctAns = value if value else False
                    elif 'Stimulus.RESP:' in line:
                        resp = value if value else False
                    elif 'Stimulus.ACC:' in line:
                        acc = value if value else False
                    elif 'Stimulus.CRESP:' in line:
                        cresp = value if value else False
                    elif 'Stimulus.' in line:
                        stimulusMix = value if value else False
                    else:
                        stimulus = False
                        correctAns = False
                        resp = False
                        acc = False
                elif flag == 'stop':
                    if(stopRelease):
                        stopRelease = False
                        if(stimulus is not False):
                            if(nFrame < 14):
                                nFrame = nFrame + 1
                            else:
                                nFrame = 1
                                nBunch = nBunch + 1

                            # 0 nback
                            if ((nBunch == 0) or (nBunch == 2) or (nBunch == 4)
                               or (nBunch == 6) or (nBunch == 8)):
                                if(acc == '1'):
                                    zero_back_corr = zero_back_corr + 1
                                elif(acc == '0'):
                                    zero_back_err = zero_back_err + 1
                            # 1 nback
                            if ((nBunch == 1) or (nBunch == 7)):
                                if(acc == '1'):
                                    one_back_corr = one_back_corr + 1
                                elif(acc == '0'):
                                    one_back_err = one_back_err + 1
                            # 2 nback
                            if ((nBunch == 3) or (nBunch == 5) or
                               (nBunch == 9)):
                                if(acc == '1'):
                                    two_back_corr = two_back_corr + 1
                                elif(acc == '0'):
                                    two_back_err = two_back_err + 1

                            # print(nBunch, ' ', nFrame)
                            # print('c: ', zero_back_corr, ' ', zero_back_err)
                            # print('c: ', one_back_corr, ' ', one_back_err)
                            # print('c: ', two_back_corr, ' ', two_back_err)
                            # print(stis, ' ', correctAns, ' ', resp, ' ', acc)
            # end for
        writer.writerow([regexR.search(patientFileList[i][j]).group(1),
                        zero_back_corr, zero_back_err, one_back_corr,
                         one_back_err, two_back_corr, two_back_err])
