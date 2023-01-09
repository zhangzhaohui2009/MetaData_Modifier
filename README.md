This is a Python utility to reprocess/modify the netCDF metadata attributes. The file MerraMetaData_Modifier.py encloses the core python modules to read and process the new attribute LUTs(metadata) in excel, csv, and ascii files, and further add, remove and modify the exisiting metadata attributes of the target netCDF data files. 

M2OCEAN_global_metadata_main.py is the main driver for processing the M2OCEAN netCDF data files. This main driver
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
