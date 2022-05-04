import reformat_files as rf
import os


def generate_pop_files_state(state_files):

	rf.delete_sign_files(state_files, "\"")
	rf.delete_comments_files(state_files, "---")
	rf.delete_rows_files(state_files, ["Notes"], ["Total"])
	
	rf.delete_columns_files(
		state_files, 
		["Notes", "State Code", "Year Code", "Race Code", "Gender Code", "Age Group Code", "Deaths", "Crude Rate"]
	)
	
	decode_info = {
		"Race": (["Race"], [rf.read_dict("1989-2016_race.tsv")]),
		"Age Group": (["Age Group"], [rf.read_dict("age_groups.tsv")])
	}
	rf.decode_col_files(state_files, decode_info)
	
	state_encode_dict = rf.read_dict("state_code.tsv")
	encode_info = {
		"State": (["State Code"], [state_encode_dict])
	}
	rf.decode_col_files(state_files, encode_info, delete_old=False)
	
	state_tables = "./population/state_level/"
	os.mkdir(state_tables)
	
	rf.cp_files([state_files[0]], [state_tables + "Pop6878.tsv"])
	rf.merge_files(state_files[1:3], state_tables + "Pop7998.tsv")
	rf.merge_files(state_files[3:5], state_tables + "Pop9916.tsv")
	
	rf.delete_rows_files(state_files, 3*["Race"], ["Other", "American Indian or Alaska Native", "Asian or Pacific Islander"])
	rf.merge_files(state_files, state_tables + "Pop6816.tsv")
	
	for pf in state_files:
		
		os.remove(pf)



def generate_pop_files_county(county_files):

	cf_names = [cf.split("/")[-1] for cf in county_files]
	
	rf.split_rows_files(county_files, [5,4,1] + 13*[8] + [25])
	
	pop_header = [
		"FIPS", "Year", "Race and Gender", "< 1 year", 
		"1-4 years", "5-9 years", "10-14 years", "15-19 years", 
		"20-24 years", "25-34 years", "35-44 years", "45-54 years", 
		"55-64 years", "65-74 years", "75-84 years", "85+ years",
		"County Name", "Record Type"
	]
	rf.add_header_files(county_files, pop_header)
	
	rf.delete_columns_files(county_files, ["County Name", "Record Type"])
	
	state_dict = rf.combine_dicts(rf.read_dict("FIPS_state.tsv"), rf.read_dict("states_postal.tsv"))
	county_dict = rf.read_dict("FIPS_county.tsv")
	decode_info = {
		"FIPS": (["State", "County"], [state_dict, county_dict]),
		"Race and Gender": (["Race", "Gender"], [rf.read_dict("1968-1998_race.tsv"), rf.read_dict("1968-1998_sex.tsv")])
		
	}
	rf.decode_col_files(county_files, decode_info)
	
	rf.delete_rows_files(county_files, ["State"], ["NA"])
	
	rf.delete_sign_files(county_files, " County")
	
	state_encode_dict = rf.read_dict("state_code.tsv")
	encode_info = {
		"State": (["State Code"], [state_encode_dict])
	}
	rf.decode_col_files(county_files, encode_info, delete_old=False)
	
	county_tables = "./population/county_level/"
	os.mkdir(county_tables)
	
	rf.cp_files(county_files, [county_tables + "wide_" + cf for cf in cf_names])
	
	rf.pivot_longer_files(
		county_files,
		["< 1 year", "1-4 years", "5-9 years", "10-14 years", "15-19 years", "20-24 years", "25-34 years",
		 "35-44 years", "45-54 years", "55-64 years", "65-74 years", "75-84 years", "85+ years"],
		 ["Age Group", "Population"]
	)
	
	rf.cp_files(county_files, [county_tables + "long_" + cf[:-4] + ".tsv" for cf in cf_names])
	
	for pf in county_files:
		
		os.remove(pf)



def main():
	
	pop_dir = "./population/original_files/"
	org_pop_files = [pop_dir + pf for pf in os.listdir(pop_dir)]
	pop_files = ["./population/" + pf for pf in os.listdir(pop_dir)]
	rf.cp_files(org_pop_files, pop_files)
	
	
	pop_files_state = ["./population/Pop6878.txt", "./population/Pop7988.txt", "./population/Pop8998.txt", "./population/Pop9908.txt", "./population/Pop0916.txt"]
	generate_pop_files_state(pop_files_state)
	
	pop_files_county = ["./population/Pop6878_county.txt", "./population/Pop7988_county.txt"]
	generate_pop_files_county(pop_files_county)	



if __name__ == '__main__':
    main()
