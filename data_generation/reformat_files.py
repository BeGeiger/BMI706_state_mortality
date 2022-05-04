########################################################################
# BMI706: Data Visualization Project Mortality Data
# April 2022

# Author: Benedikt Geiger

# This module can be used to reformat files line by line in various ways
########################################################################

import in_place
import os
import shutil



def add_column_file(fname, cname, cpos, cvalues):

	cvalues = [str(cv) for cv in cvalues]

	if len(cvalues) == 1:
	
		cvalues *= sum(1 for _ in open(fname)) - 1

	with in_place.InPlace(fname) as f:
	
		for i,line in enumerate(f):

			line = line.split(sep="\t")
			line[-1] = line[-1][:-1]
			
			if i==0:
			
				new_line = line[:cpos] + [cname] + line[cpos:]
			
			else:
			
				new_line = line[:cpos] + [cvalues[i-1]] + line[cpos:]
			
			f.write("\t".join(new_line) + "\n")



def add_column_files(fnames, cnames, cposs, cvaluess):

	if len(cnames) == 1:
	
		cnames *= len(fnames)

	if len(cposs) == 1:
	
		cposs *= len(fnames)

	for i, f in enumerate(fnames):
	
		add_column_file(f, cnames[i], cposs[i], [cvaluess[i]])



def add_header_file(fname, header):

	with open(fname, "r") as old, open(fname + "_new", "w") as new:

		new.write("\t".join(header) + "\n")
		
		for i,line in enumerate(old):
		
			if i==0:
				line = line.split(sep="\t")
				assert len(header) == len(line), f"The provided header does not fit the number of columns in {fname}."
				line = "\t".join(line)
				
			new.write(line)

	os.rename(fname + "_new", fname)



def add_header_files(fnames, header):

	for f in fnames:
		
		add_header_file(f, header)



def aggregate_ages_file(fname, col, to_agg, agg_name):

	aggregate = {}

	with open(fname, "r") as old, open(fname + "_new", "w") as new:
	
		header = old.readline()
		header = header.split(sep="\t")
		header[-1] = header[-1][:-1]
		
		pos = first_occurance(header, col)
		
		new.write("\t".join(header) + "\n")
		
		for line in old:
		
			line = line.split(sep="\t")
			line[-1] = line[-1][:-1]
			info, deaths = line[:-1], int(line[-1:][0])
			
			key_info = [entry for i,entry in enumerate(info) if i != pos]
			
			if info[pos] in to_agg:
				
				key = key_info[:pos] + [agg_name] + key_info[pos:]
			
			else:
			
				key = info
			
			key = tuple(key)
			
			if key not in aggregate:
			
				aggregate[key] = deaths
			
			else:
			
				aggregate[key] += deaths
		
		for key, value in aggregate.items():
		
			new_line = "\t".join(list(key) + [str(value)]) + "\n"
			new.write(new_line)
	
	os.rename(fname + "_new", fname)



def aggregate_duplicates_file(fname):

	aggregate = {}

	with open(fname, "r") as old, open(fname + "_new", "w") as new:
	
		header = old.readline()
		header = header.split(sep="\t")
		header[-1] = header[-1][:-1]
		
		new.write("\t".join(header) + "\n")
		
		for line in old:
		
			line = line.split(sep="\t")
			line[-1] = line[-1][:-1]
			info, deaths = line[:-1], int(line[-1:][0])
			
			key = tuple(info)
			
			if key not in aggregate:
			
				aggregate[key] = deaths
			
			else:
			
				aggregate[key] += deaths
		
		for key, value in aggregate.items():
		
			new_line = "\t".join(list(key) + [str(value)]) + "\n"
			new.write(new_line)
	
	os.rename(fname + "_new", fname)



def cp_files(old_paths, new_paths):

	assert len(old_paths) == len(new_paths), "You need to provide exaclty one new path for every file you want to copy."
	
	for i, op in enumerate(old_paths):
	
		shutil.copy2(op, new_paths[i])



def combine_dicts(dict1, dict2):

	keys = list(dict1.keys())
	values = [dict2[dict1[k]] for k in keys]
	
	return dict(zip(keys, values))



def cumsums(my_list):
	
	csums = len(my_list) * [0]
	
	for i, entry in enumerate(my_list):
	
		if i==0: 
			csums[0] = entry
		else:
			csums[i] = csums[i-1] + entry

	return csums



def decode_col_inplace(fname, decode_info, delete_old=True):
	"""
	decode_info is dictionary of the form {old_name: (new_names, dics)}, were new_names is a list of names
	and dics is a list of dictionaries
	"""
	
	with in_place.InPlace(fname) as f:
	
		header = f.readline()
		header = header.split(sep="\t")
		header[-1] = header[-1][:-1]
		
		if delete_old:
			new_header = [decode_info[col][0] if col in decode_info else [col] for col in header]
		else:
			new_header = [[col] + decode_info[col][0] if col in decode_info else [col] for col in header]

		new_header = [col for sublist in new_header for col in sublist]
		new_header[-1] += "\n"
		
		f.write("\t".join(new_header))
		
		for line in f:
		
			line = line.split(sep="\t")
			line[-1] = line[-1][:-1]
			
			if delete_old:
				new_line = [
					[dic[entry] for dic in decode_info[header[i]][1]] 
					if header[i] in decode_info else [entry]
					for i,entry in enumerate(line)
				]
			else:
				new_line = [
					[entry] + [dic[entry] for dic in decode_info[header[i]][1]] 
					if header[i] in decode_info else [entry]
					for i,entry in enumerate(line)
				]
			
			new_line = [entry for sublist in new_line for entry in sublist]
			new_line[-1] += "\n"
			
			f.write("\t".join(new_line))



