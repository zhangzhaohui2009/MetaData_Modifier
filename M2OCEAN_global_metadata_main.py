#!/usr/bin/env python
import os, sys
from datetime import date, timedelta
from MerraMetaData_Modifier import MetaData_Dictionary, MetaData_Modifier

__authors__ = ["Zhaohui Zhang"]
__license__ = "Public Domain"
__maintainer__ = "Zhaohui Zhang"
__email__ = "zhaohui.zhang@nasa.gov"
__date__  = "Jan 3, 2023"

'''

Main driver to reprocess/modify the global metadata of the M2OCEAN data files. This main driver
program may be used as a template for other product/collection files where some specific (dynamic)
metadata information need to be extracted from data file names or other sources, rather than from
the excel/csv/ascii table files.

How to use:
  
   M2OCEAN_global_metadata_main.py --help

   e.g., 
   a) to process individula file
   M2OCEAN_global_metadata_main.py sample_data.20220601/M2OCEAN_S2SV3.ocn_tavg_1mo_glo_T1440x1080_slv.19980201_0000z.nc4
   b) to process all the files in a subdirectory 
   M2OCEAN_global_metadata_main.py sample_data.20220601

'''

def m2ocean_main(inFile, outFile, **kwargs):
    verbose = kwargs.get('verbose', False)
    meta_excel = kwargs.get('excel_file', 'M2OCEAN_global_metadata.xls')
    meta_csv   = kwargs.get('csv_file', 'M2OCN_gmet.csv')

    def InfoFromFileName(fileName):
        ScienceProductName = fileName.split('.')[1]
        dateTimeInfo = {}
        myDateTime = fileName.split('.')[-2].split('_')
        dstr = myDateTime[0]
        if len(dstr) == 6:
           dstr += "01" 
        if len(dstr) != 8:
           print("Error in getting the date&time information from input filename ...")
           print("input filename: {}".format(fileName))
           return None
        year, month, day = int(dstr[0:4]), int(dstr[4:6]), int(dstr[6:8])
        dateTimeInfo['BeginDate'] = date(year, month,day).isoformat()
        dm = 1 # add the number of months of the date span
        year, month = year + int((month+dm)/12), ((month+dm-1)%12)+1
        dateTimeInfo['EndDate'] = (date(year, month, day)-timedelta(1)).isoformat() 
        dateTimeInfo['BeginTime'] = "00:00:00.0000"
        dateTimeInfo['EndTime'] = "23:59:59.9999"
        return(ScienceProductName, dateTimeInfo)

    basename=os.path.basename(inFile)
    ProductName, dateTimeInfo = InfoFromFileName(basename)
    if dateTimeInfo != None:
       RangeBeginningDate = dateTimeInfo['BeginDate']
       RangeEndingDate = dateTimeInfo['EndDate']
       RangeBeginningTime = dateTimeInfo['BeginTime']
       RangeEndingTime = dateTimeInfo['EndTime']
    #ptime = '20220809T10:00:00Z'   # product create time 
    ptime = date.today().strftime("%Y%m%dT%H:%M:%SZ")
    
    # map productName to shortName
    md = MetaData_Dictionary()
    md.loadMetaDataTabel(meta_excel,
                          sheet_name='products', usecols=['ShortName','ScienceProductName'])
    attrs = md.selectOneRow(ProductName, KeyCol='ScienceProductName')
    shortName = attrs['ShortName']
    
    # global attributes with dynamic values from file to file
    attrs={
          'Title': shortName,
          'GranuleID':basename, 
          'Filename':basename,
          'ProductionDateTime': ptime,
          'RangeBeginningDate': RangeBeginningDate,
          'RangeBeginningTime': "00:00:00.0000",
          'RangeEndingDate':  RangeEndingDate,
          'RangeEndingTime': "23:59:59.9999",
     }

    mf = MetaData_Modifier(inFile, OutFile=outFile)
    mf.add_globalmeta(attrs, verbose=verbose)

    # global attributes with static values common in all files
    mf.add_globalmeta_file(meta_excel, KeyCol='ShortName', KeyValue=shortName, sheet_name='metadata')

    # global attributes with static values specific to product collection
    mf.add_globalmeta_file(meta_csv, delimiter='=', header=None, names=['a','b'], KeyCol='a',ValCol='b')
    mf.close()
    
if __name__ == "__main__":
   import argparse
   import glob 

   parser = argparse.ArgumentParser(description='Main program to modify the metadata of M2OCEAN NC4 files ')
   parser.add_argument("fpath", type=str,  help="Single file or path of M2OCEAN NC4 data")
   parser.add_argument("outdir", type=str,  help="output subdirectory", default="results", nargs='?')
   parser.add_argument("-v","--verbose", action='store_true',  help="print info for debug")
   args = parser.parse_args()

   fpath = args.fpath
   verbose = args.verbose

   outdir = args.outdir
   if not os.path.exists(outdir):
      os.makedirs(outdir)
   if os.path.isdir(fpath):
     filelist = glob.iglob(fpath+"/M2OCEAN_S2SV3*.nc4", recursive=False)
   else:
     filelist = [fpath]

   for infile in filelist:
      _, basename = os.path.split(os.path.abspath(infile))
      print(infile)
      outfile = os.path.join(outdir,basename)
      m2ocean_main(infile, outfile, verbose=verbose)

