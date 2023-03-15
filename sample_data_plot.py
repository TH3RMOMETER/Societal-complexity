import matplotlib.pyplot as plt
import netCDF4
import numpy as np
from pylab import *
from scipy.io import *

# Open the netcdf file
a = netCDF4.Dataset('openmars_my28_ls109_my28_ls124.nc','r')

# Pull out the necessary arrays of data
lats = a.variables['lat'][:]  # Latitude
lons = a.variables['lon'][:]  # Longitude
ps = a.variables['ps'][:]     # Surface pressure

# Plot the first timestep of this datafile
fig = plt.figure()
CS1=plt.contourf(lons,lats,ps[0,:,:],30,cmap = plt.cm.jet)
cbar = plt.colorbar(CS1)
cbar.set_label('Surface pressure / Pa',fontsize=20)
for t in cbar.ax.get_yticklabels():
      t.set_fontsize(18)
plt.xticks( arange(-135,180,45), ('135$^\circ$W','90$^\circ$W','45$^\circ$W','0$^\circ$','45$^\circ$E','90$^\circ$E','135$^\circ$E'),fontsize=16 )
plt.xlabel(r'Longitude',fontsize=18)
plt.yticks( arange(-60,90,30), ('60$^\circ$S','30$^\circ$S','0$^\circ$','30$^\circ$N','60$^\circ$N'),fontsize=16  )
plt.ylabel('Latitude',fontsize=18)
plt.axis([-180., 175.,-87.5,87.5])
# Set size of the figure and then write to a PNG file
fig.set_size_inches(14, 8)
plt.savefig('my24_ls267_ps.png',dpi=200,bbox_inches='tight',pad_inches = 0.3)
plt.close()