def decode_col_newf(fname, decode_info, new_fname, delete_old=True):
	"""
	decode_info is dictionary of the form {old_name: (new_names, dics)}, were new_names is a list of names
	and dics is a list of dictionaries
	"""

	assert fname != new_fname, "The new file must have a different name than the original one."
	
	with open(fname, "r") as old, open(new_fname, "w") as new:
	
		header = old.readline()
		header = header.split(sep="\t")
		header[-1] = header[-1][:-1]
		
		if delete_old:
			new_header = [decode_info[col][0] if col in decode_info else [col] for col in header]
		else:
			new_header = [[col] + decode_info[col][0] if col in decode_info else [col] for col in header]

		new_header = [col for sublist in new_header for col in sublist]
		new_header[-1] += "\n"
		
		new.write("\t".join(new_header))
		
		for line in old:
		
			line = line.split(sep="\t")
			line[-1] = line[-1][:-1]
			
			if delete_old:
				new_line = [
					[dic[entry] for dic in decode_info[header[i]][1]] 
					if header[i] in decode_info else [entry]
					for i,entry in enumerate(line)
				]
			else:
				new_line = [
					[entry] + [dic[entry] for dic in decode_info[header[i]][1]] 
					if header[i] in decode_info else [entry]
					for i,entry in enumerate(line)
				]
			
			new_line = [entry for sublist in new_line for entry in sublist]
			new_line[-1] += "\n"
			
			new.write("\t".join(new_line))




def decode_col_files(files, decode_info, new_fnames=None, delete_old=True, inplace=True):

	if inplace:
	
		for f in files:
		
			decode_col_inplace(f, decode_info, delete_old)
	
	else:

		assert (new_fnames != None) & (len(files) == len(new_fnames)), "You must provide new file name for every file if you don't want to delete the columns in-place."
		
		for i,f in enumerate(files):
		
			decode_col_newf(f, decode_info, new_fnames[i], delete_old)



def delete_columns_inplace(fname, to_delete):

	with in_place.InPlace(fname) as f:
		
		header = f.readline()
		header = header.split(sep="\t")
		
		indices_to_del = [first_occurance(header, to_del) for to_del in to_delete]
		
		assert -1 not in indices_to_del, f"Some columns you want to delete in {fname} were not found in the header."
		
		add_enter = header[-1][:-1] in to_delete
				
		new_header = [cname for i,cname in enumerate(header) if i not in indices_to_del]
		
		if add_enter: new_header[-1] += "\n"
		
		f.write("\t".join(new_header))
		
		for line in f:
			
			line = line.split(sep="\t")
			new_line = [entry for i,entry in enumerate(line) if i not in indices_to_del]
			
			if add_enter: new_line[-1] += "\n"
			
			f.write("\t".join(new_line))
			


def delete_columns_newf(fname, to_delete, new_fname):

	assert fname != new_fname, "The new file must have a different name than the original one."

	with open(fname, "r") as old, open(new_fname, "w") as new:
		
		header = old.readline()
		header = header.split(sep="\t")
		
		indices_to_del = [first_occurance(header, to_del) for to_del in to_delete]
		
		assert -1 not in indices_to_del, f"Some columns you want to delete in {fname} were not found in the header."
		
		add_enter = header[-1][:-1] in to_delete
				
		new_header = [cname for i,cname in enumerate(header) if i not in indices_to_del]
		
		if add_enter: new_header[-1] += "\n"
		
		new.write("\t".join(new_header))
		
		for line in old:
			
			line = line.split(sep="\t")
			new_line = [entry for i,entry in enumerate(line) if i not in indices_to_del]
			
			if add_enter: new_line[-1] += "\n"
			
			new.write("\t".join(new_line))
		


def delete_columns_files(files, to_delete, new_fnames=None, inplace=True):

	if inplace:
	
		for f in files:
			
			delete_columns_inplace(f, to_delete)
	
	else:
	
		assert (new_fnames != None) & (len(files) == len(new_fnames)), "You must provide new file name for every file if you don't want to delete the columns in-place."
		
		for i,f in enumerate(files):
		
			delete_columns_newf(f, to_delete, new_fnames[i])



def delete_comments_file(fname, identifier):
	
	with in_place.InPlace(fname) as f:
		
		for line in f:
		
			if line != identifier + "\n":
				f.write(line)
			else: 
				break


