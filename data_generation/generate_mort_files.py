import reformat_files as rf
import os



def merge_splitted_mort_files(mort_files):

	for tup in mort_files:
	
		rf.merge_files(list(tup), "./mortality/" + tup[0].split(sep="/")[-1][:6] + ".txt")



def generate_mort_files_state(state_files, icd, smf=None):

	if icd == 8:
	
		icd_groups = "ICD 69 Groups"
		icd_groups_code = "ICD 69 Groups Code"
		icd_dict_aux = rf.read_dict("ICD8_aux.tsv")
		icd_dict_groups = rf.read_dict("ICD8_recode.tsv")
		file_years = [str(i) for i in range(68,79)]
		years = ["19" + fy for fy in file_years]
		
	elif icd == 9:
	
		icd_groups = "ICD 72 Groups"
		icd_groups_code = "ICD 72 Groups Code"
		icd_dict_aux = rf.read_dict("ICD9_aux.tsv")
		icd_dict_groups = rf.read_dict("ICD9_recode.tsv")
		file_years = [str(i) for i in range(79,99)]
		years = ["19" + fy for fy in file_years]
		
	else:
	
		icd_groups = "ICD 113 Groups"
		icd_groups_code = "ICD 113 Groups Code"
		icd_dict_aux = rf.read_dict("ICD10_aux.tsv")
		icd_dict_groups = rf.read_dict("ICD10_recode.tsv")
		file_years = ["99"] + ["0" + str(i) for i in range(0,10)] + [str(i) for i in range(10,17)]
		years = ["1999"] + ["20" + fy for fy in file_years[1:]]
		
	icd_dict = rf.combine_dicts(icd_dict_aux, icd_dict_groups)
	
	
	rf.delete_sign_files(state_files, "\"")
	rf.delete_comments_files(state_files, "---")
	rf.delete_rows_files(state_files, ["Notes", "Age Group", "Deaths"], ["Total", "Not Stated", "Missing"])
	
	rf.delete_columns_files(
		state_files, 
		["Notes", "State Code", "Race Code", "Gender Code", "Age Group Code", icd_groups, "Population", "Crude Rate"]
	)
	
	decode_info = {
		"Race": (["Race"], [rf.read_dict("1989-2016_race.tsv")]),
		"Age Group": (["Age Group"], [rf.read_dict("age_groups.tsv")]),
		icd_groups_code: (["ICD Group"], [icd_dict])
	}
	rf.decode_col_files(state_files, decode_info)
	
	if smf: 
	
		merge_splitted_mort_files(smf)
		halves = [mf for sublist in smf for mf in sublist]
		
		for h in halves:
			
			os.remove(h)
		
		state_files = ["./mortality/Mort" + fy + ".txt" for fy in file_years]
		
	if icd == 9:
	
		rf.delete_rows_files(state_files, 4*["Deaths"], [1,2,3,4])

	state_encode_dict = rf.read_dict("state_code.tsv")
	encode_info = {
		"State": (["State Code"], [state_encode_dict])
	}
	rf.decode_col_files(state_files, encode_info, delete_old=False)
	
	rf.add_column_files(state_files, ["Year"], [2], [int(y) for y in years])
	rf.merge_files(state_files, "./mortality/state_level/" + "Mort" + str(file_years[0]) + str(file_years[-1]) + ".tsv")
	
	for mf in state_files:
		
		os.remove(mf)



def generate_6816_mort_file(directory):

	common_icd = rf.read_list("./dics_and_lists/ICD_all.tsv")

	fnames = [directory + f for f in os.listdir(directory)]
	fnames_new = [f + "_new" for f in fnames]
	
	rf.cp_files(fnames, fnames_new)
	
	rf.filter_files(fnames_new, ["Race", "ICD Group"], [["White", "Black"], common_icd])
	rf.delete_rows_files(fnames_new, 4*["Deaths"], [1,2,3,4])
	
	rf.merge_files(fnames_new, directory + "Mort6816.tsv")
	
	for fn in fnames_new:
	
		os.remove(fn)



