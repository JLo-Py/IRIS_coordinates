# Juraj Lorincik, 2024 Feb 7

import astropy.io.fits as fits
import numpy as np

__all__ = ["sns_get_xy", "ras_get_xy"]
__version__ = "1.0"

def sns_get_xy(fpras, all_times = False):

    if not isinstance(fpras, str):
        raise ValueError('.fits not found / incorrect format')
    
    obs_desc = fits.getheader(fpras, ext = 0)['OBS_DESC']

    if obs_desc.find('sit-and-stare') == -1:
        raise Exception('The code works with sit-and-stare datasets only.')
    
    if all_times:
        print('---------------------------------------------------------------------')
        print('Returning coords. along slit for all times. This is usually obsolete.')
        print('---------------------------------------------------------------------')
    
    sat_rot = fits.getheader(fpras, ext = 0)['SAT_ROT']

    if abs(sat_rot) < 1:
        sat_rot = 0.
        
    ns = fits.getheader(fpras, ext = 1)['NAXIS2']     # No. of positions along the slit. 
    ds = fits.getheader(fpras, ext = 1)['CDELT2']     # Spatial step. 
    
    nt = fits.getheader(fpras, ext = 1)['NAXIS3']
    midind = int(nt/2)
    
    fov = ds*ns
        
    xcen = fits.getdata(fpras, ext = -2)[:,13]
    ycen = fits.getdata(fpras, ext = -2)[:,14]

    if sat_rot == 0:
        print('0° roll observation.')
        
        xcoord = xcen
        if all_times == False: ycen = ycen[midind]
        ycoord = np.linspace(ycen-fov/2+ds/2, ycen+fov/2-ds/2, ns)
            
    elif abs(sat_rot) == 90:
        print('+/- 90° roll observation.')
        
        ycoord = ycen
        if all_times == False: xcen = xcen[midind]
        xcoord = np.linspace(xcen-fov/2+ds/2, xcen+fov/2-ds/2, ns)
        
        # They need to be flipped in order to correspond to whatever IDL returns.
        # Not sure this is correct, though. 
        
        xcoord = np.flip(xcoord)        
        ycoord = np.flip(ycoord)
                
        if sat_rot == -90: 
            xcoord = np.flip(xcoord)
        
    else:   
        print(str(sat_rot)+"° roll observation. Don't forget to vstack or zip the X & Y coordinates.")
            
        angle_rad = np.radians(sat_rot)
        
        norm_offsets = np.linspace(-0.5, 0.5, ns)

        x_offset = norm_offsets * fov * np.cos(angle_rad)
        y_offset = norm_offsets * fov * np.sin(angle_rad)

        if all_times == False:
            xcen = xcen[midind]
            ycen = ycen[midind]
            xcoord = xcen + x_offset
            ycoord = ycen + y_offset
        else:      
            xcoord = np.zeros([ns, nt])
            ycoord = np.zeros([ns, nt])
            for it in range(nt):
                xcoord[:, it] = xcen[it] + x_offset
                ycoord[:, it] = ycen[it] + y_offset

        xl = xcoord[0] - xcoord[-1]
        yl = ycoord[0] - ycoord[-1]
        
        actual_length = np.sqrt(xl**2 + yl**2)      # extent of the IRIS slit in the Euclidean space
        expected_length = fov                       # real extent of the IRIS slit

        # diff = np.round((1 - expected_length/actual_length)*100, 5)
        # print('There is a '+str(diff)+'% difference between the real size of IRIS slit and the extent of the computed coordinates. ')

    return xcoord, ycoord, midind

def ras_get_xy(fpras, mid_time = True, **kwargs):
    
    # For rastrers. To be implemented in the future. 
    # I suppose different coordinates in the .fits file should be read for the code above to work?
    
    raise Exception('You have to code this you lazy fuck.')

