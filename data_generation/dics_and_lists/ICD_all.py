def get_ICDgroups(fname):

	ICDg = set()

	with open(fname, "r") as f:
	
		for line in f:
		
			line = line.split(sep="\t")
			ICDg.add(line[-1][:-1])
			
	return ICDg


icd8g = get_ICDgroups("ICD8_recode.tsv")
icd9g = get_ICDgroups("ICD9_recode.tsv")
icd10g = get_ICDgroups("ICD10_recode.tsv")

common = icd8g.intersection(icd9g, icd10g) - {"All other diseases", "All other forms of heart disease"}

with open("ICD_all.tsv", "w") as f:

	for icd in common:
	
		f.write(icd + "\n")
