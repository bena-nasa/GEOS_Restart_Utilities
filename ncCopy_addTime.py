#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import argparse

def parse_args():
    p = argparse.ArgumentParser(description='Add time dimension to variables in a NetCDF file')
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
# Detect file type and set exclude list
#---------------------
isCubedSphere = 'nf' in ncFid.dimensions

if isCubedSphere:
    Exclude_Var = ['Xdim', 'Ydim', 'nf', 'ncontact', 'cubed_sphere',
                   'lons', 'lats', 'contacts', 'orientation', 'anchor',
                   'lev', 'time']
else:
    Exclude_Var = ['lon', 'lat', 'time', 'lev']

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
        ncFidOut.createDimension(dimname, len(dim))

#---------------------
# Copy all variables
#---------------------
for varname, var in ncFid.variables.items():
    src_dims = var.dimensions
    fill = getattr(var, '_FillValue', None)
    kwargs = {}
    if fill is not None:
        kwargs['fill_value'] = fill

    if varname in Exclude_Var:
        # Copy variable as-is (no time added)
        vout = ncFidOut.createVariable(varname, var.datatype, src_dims, **kwargs)
        for att in var.ncattrs():
            if att != '_FillValue':
                setattr(vout, att, getattr(var, att))
        if varname == 'time':
            vout[:] = 0
        elif var.dimensions:
            vout[:] = var[:]
        else:
            # Scalar variable (e.g., cubed_sphere)
            vout.assignValue(var.getValue())
    else:
        # Data variable: prepend time dimension
        new_dims = ('time',) + src_dims
        vout = ncFidOut.createVariable(varname, var.datatype, new_dims, **kwargs)
        for att in var.ncattrs():
            if att != '_FillValue':
                setattr(vout, att, getattr(var, att))
        vout[0, ...] = var[:]

#-----------------
# Closing the files
#-----------------
ncFidOut.close()
ncFid.close()
