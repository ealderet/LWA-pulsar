#!/usr/bin/env python3

"""
Runs through all steps of PRESTO pulsar search. Can include rfi masking, can start from
HDF5 or PSRFITS. If starting with HDF5, can start with donwselected file. There cannot be
more than one type of any filetype in the working directory, as this script cannot
distinguish between files. I may change that later.
"""

import os
import re
import argparse
import tempfile
from astropy.coordinates import Angle as AstroAngle
from lsl.reader.ldp import DRXFile
from lsl.common import metabundle, metabundleADP
from lsl.misc import parser as aph

writePsrfits_directory = '/home/lwa/pulsar/writePsrfits2FromHDF5.py'
downselect_directory = '/data/scripts/downselect.py'
grab_directory = '/data/scripts/grab.py'

def poplines():
    """
    Temporary fix for writePsrfits2FromHDF5.py errors.
    First two pops remove '.decode()'
    Last if statement removes human verification on ra/dec, raises error if they are
    set to null instead.
    """
    # Read in file
    with open(writePsrfits_directory, 'r', encoding='utf8') as file:
        lines = file.readlines()
    
    # Pop .decode() lines
    if lines[51].strip() == "station = station.decode()":
        lines[51] = '\n'
    if lines[60].strip() == "sourceName = sourceName.decode()":
        lines[60] = '\n'

    # Remove verification, raise error instead
    if lines[98].strip() == "out = input('=> Accept? [Y/n] ')":
        for i in range(98, 102):
            lines[i] = '\n'
        lines[102] = "            if tempRA == '---' or tempDec == '---':"
        lines[103] = "                sys.exit()"

    # Write new file
    with open(writePsrfits_directory, 'w', encoding='utf8') as file:
        file.writelines(lines)

def main(args):
    """
    Main func
    """
    # Fix writePsrfits2FromHDF5.py if not fixed already
    poplines()

    # Get params
    filename = args.filename
    source = args.source



    # Check if downselect.py or writePsrfits2FromHDF5.py have already been run
    count = 0
    decim_count = 0
    for file in os.popen("ls").read().split():
        if file.endswith('.fits'):
            count += 1
        if file.endswith(".hdf5"):
            decim_count += 1



    # If writePsrfits2FromHDF5.py has NOT been run
    if count == 0:

        # If downselect.py has NOT been run
        if decim_count == 0:
            # Run downselect.py
            os.system(downselect_directory + f" -p -s 35,80 1 {filename}")
            decim_filename = filename + "-decim.hdf5"
        # If downselect.py has been run MORE THAN once
        if decim_count > 1:
            raise Exception("More than one decim file detected!")

        source_string = ''
        # If source given
        if source is not None:
            # Make pulsar source argument string for PSRFITS conversion and use in prepfold
            source_string = f"-s {source}"
        
        # Run writePsrfits2FromHDF5.py
        os.system(writePsrfits_directory + f" -p {source_string} {decim_filename}")
        
        # Check if writePsrfits2FromHDF5.py conversion failed (check for error in writePsrfits2FromHDF5.py if this happens)
        count = 0
        for file in os.popen("ls").read().split():
            if file.endswith('.fits'):
                count += 1
        if count == 0:
            raise Exception("FITS conversion failed!")
        
    # If writePsrfits2FromHDF5.py has been run MORE THAN once
    if count > 1:
        raise Exception("More than one PSRFITS file in directory!")
    


    # Remove 'B' from source argument string
    noB_source = source.replace('B','')
    


    # RFI yes/no
    if args.rfibool is True:
        # Run rfifind
        os.system(f"rfifind -time [args.rfitime] -o {args.subname} *.fits")
        
        # Run prepfold with RFI mask
        os.system(f"prepfold -psr {noB_source} -slow -dm {args.dm} -mask *.mask *.fits")
    else:
        # Run prepfold without RFI mask
        os.system(f"prepfold -psr {noB_source} -slow -dm {args.dm} *.fits")
    
    
    # Check to see if prepfold failed to run (check for error in prepfold if this happens).
    count = 0
    for file in os.popen("ls").read().split():
        if file.endswith('.pfd.bestprof'):
            count += 1
    if count != 1:
        raise Exception("prepfold failed to run. Try checking to make sure the source is correct.")

    # Run grab.py to get necessary parameters of prepfold search
    os.system(grab_directory + " *.pfd.bestprof")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='build a Makefile for analyzing FRB data from the LWA',
        epilog='NOTE: --source, --ra, --dec, and --dm are only used if a DRX file is given, otherwise the values are automatically extracted from the metadata.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument('filename', type=str,
                        help='filename process - metadata or DRX')
    parser.add_argument('-s', '--source', type=str,
                        help='source name')
    parser.add_argument('-e', '--dm', type=float,
                        help='dispersion measure; pc/cm^3')
    parser.add_argument('-rfi', '--rfibool', type=bool,
                        help='decide if rfi flagging should happen')
    parser.add_argument('-n', '--subname', type=str,
                        help='name for subfiles created along the way')
    parser.add_argument('-t', '--rfitime', type=float,
                        help='time for rfifind')
    args = parser.parse_args()
    main(args)
