"""
Reformat the original FIPS.csv file

Afterwards, I manually added the entries as there were some FIPS changes in the past
# 12	025	Miami-Dade County	FL
# 30	113	Yellowstone Park County	MT
# 02	900	all areas	AK
# 51	560	Clifton Forge city	VA
# 51	780	South Boston city	VA
# 13	999	Unknown County	GA
# 00	000	USA	NA
"""

with open("FIPS.csv", "r") as old, open("myFIPS.txt", "w") as new:
    
    for i,line in enumerate(old):
        
        if i==0: continue
        
        line = line.split(sep=",")
        line = [line[0][:-3].zfill(2), line[0][-3:], line[1], line[2]]
        new_line = '\t'.join(line)
        new.write(new_line)
