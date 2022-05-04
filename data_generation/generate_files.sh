#!/bin/sh

# BMI706: Data Visualization Project Mortality Data
# April 2022
# Author: Benedikt Geiger

# This bash script downloads the county level population and mortality files for 1968-1988 
# and formats all population and mortality files for the years 1968-2016

pip install in_place

# Unzip state level CDC WONDER data; downlaod and add compressed population files for 1968-1988
unzip ./population/original_files.zip
rm ./population/original_files.zip
mv original_files ./population/original_files

echo Download county population files...
wget https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NVSS/cmf/pop6878.zip
wget https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NVSS/cmf/pop7988.zip
echo Done!

unzip pop6878.zip
unzip pop7988.zip

rm *.zip

mv Pop6878.txt ./population/original_files/Pop6878_county.txt
mv Pop7988.txt ./population/original_files/Pop7988_county.txt


# Unzip state level CDC WONDER data; downlaod and add compressed mortality files for 1968-1988
unzip ./mortality/original_files.zip
rm ./mortality/original_files.zip
mv original_files ./mortality/original_files

echo Download county mortality files...
wget https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NVSS/cmf/mort6878.zip
wget https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NVSS/cmf/mort7988.zip
echo Done!

unzip mort6878.zip
unzip mort7988.zip

rm *.zip

mv Mort6878.txt ./mortality/original_files/Mort6878_county.txt
mv Mort7988.txt ./mortality/original_files/Mort7988_county.txt


# Data generation with python scripts
for file in generate*.py
do
	echo Executing "$file"
	python3 "$file"
done


echo Computing mortality rates
python3 compute_mortality_rates.py
