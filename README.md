This README will be broken into 3 parts:

1. Explaining PRESTO and the processing pipeline
2. Explaining pulsar_search.py
3. Explaining pulsar_search.py's dependencies

# PRESTO and the processing pipeline
### downselect.py
When given a raw HDF5 file from OVRO-LWA, the first thing you have to do is run downselect.py to select the frequency range you want. The original raw files have a frequency range of -11MHz to 86MHz. PRESTO really, really doesn't like the negative frequencies, so at the very least get rid of those. I would recommend a frequency range of 35MHz to 80MHz for most pulsars, but that can be changed if necessary. An example run of downselect.py is:
$$	ext{downselect.py -p -s 35,80 1 <filename>}$$
"-p" removes some flagging, the "1" after the selected frequencies is required.

### writePsrfits2FromHDF5.py
After running downselect.py, you want to convert the HDF5 file to PSRFITS with writePsrfits2FromHDF5.py
#### Necessary changes
Before converting, we have to remove line 52, "station = station.decode()", and line 61, "sourceName = sourceName.decode()". If we don't remove these lines, we get an error saying "str attribute has no option 'decode'." Removing these lines gets rid of the error and still allows the script to run as normal. I am unsure why these were added in the first place.
#### Converting files
An example of running writePsrfits2FromHDF5.py is below
$$\text{writePsrfits2FromHDF5.py -p pulsar_name filename},$$
where <pulsar_name> is the name of your pulsar in the Besselian epoch (B0834+06 as an example). The 'B' is required.

Now that we have a .fits file, we can either go straight to folding our pulsar data, or we can do some RFI masking with rfifind.

### rfifind
rfifind is fairly straightforward, you can read the PRESTO documentation to get a better understanding of how it masks RFI. An example of running rfifind is given below
$$\text{rfifind -time 30.0 -o sub_filename filename}$$
<sub_filename> is the prefix you want the files created by rfifind to start with. I usually do the name of my source. The time can be changed if you find that rfifind is masking too much or too little, it defaults to 30 if the option isn't specified. For higher DM pulsars, I've found that leaving it at 30 is best, but again this is subject to your object.

### prepfold
prepfold is what we use to fold our timeseries data and find our pulsar. An example of running prepfold is below.
$$\text{prepfold -psr pulsar_name_no_B -slow -dm DM_value -mask rfi_mask filename}$$
Breaking it down:
1. <pulsar_name_no_B> is the same name you gave to writePsrfits2FromHDF5.py, but without the 'B' at the front.
2. -slow makes prepfold search more finely. I would recommend leaving this on.
3. <DM_value> is the expected DM of your pulsar
4. <rfi_mask> is the '.mask' file given to you by rfifind. If you didn't run rfifind, don't include -mask.

This gives you three files, the two you're interested in are the '.ps' and '.bestprof' files. The '.ps' file you can convert to a pdf (Apple as a built-in "pstopdf" function in the command line), and the '.bestprof' file you can read to see some of the parameters of the best result. These parameters are also on the pdf, but they can be scraped from the '.bestprof' file easily if needed.

# pulsar_search.py
This script takes all the steps I just described and truncates them to one command. It also returns the best DM, SNR, and period of the found pulsar.

### DEPENDENCIES
pulsar_search.py requires both downselect.py and grab.py to work. If you're using this in a location other than my (Ethan Alderete's) environment in the lwaproject/lsl:pulsar podman container, you also have to change the directories leading to downselect.py, grab.py, and writePsrfits2FromHDF5.py at the top of pulsar_search.py.

### Example
This is an example of what I run while in the lwaproject/lsl:pulsar container
$$\text{/data/scripts/pulsar_search.py -s B0834+06 -e 26.7 -rfi True -n B0834+06 -t 30.0},$$
where
1. -s is the pulsar name
2. -e is the rough DM
3. -rfi is a boolean to turn on/off rfi masking
4. -n is the subname given to rfi files
5. -t is the time given to rfi masking

If you're not doing rfi masking, obviously the last three options aren't needed and can be left out.

That's it, get to hunting pulsars!
