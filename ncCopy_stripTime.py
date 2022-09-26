#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import argparse

def parse_args():
    p = argparse.ArgumentParser(description='Flatten a lat-lon to 1D')
    p.add_argument('input',type=str,help='input file',default=None)
    p.add_argument('output',type=str,help='output file',default=None)
    return vars(p.parse_args())

#------------------
# Opening the file
#------------------
comm_args    = parse_args()
Input_file   = comm_args['input']
Output_file  = comm_args['output']
ncFid = Dataset(Input_file, mode='r')
ncFidOut = Dataset(Output_file, mode='w', format='NETCDF4')
#---------------------
# Extracting variables
#---------------------

haveLev = False
for dim in ncFid.dimensions:
    if dim == 'lev':
       haveLev = True
   
time = ncFid.variables['time'][:]
if haveLev:
   lev  = ncFid.variables['lev'][:]
lat  = ncFid.variables['lat'][:]
lon  = ncFid.variables['lon'][:]

for att in ncFid.ncattrs():
    setattr(ncFidOut,att,getattr(ncFid,att))

lonOut = ncFidOut.createDimension('lon', len(lon))
lonsOut = ncFidOut.createVariable('lon','f4',('lon',))
for att in ncFid.variables['lon'].ncattrs():
    setattr(ncFidOut.variables['lon'],att,getattr(ncFid.variables['lon'],att))
lonsOut[:] = lon


latOut = ncFidOut.createDimension('lat', len(lat))
latsOut = ncFidOut.createVariable('lat','f4',('lat',))
for att in ncFid.variables['lat'].ncattrs():
    setattr(ncFidOut.variables['lat'],att,getattr(ncFid.variables['lat'],att))
latsOut[:] = lat

if haveLev:
   levOut = ncFidOut.createDimension('lev', len(lev))
   levsOut = ncFidOut.createVariable('lev','f4',('lev',))
   for att in ncFid.variables['lev'].ncattrs():
       setattr(ncFidOut.variables['lev'],att,getattr(ncFid.variables['lev'],att))
   levsOut[:] = lev

timeOut = ncFidOut.createDimension('time', 1)
timesOut = ncFidOut.createVariable('time','f4',('time',))
for att in ncFid.variables['time'].ncattrs():
    setattr(ncFidOut.variables['time'],att,getattr(ncFid.variables['time'],att))
timesOut[:] = 0

Exclude_Var = ['lon','lat','time','lev']
for var in ncFid.variables:
   if var not in Exclude_Var:
      temp = ncFid.variables[var][:]
      dim_size =len(temp.shape)
      if dim_size == 4:
         Tout = ncFidOut.createVariable(var,'f4',('lev','lat','lon',),fill_value=1.0e15)
         for att in ncFid.variables[var].ncattrs():
            if att != "_FillValue":
               setattr(ncFidOut.variables[var],att,getattr(ncFid.variables[var],att))
            Tout[:,:,:] = temp[0,:,:,:]
      elif dim_size == 3:
         Tout = ncFidOut.createVariable(var,'f4',('lat','lon',),fill_value=1.0e15)
         for att in ncFid.variables[var].ncattrs():
            if att != "_FillValue":
               setattr(ncFidOut.variables[var],att,getattr(ncFid.variables[var],att))
            Tout[:,:] = temp[0,:,:]
ncFidOut.close()


#-----------------
# Closing the file
#-----------------
ncFid.close()


