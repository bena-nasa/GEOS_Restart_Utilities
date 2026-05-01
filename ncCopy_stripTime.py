#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import argparse

def parse_args():
    p = argparse.ArgumentParser(description='Copy a NetCDF file, stripping the time dimension from all variables')
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
# Copy global attributes
#---------------------
for att in ncFid.ncattrs():
    setattr(ncFidOut, att, getattr(ncFid, att))

#---------------------
# Copy all dimensions
#---------------------
for dimname, dim in ncFid.dimensions.items():
    if dimname == 'time':
        ncFidOut.createDimension('time', 1)
    else:
        size = len(dim) if not dim.isunlimited() else len(dim)
        ncFidOut.createDimension(dimname, size)

#---------------------
# Copy all variables
#---------------------
for varname, var in ncFid.variables.items():
    src_dims = var.dimensions

    if varname == 'time':
        # Time variable: keep dimension but set value to 0
        fill = getattr(var, '_FillValue', None)
        kwargs = {}
        if fill is not None:
            kwargs['fill_value'] = fill
        vout = ncFidOut.createVariable('time', var.datatype, ('time',), **kwargs)
        for att in var.ncattrs():
            if att != '_FillValue':
                setattr(vout, att, getattr(var, att))
        vout[:] = 0

    elif 'time' in src_dims:
        # Data variable that depends on time: strip the time dimension
        new_dims = tuple(d for d in src_dims if d != 'time')
        fill = getattr(var, '_FillValue', None)
        kwargs = {}
        if fill is not None:
            kwargs['fill_value'] = fill
        vout = ncFidOut.createVariable(varname, var.datatype, new_dims, **kwargs)
        for att in var.ncattrs():
            if att != '_FillValue':
                setattr(vout, att, getattr(var, att))
        # Index out the time dimension (assumed to be first and size 1)
        time_idx = src_dims.index('time')
        slices = tuple(0 if i == time_idx else slice(None) for i in range(len(src_dims)))
        vout[:] = var[slices]

    else:
        # Variable without time: copy as-is
        fill = getattr(var, '_FillValue', None)
        kwargs = {}
        if fill is not None:
            kwargs['fill_value'] = fill
        vout = ncFidOut.createVariable(varname, var.datatype, src_dims, **kwargs)
        for att in var.ncattrs():
            if att != '_FillValue':
                setattr(vout, att, getattr(var, att))
        # Handle scalar variables (e.g., cubed_sphere grid mapping)
        if var.dimensions:
            vout[:] = var[:]
        else:
            vout.assignValue(var.getValue())

#-----------------
# Closing the files
#-----------------
ncFidOut.close()
ncFid.close()
