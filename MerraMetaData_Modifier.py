#!/usr/bin/env python

import netCDF4
import numpy as np
import glob, pathlib, shutil
import os, sys
import pandas as pd
from datetime import date, timedelta


__authors__ = ["Zhaohui Zhang"]
__license__ = "Public Domain"
__maintainer__ = "Zhaohui Zhang"
__email__ = "zhaohui.zhang@nasa.gov"
__date__  = "Dec 15, 2022"

class MetaData_Dictionary(object):
   def __init__(self, MetaData_File=None, **kwargs):
      self.df = None
      self.usecols = None
      if MetaData_File != None :
         self.loadMetaDataTabel(MetaData_File, **kwargs)

   def __del__(self):
       del self.df

   def loadMetaDataTabel(self, MetaData_File,**kwargs):
      if not os.path.isfile(MetaData_File):
         err = "Error: file not exis {} ... ".format(MetaData_File)
         print(err)
         return(False)
  
      # check input file type by file extension
      file_type = pathlib.Path(MetaData_File).suffix
      if file_type not in ['.csv','.xls','.txt']: 
         print("Error: input file should be .csv or .xls ..." )
         return(False)

      usecols = kwargs.get('usecols', None)
      
      try:
         if file_type == '.xls':         
            sheet_name = kwargs.get('sheet_name','metadata')
            #self.df = pd.read_excel(MetaData_File, sheet_name=sheet_name, usecols=usecols)
            self.df = pd.read_excel(MetaData_File, sheet_name=sheet_name)
            self.df = self.df.rename(columns=lambda x: x.strip())
            if usecols is not None:
               self.df = self.df[usecols]
            cc = self.df.columns.values
            self.usecols = cc if usecols == None else usecols
            #print(self.df[self.KeyCol] )

         if file_type == '.csv' or file_type == '.txt':         
            self.df = pd.read_csv(MetaData_File,**kwargs)
            self.df = self.df.rename(columns=lambda x: x.strip())
            if usecols is not None:
               self.df = self.df[usecols]
            cc = self.df.keys().values
            self.usecols = cc if usecols == None else usecols
            for col in self.usecols:
                self.df[col] = self.df[col].map(str.strip)
            #print(self.df[self.KeyCol] )
               
          #for row in self.df.itertuples(index=False):
          #   print(row)
      except IOError:
         os.touch(MetaData_File)

   def selectOneRow(self, KeyName, KeyCol=None):
       df = self.df
       if df is None:
          print("MetaData has not not been loaded ...")
          return None
       if KeyCol == None:
          KeyCol = self.usecols[0]
       if KeyCol not in self.usecols:
          print("keyCol {} is not in the usecols {}".format(KeyCol,self.usecols))
          return(None)

       meta = df.loc[df[KeyCol] == KeyName]
       n_attrs = len(meta)
       if n_attrs == 0:
          print("Error: {} is not a valid key ...".format(KeyName))
          print("Valid Keys: \n", df[KeyCol])
          return None
       if n_attrs > 1:
          print("Warning: {} is not a unique key ...".format(KeyName))
       #print(meta.to_dict('records')[0])
       attrs = meta.to_dict('records')[0]
       return(attrs)

   def selectTwoCols(self, KeyCol=None, ValCol=None):
       df = self.df
       if df is None:
          print("MetaData has not not been  defined ...")
          return None

       if KeyCol == None :
          KeyCol = self.usecols[0]
       if KeyCol not in self.usecols:
          print("KeyCol Name {} is not in the usecols {}".format(KeyCol,self.usecols))
          return(None)
       if ValCol == None :
          ValCol = self.usecols[1]
       if ValCol not in self.usecols:
          print("ValCol Name {} is not in the usecols {}".format(ValCol,self.usecols))
          return(None)

       meta_keys = df[KeyCol].values
       meta_values = df[ValCol].values
       #attrs = df.groupby(self.KeyCol)[ValCol].apply(list).to_dict()
       attrs = dict(zip(meta_keys, meta_values))
       return(attrs)


class MetaData_Modifier(object):
   def __init__(self, InFile, OutFile=None ):
      if not os.path.isfile(InFile):
         err = "Error: file not exis {} ... ".format(InFile)
         print(err)
         return(False)

      self.fileName = InFile
      if OutFile != None:
         shutil.copyfile(InFile, OutFile)
         self.fileName = OutFile

      try:
         self.fid = netCDF4.Dataset(self.fileName,'r+',format='NETCDF4')
      except IOError:
         os.touch(self.fileName)
      self.nc_attrs = self.fid.ncattrs()
      #self.print_attribute()
 
   def close(self):
       if self.fid != None:
          self.fid.close()

   def add_globalmeta(self, attrs, verbose=False, overwrite=True):
      ds = self.fid
      if attrs == None :
        return None
 
      def _attr_exist(attr, attr_list):
         for a in attr_list:
           if attr == a :
              return (1, a)
           elif attr.lower() == a.lower() :
              return (2, a)
         return (0,attr)   
      for key, value in attrs.items():
         value = '' if pd.isna(value) else value
         self.nc_attrs = self.fid.ncattrs()
         kstate, attr =  _attr_exist(key, self.nc_attrs)
         if kstate == 0 : 
            ds.setncatts({key: value})
            if verbose:
               print("New Meta: {} = {}".format(key,  value))
         elif overwrite and (kstate == 1):
            old_value = ds.getncattr(attr)
            ds.setncatts({key: value})
            if verbose:
               print("Replace Meta: {} from  '{}' to '{}'".format(key,  old_value, value))
         elif overwrite and (kstate == 2):
            old_value = ds.getncattr(attr)
            ds.delncattr(attr)
            ds.setncatts({key: value})
            if verbose:
               print("Replace Meta: {} from  '{}' to '{}'".format(key,  old_value, value))
         self.nc_attrs = self.fid.ncattrs()


   def add_globalmeta_file(self, attr_file, KeyCol=None, KeyName=None, ValCol=None,  **kwargs):
      if KeyCol == None:
         print("Error: the KeyCol (column containg the keys) is not set ...")
         return
       
      verbose = kwargs.get('verbose', False)
      overwrite = kwargs.get('overwrite', True)
      if ((KeyName == None and ValCol == None) or 
         (KeyName != None and ValCol != None)) :
         message = '''Error: set either an element in the KeyCol (KeyName=) 
          or a column name (ValCol=), not both or none ...'''
         print(message)
         return
      md = MetaData_Dictionary()
      if ValCol != None:
         # global attributes with static values common in all files
         md.loadMetaDataTabel(attr_file,**kwargs) 
         attrs= md.selectTwoCols(KeyCol=KeyCol, ValCol=ValCol)
         self.add_globalmeta(attrs, verbose=verbose)
 
      if KeyName != None:
         # global attributes with static values specific to product collection
         md.loadMetaDataTabel(attr_file, **kwargs)
         attrs = md.selectOneRow(KeyName, KeyCol=KeyCol) 
         self.add_globalmeta(attrs, verbose=verbose)

   def list_globalmeta(self, verbose=False):
      for nc_attr in self.nc_attrs:
          print('\t%s:' % nc_attr, repr(self.fid.getncattr(nc_attr)))