def generate_mort_file_county(county_file, icd):

	if icd == 8:
	
		icd_dict_groups = rf.read_dict("ICD8_recode.tsv")
	
	else:
	
		icd_dict_groups = rf.read_dict("ICD9_recode.tsv")

	cf_name = county_file.split("/")[-1]
	
	rf.split_rows_file(county_file, [5,4,1,2,4,3])
	
	mort_header = [
		"FIPS", "Year", "Race and Gender", "Age Group Code", "ICD code", "ICD Group Encoded", "Deaths"
	]
	rf.add_header_file(county_file, mort_header)
	
	rf.delete_columns_inplace(county_file, ["ICD code"])
	rf.delete_rows_file(county_file, ["Age Group Code"], ["99"])
	
	rf.aggregate_duplicates_file(county_file)
	rf.aggregate_ages_file(county_file, "Age Group Code", ["01", "02", "03", "04"], "< 1 year")
	
	state_dict = rf.combine_dicts(rf.read_dict("FIPS_state.tsv"), rf.read_dict("states_postal.tsv"))
	county_dict = rf.read_dict("FIPS_county.tsv")
	decode_info = {
		"FIPS": (["State", "County"], [state_dict, county_dict]),
		"Race and Gender": (["Race", "Gender"], [rf.read_dict("1968-1998_race.tsv"), rf.read_dict("1968-1998_sex.tsv")]),
		"Age Group Code": (["Age Group"], [rf.read_dict("age_groups.tsv")]),
		"ICD Group Encoded": (["ICD Group"], [icd_dict_groups])
	}
	rf.decode_col_inplace(county_file, decode_info)
	rf.delete_sign_file(county_file, " County")
	
	state_encode_dict = rf.read_dict("state_code.tsv")
	encode_info = {
		"State": (["State Code"], [state_encode_dict])
	}
	rf.decode_col_inplace(county_file, encode_info, delete_old=False)
	
	rf.cp_files([county_file], ["./mortality/county_level/" + cf_name[:-4] + ".tsv"])
	
	os.remove(county_file)



def main():
	
	mort_dir = "./mortality/original_files/"

	mort_files_icd8 = ["./mortality/" + mf for mf in ["Mort" + str(i) + ".txt" for i in range(68,79)]]
	mort_files_icd9 = ["./mortality/" + mf for mf in ["Mort" + str(i) + ".txt" for i in range(79,99)]]
	
	smf1 = [("Mort99_1.txt", "Mort99_2.txt")]
	smf2 = [("Mort0" + i + "_1.txt", "Mort0" + i + "_2.txt") for i in [str(i) for i in range(0,10)]]
	smf3 = [("Mort" + i + "_1.txt", "Mort" + i + "_2.txt") for i in [str(i) for i in range(10,17)]]
	smf = smf1 + smf2 + smf3
	smf = [("./mortality/" + tup[0], "./mortality/" + tup[1]) for tup in smf]
	
	mort_files_icd10 = [mf for sublist in smf for mf in sublist]
	
	state_files = mort_files_icd8 + mort_files_icd9 + mort_files_icd10
	county_files = ["./mortality/Mort6878_county.txt", "./mortality/Mort7988_county.txt"]
	mort_files = state_files + county_files
	org_mort_files = [mort_dir + mf for mf in [m.split(sep="/")[-1] for m in mort_files]]
	
	rf.cp_files(org_mort_files, mort_files)
	
	os.mkdir("./mortality/state_level/")
	generate_mort_files_state(mort_files_icd8, 8)
	generate_mort_files_state(mort_files_icd9, 9)
	generate_mort_files_state(mort_files_icd10, 10, smf=smf)
	
	generate_6816_mort_file("./mortality/state_level/")
	
	os.mkdir("./mortality/county_level/")
	generate_mort_file_county(county_files[0], 8)
	generate_mort_file_county(county_files[1], 9)



if __name__ == '__main__':
    main()
