#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import numpy
import argparse

def parse_args():
    p = argparse.ArgumentParser(description='convert old style cube to new style cube input')
    p.add_argument('-i','--input',type=str,help='input file',default=None)
    p.add_argument('-e','--example',type=str,help='example file',default=None)
    p.add_argument('-o','--output',type=str,help='output file',default=None)
    return vars(p.parse_args())

#------------------
# Opening the file
#------------------
comm_args    = parse_args()
Input_file   = comm_args['input']
Output_file  = comm_args['output']
Example_file  = comm_args['example']

has_example = (Example_file != None)
ncFid = Dataset(Input_file, mode='r')
if has_example:
   ncFidEx = Dataset(Example_file, mode='r')
ncFidOut = Dataset(Output_file, mode='w', format='NETCDF4')

#---------------------
# Extracting variables
#---------------------

haveLev = False
for dim in ncFid.dimensions:
    if dim == 'lev':
           haveLev = True
           levSize = len(ncFid.dimensions['lev'])

haveEdge = False
for dim in ncFid.dimensions:
    if dim == 'edge':
           haveEdge = True
           edgeSize = len(ncFid.dimensions['edge'])

haveTime = False
for dim in ncFid.dimensions:
    if dim == 'time':
       haveTime = True

if haveTime:
   time = ncFid.variables['time'][:]
if haveLev:
   lev  = ncFid.variables['lev'][:]
if haveEdge:
   edge  = ncFid.variables['edge'][:]


cRes = len(ncFid.dimensions['lon'])

Xdim = ncFidOut.createDimension('Xdim',cRes)
Ydim = ncFidOut.createDimension('Ydim',cRes)
nf = ncFidOut.createDimension('nf',6)
ncontact = ncFidOut.createDimension('contact',4)

if haveLev:
   levOut = ncFidOut.createDimension('lev',levSize)

if haveEdge:
   edgeOut = ncFidOut.createDimension('edge',edgeSize)

timeOut = ncFidOut.createDimension('time',1)

vXdim = ncFidOut.createVariable('Xdim','f8',('Xdim'))
vYdim = ncFidOut.createVariable('Ydim','f8',('Ydim'))
setattr(ncFidOut.variables['Xdim'],'units','degrees_east')
setattr(ncFidOut.variables['Ydim'],'units','degrees_north')
setattr(ncFidOut.variables['Xdim'],'long_name','Fake Longitude for GrADS Compatibility')
setattr(ncFidOut.variables['Ydim'],'long_name','Fake Latitude for GrADS Compatibility')
vXdim[:]=range(1,cRes+1)
vYdim[:]=range(1,cRes+1)
vnf = ncFidOut.createVariable('nf','i4',('nf'))
vnf[:]=range(1,7)
setattr(ncFidOut.variables['nf'],'long_name','cubed-sphere face')
setattr(ncFidOut.variables['nf'],'axis','e')
setattr(ncFidOut.variables['nf'],'grads_dim','e')

if haveLev:
   vLevOut= ncFidOut.createVariable('lev','f8',('lev'))
   for att in ncFid.variables['lev'].ncattrs():
      setattr(ncFidOut.variables['lev'],att,getattr(ncFid.variables['lev'],att))
   vLevOut[:] = range(1,levSize+1)

if haveTime:
   vtimeOut = ncFidOut.createVariable('time','i4',('time'))
   for att in ncFid.variables['time'].ncattrs():
      setattr(ncFidOut.variables['time'],att,getattr(ncFid.variables['time'],att))
   vtimeOut[:] = 0

vchar = ncFidOut.createVariable('cubed_sphere','S1')
setattr(ncFidOut.variables['cubed_sphere'],'grid_mapping_name','gnomonic cubed-sphere')
setattr(ncFidOut.variables['cubed_sphere'],'file_format_version','2.90')
setattr(ncFidOut.variables['cubed_sphere'],'additional_vars','contacts,orientation,anchor')

Exclude_Var = ['Xdim','Ydim','time','lev','edge','lon','lat']

