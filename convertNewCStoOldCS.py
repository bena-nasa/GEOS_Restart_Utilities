#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import numpy
import argparse

def parse_args():
    p = argparse.ArgumentParser(description='Flatten a lat-lon to 1D')
    p.add_argument('input',type=str,help='input file',default=None)
    p.add_argument('output',type=str,help='output file',default=None)
    p.add_argument('-s','--striptime',action='store_true',help="strip time if present")
    return vars(p.parse_args())

#------------------
# Opening the file
#------------------
comm_args    = parse_args()
Input_file   = comm_args['input']
Output_file  = comm_args['output']
strip_time = comm_args['striptime']

ncFid = Dataset(Input_file, mode='r')
ncFidOut = Dataset(Output_file, mode='w', format='NETCDF4')

#---------------------
# Extracting variables
#---------------------

haveLev = False
for dim in ncFid.dimensions:
    if dim == 'lev':
           haveLev = True
           levSize = len(ncFid.dimensions['lev'])


haveTime = False
for dim in ncFid.dimensions:
    if dim == 'time':
       haveTime = True
       timeSize = len(ncFid.dimensions['time'])

if not haveTime:
    strip_time = False

if haveTime:
   time = ncFid.variables['time'][:]
if haveLev:
   lev  = ncFid.variables['lev'][:]
   levSize = len(ncFid.dimensions['lev'])

cRes = len(ncFid.dimensions['Xdim'])

Xdim = ncFidOut.createDimension('lon',cRes)
Ydim = ncFidOut.createDimension('lat',cRes*6)

if haveLev:
   levOut = ncFidOut.createDimension('lev',levSize)

if haveTime:
   timeOut = ncFidOut.createDimension('time',timeSize)

vXdim = ncFidOut.createVariable('lon','f8',('lon'))
vYdim = ncFidOut.createVariable('lat','f8',('lat'))
setattr(ncFidOut.variables['lon'],'units','degrees_east')
setattr(ncFidOut.variables['lat'],'units','degrees_north')
setattr(ncFidOut.variables['lon'],'long_name','longitude')
setattr(ncFidOut.variables['lat'],'long_name','latitude')
vXdim[:]=range(1,cRes+1)
vYdim[:]=range(1,(cRes*6)+1)

if haveLev:
   vLevOut= ncFidOut.createVariable('lev','f8',('lev'))
   for att in ncFid.variables['lev'].ncattrs():
      setattr(ncFidOut.variables['lev'],att,getattr(ncFid.variables['lev'],att))
   vLevOut[:] = range(1,levSize+1)

if haveTime:
   vtimeOut = ncFidOut.createVariable('time','i4',('time'))
   for att in ncFid.variables['time'].ncattrs():
      setattr(ncFidOut.variables['time'],att,getattr(ncFid.variables['time'],att))
   vtimeOut[:] = range(timeSize)

Exclude_Var = ['Xdim','Ydim','time','lev','lons','lats','contacts','anchor','cubed_sphere','nf','ncontact','corner_lons','corner_lats']

for var in ncFid.variables:
   if var not in Exclude_Var:
      temp = ncFid.variables[var][:]
      dim_size =len(temp.shape)
      if haveTime:
         dim_size = dim_size -1
     
      time_in_output = haveTime and (not strip_time)
      if dim_size == 4:
         if time_in_output:
            tout = ncFidOut.createVariable(var,'f4',('time','lev','lat','lon'),fill_value=1.0e15)
         else:
            tout = ncFidOut.createVariable(var,'f4',('lev','lat','lon'),fill_value=1.0e15)
         for att in ncFid.variables[var].ncattrs():
            if att != "_FillValue":
               setattr(ncFidOut.variables[var],att,getattr(ncFid.variables[var],att))
         for i in range(6):
             il =  cRes*i
             iu =  cRes*(i+1)
             for j in range(levSize):
                if haveTime:
                   if strip_time:
                      tout[j,il:iu,:]=temp[0,j,i,:,:]
                   else:
                      tout[:,j,il:iu,:]=temp[:,j,i,:,:]
                else:
                   tout[j,il:iu,:]=temp[j,i,:,:]

      elif dim_size == 3: 
         if time_in_output:
            tout = ncFidOut.createVariable(var,'f4',('time','lat','lon'),fill_value=1.0e15)
         else:
            tout = ncFidOut.createVariable(var,'f4',('lat','lon'),fill_value=1.0e15)
         for att in ncFid.variables[var].ncattrs():
            if att != "_FillValue":
               setattr(ncFidOut.variables[var],att,getattr(ncFid.variables[var],att))
         setattr(ncFidOut.variables[var],'grid_mapping','cubed_sphere')
         setattr(ncFidOut.variables[var],'coordinates','lons lats')
         for i in range(6):
             il =  cRes*i
             iu =  cRes*(i+1)
             for j in range(cRes):
                for k in range(cRes):
                   if haveTime:
                      if strip_time:
                         tout[il+k,j]=temp[0,i,k,j].copy()
                      else:
                         tout[:,il+k,j]=temp[:,i,k,j].copy()
                   else:
                      tout[il+k,j]=temp[i,k,j]

#-----------------
# Closing the file
#-----------------
ncFidOut.close()
ncFid.close()