def delete_comments_files(files, identifier):

	for f in files:
	
		delete_comments_file(f, identifier)



def delete_rows_file(fname, cols, crits):

	crits = [str(c) for c in crits]
	
	with open(fname, "r") as old, open(fname + "_new", "w") as new:
		
		header = old.readline()
		header = header.split(sep="\t")
		header[-1] = header[-1][:-1]
		
		indices_of_cols = [first_occurance(header, col) for col in cols]
		
		assert -1 not in indices_of_cols, "Some criteria columns were not found in the header."
		
		new.write("\t".join(header) + "\n")
		
		for line in old:
		
			line = line.split(sep="\t")
			line[-1] = line[-1][:-1]
			
			checks = [line[c_index] == crits[i] for i, c_index in enumerate(indices_of_cols)]
			
			if sum(checks):
				continue
			else:
				new.write("\t".join(line) + "\n")
	
	os.rename(fname + "_new", fname)



def delete_rows_files(fnames, cols, crits):
	
	for f in fnames:
	
		delete_rows_file(f, cols, crits)



def delete_sign_file(fname, sign):
	
	with in_place.InPlace(fname) as f:
	
		for line in f:
		
    			line = line.replace(sign, "")
    			f.write(line)



def delete_sign_files(files, sign):

	for f in files:
	
		delete_sign_file(f, sign)



def filter_file(fname, cols, crits):

	n_crits = len(crits)
	crits = [[str(c) for c in crit] for crit in crits]
	
	with open(fname, "r") as old, open(fname + "_new", "w") as new:
		
		header = old.readline()
		header = header.split(sep="\t")
		header[-1] = header[-1][:-1]
		
		indices_of_cols = [first_occurance(header, col) for col in cols]
		
		assert -1 not in indices_of_cols, "Some criteria columns were not found in the header."
		
		new.write("\t".join(header) + "\n")
		
		for line in old:
		
			line = line.split(sep="\t")
			line[-1] = line[-1][:-1]
			
			checks = [line[c_index] in crits[i] for i, c_index in enumerate(indices_of_cols)]
			
			if sum(checks) == n_crits:
				new.write("\t".join(line) + "\n")
			else:
				continue
	
	os.rename(fname + "_new", fname)



def filter_files(fnames, cols, crits):
	
	for f in fnames:
	
		filter_file(f, cols, crits)



def first_occurance(my_list, lookup):

	for i, entry in enumerate(my_list):
		
		if entry == lookup or entry == lookup + "\n": return i
	
	return -1



def merge_files(files, new_fname):

	new_header = []

	with open(new_fname, "w") as m:
	
		for i,fi in enumerate(files):
		
			with open(fi, "r") as f:
			
				header = f.readline()
				header = header.split(sep="\t")
				
				if i==0: 
					new_header = header
					m.write("\t".join(new_header))
				else:
					positions = [first_occurance(new_header, h) for h in header]
				
				for line in f:
					
					line = line.split(sep="\t")
					line[-1] = line[-1][:-1]
					
					if i==0:
						new_line = line
					else:
						new_line = [line[pos] for pos in positions]
					new_line[-1] += "\n"
					
					m.write("\t".join(new_line))



def pivot_longer_file(fname, old_columns, new_columns):

	with open(fname, "r") as old, open(fname + "_new", "w") as new:
	
		header = old.readline()
		header = header.split(sep="\t")
		header[-1] = header[-1][:-1]
		
		positions = [first_occurance(header, oc) for oc in old_columns]
		
		new_header = [col for col in header if col not in old_columns] + new_columns
		
		new.write("\t".join(new_header) + "\n")
		
		for line in old:
		
			line = line.split(sep="\t")
			line[-1] = line[-1][:-1]
			
			new_line_base = [entry for i,entry in enumerate(line) if i not in positions]
			
			for pos in positions:
			
				new_line = new_line_base + [header[pos], line[pos]]
				
				new.write("\t".join(new_line) + "\n")			

	os.rename(fname + "_new", fname)



def pivot_longer_files(fnames, old_columns, new_columns):

	for f in fnames:
		
		pivot_longer_file(f, old_columns, new_columns)



def read_dict(fname):
	
	my_dict = {}

	with open("dics_and_lists/" + fname, "r") as file:
	
		for line in file:
		
			line = line.split(sep="\t")
			my_dict[line[0]] = line[1][:-1]
	
	return my_dict



def read_list(fname):
	
	my_list = []

	with open(fname, "r") as file:
	
		for line in file:
		
			my_list.append(line[:-1])
	
	return my_list



def split_rows_file(fname, block_sizes):
	
	positions = [0] + cumsums(block_sizes)
	
	with in_place.InPlace(fname) as f:
		
		for line in f:
		
			new_line = [line[pos:positions[i+1]] for i,pos in enumerate(positions) if i<len(positions)-1] + [line[positions[-1]:]]
			new_line = [entry.strip() for entry in new_line]
			
			f.write("\t".join(new_line) + "\n")


def split_rows_files(fnames, block_sizes):

	for f in fnames:
	
		split_rows_file(f, block_sizes)