for var in ncFid.variables:
   if var not in Exclude_Var:
      temp = ncFid.variables[var][:]
      dim_size =len(temp.shape)
      print(var)
      haveTime = 'time' in ncFid.variables[var].dimensions
      if haveTime:
         dim_size = dim_size -1
      print(dim_size)
      print(haveTime)
      
      if dim_size == 3:
         for dim in ncFid.variables[var].dimensions:
             if dim == 'lev' or dim == 'edge':
                third_dim = dim

         if haveTime:
            tout = ncFidOut.createVariable(var,'f4',('time',third_dim,'nf','Ydim','Xdim'),fill_value=1.0e15)
         else:
            tout = ncFidOut.createVariable(var,'f4',(third_dim,'nf','Ydim','Xdim'),fill_value=1.0e15)
         for att in ncFid.variables[var].ncattrs():
            if att != "_FillValue":
               setattr(ncFidOut.variables[var],att,getattr(ncFid.variables[var],att))
         setattr(ncFidOut.variables[var],'grid_mapping','cubed_sphere')
         setattr(ncFidOut.variables[var],'coordinates','lons lats')
         for i in range(6):
             il =  cRes*i
             iu =  cRes*(i+1)
             if haveTime:
                tout[:,:,i,:,:] = temp[:,:,il:iu,:]
             else:
                tout[:,i,:,:] = temp[:,il:iu,:]

      elif dim_size == 2: 
         if haveTime:
            tout = ncFidOut.createVariable(var,'f4',('time','nf','Ydim','Xdim'),fill_value=1.0e15)
         else:
            tout = ncFidOut.createVariable(var,'f4',('nf','Ydim','Xdim'),fill_value=1.0e15)
         for att in ncFid.variables[var].ncattrs():
            if att != "_FillValue":
               setattr(ncFidOut.variables[var],att,getattr(ncFid.variables[var],att))
         setattr(ncFidOut.variables[var],'grid_mapping','cubed_sphere')
         setattr(ncFidOut.variables[var],'coordinates','lons lats')
         for i in range(6):
             il =  cRes*i
             iu =  cRes*(i+1)
             if haveTime:
                tout[:,i,:,:] = temp[:,il:iu,:]
             else:
                tout[i,:,:] = temp[il:iu,:]

      elif dim_size == 1: 
         tout = ncFidOut.createVariable(var,'f4',('edge'),fill_value=1.0e15)
         for att in ncFid.variables[var].ncattrs():
            if att != "_FillValue":
               setattr(ncFidOut.variables[var],att,getattr(ncFid.variables[var],att))
         setattr(ncFidOut.variables[var],'grid_mapping','cubed_sphere')
         setattr(ncFidOut.variables[var],'coordinates','lons lats')
         tout[:] = temp[:]


if has_example:
    XCdim = ncFidOut.createDimension('XCdim',cRes+1)
    YCdim = ncFidOut.createDimension('YCdim',cRes+1)
    center_lons = ncFidOut.createVariable('lons','f8',('nf','Ydim','Xdim'))
    setattr(ncFidOut.variables['lons'],'long_name','longitude')
    setattr(ncFidOut.variables['lons'],'units','degrees_east')
    center_lats = ncFidOut.createVariable('lats','f8',('nf','Ydim','Xdim'))
    setattr(ncFidOut.variables['lats'],'long_name','latitude')
    setattr(ncFidOut.variables['lats'],'units','degrees_north')

    center_lons[:,:,:] = ncFidEx.variables['lons'][:,:,:]
    center_lats[:,:,:] = ncFidEx.variables['lats'][:,:,:]


    corner_lons = ncFidOut.createVariable('corner_lons','f8',('nf','YCdim','XCdim'))
    setattr(ncFidOut.variables['corner_lons'],'long_name','longitude')
    setattr(ncFidOut.variables['corner_lons'],'units','degrees_east')
    corner_lats = ncFidOut.createVariable('corner_lats','f8',('nf','YCdim','XCdim'))
    setattr(ncFidOut.variables['corner_lats'],'long_name','latitude')
    setattr(ncFidOut.variables['corner_lats'],'units','degrees_north')

    corner_lons[:,:,:] = ncFidEx.variables['corner_lons'][:,:,:]
    corner_lats[:,:,:] = ncFidEx.variables['corner_lats'][:,:,:]
#-----------------
# Closing the file
#-----------------
ncFidOut.close()
ncFid.close()

