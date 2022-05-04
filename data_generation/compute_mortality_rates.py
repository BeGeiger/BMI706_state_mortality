import reformat_files as rf
import os



def compute_mr(pop_mort_pair):

	p_file, m_file = pop_mort_pair
	
	pop_dict = {}
	
	with open(p_file, "r") as p:
	
		p.readline()
		
		for line in p:
		
			line = line.split(sep="\t")
			line[-1] = line[-1][:-1]
			
			info, pop = line[:-1], int(line[-1:][0])
			
			info = tuple(info)
			
			pop_dict[info] = pop
	
	len_key = len(info)

	ncol_m_file = (sum(1 for _ in open(m_file)) - 1)
	rates = ["0"] * ncol_m_file
	reliable = ["F"] * ncol_m_file

	with open(m_file, "r") as m:
	
		m.readline()
		
		for i,line in enumerate(m):
			
			line = line.split(sep="\t")
			line[-1] = line[-1][:-1]
			
			info, deaths = tuple(line[:len_key]), float(line[-1])
			
			pop = pop_dict[info]
			
			if pop != 0:
			
				rates[i] = str(round(deaths / pop * 1e5, 2))

			if deaths > 9:
			
				reliable[i] = "T"

	rf.add_column_file(m_file, "Mortality Rate", len_key + 3, rates)
	rf.add_column_file(m_file, "Reliable MR?", len_key + 4, reliable)



def main():
	
	pop_state_path = "./population/state_level/"
	mort_state_path = "./mortality/state_level/"

	pop_state_files = [pop_state_path + pf for pf in ["Pop6816.tsv", "Pop6878.tsv", "Pop7998.tsv", "Pop9916.tsv"]]
	mort_state_files = [mort_state_path + mf for mf in ["Mort6816.tsv", "Mort6878.tsv", "Mort7998.tsv", "Mort9916.tsv"]]
	
	pop_mort_pairs = [(pf, mort_state_files[i]) for i,pf in enumerate(pop_state_files)]
	
	for pm_pair in pop_mort_pairs:
		
		compute_mr(pm_pair)
	
	
	pop_county_path = "./population/county_level/"
	mort_county_path = "./mortality/county_level/"
	
	pop_county_files = [pop_county_path + pf for pf in ["long_Pop6878_county.tsv", "long_Pop7988_county.tsv"]]
	mort_county_files = [mort_county_path + mf for mf in ["Mort6878_county.tsv", "Mort7988_county.tsv"]]
	
	pop_mort_pairs = [(pf, mort_county_files[i]) for i,pf in enumerate(pop_county_files)]
	
	for pm_pair in pop_mort_pairs:
		
		compute_mr(pm_pair)



if __name__ == '__main__':
    main()
