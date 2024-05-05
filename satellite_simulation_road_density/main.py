import spacetrack
from skyfield.api import load
from skyfield.api import EarthSatellite
import numpy as np
import math
import spacetrack.operators as op
import datetime
import pytz
import tifffile as tiff
import tqdm
import math

# Specify the address of the road density image
road_density_filepath='./grip4_area_land_km2_georeference.tif'

# Create a SpaceTrack instance
username='insert_your_user_email'
pwd='insert_your_pwd'

space_track = spacetrack.SpaceTrackClient(identity=username, password=pwd)

def get_sat_tracks(norad_id,start_date,end_date):
    
    # Get the TLE for a satellite with NORAD ID 25544 between Feb1 and Feb8      
    ST_epoch = op.inclusive_range(start_date,end_date)
    tle = space_track.tle(norad_cat_id=norad_id, epoch=ST_epoch)

    # Parse TLE
    ts = load.timescale()
    line1, line2 = tle[0]['TLE_LINE1'],tle[0]['TLE_LINE2']
    satellite = EarthSatellite(line1, line2, 'Sat', ts)

    t0 = ts.utc(int(start_date.split('-')[0]), int(start_date.split('-')[1]), int(start_date.split('-')[2]),0,0,0)
    t1 = ts.utc(int(end_date.split('-')[0]), int(end_date.split('-')[1]), int(end_date.split('-')[2]),0,0,0)

    DT=time_diff_in_seconds(t0, t1)
    tstep_needed=1
    tsd = ts.linspace(t0, t1, int(DT/tstep_needed))    
    
    positions = satellite.at(tsd)        #.position.km
    positions = positions.subpoint()    
    longitudes,latitudes=positions.longitude.degrees,positions.latitude.degrees    
    local_times = []

    for idx in range(tsd.shape[0]):    
        
        t=tsd[idx].utc_datetime()        
        # Create EarthSatellite object for subsatellite point calculation
        longitude = longitudes[idx]
        # subsatellite_temp = satellite
        # Calculate local times for each time step
        local_time = calculate_local_time(t, longitude)
        # print(t,longitude)
        local_times.append(local_time)
    
    return longitudes, latitudes, local_times

# given the current utc time and a local point ( latitude, longitude ), write a function to calculate current local time at the local time by taking a longitude difference
def calculate_local_time(utc_time, longitude_difference):
  
  # Get the UTC timezone
  utc_timezone = utc_time
  # Convert the UTC time to a timezone-aware datetime object
  utc_time_aware = utc_timezone
  # Calculate the offset in hours from the longitude difference
  offset_hours = longitude_difference / 15
  # Create a timezone object for the local point
  local_timezone = pytz.FixedOffset(offset_hours * 60)
  # Convert the UTC time to the local time
  local_time = utc_time_aware.astimezone(local_timezone)

  return local_time

# Propagate satellite position
def time_diff_in_seconds(time1, time2):
  # Convert both time objects to Unix timestamps
  unix_time1 = time1.utc_datetime().timestamp()
  unix_time2 = time2.utc_datetime().timestamp()
  # Calculate the difference in seconds
  difference = unix_time2 - unix_time1
  return difference

im=tiff.imread(road_density_filepath)
im_revisits=np.zeros((im.shape[0],im.shape[1])).astype('uint16')
deg2px=0.08333
local_time_distibution=[]

# Planet sat list
case_number_list=[1,2,3,4]

# Source: Union of Concerned Scientists Database
norad_id_list=[55039,55029,55043,55065,55079,55024,55068,55040,55031,55023,55026,55074,55063,55077,55022,55080,55020,55027,55070,55083,55033,55030,55035,55025,55075,55021,55042,55082,55057,55078,55055,55028,55066,55032,55071,55069,51017,51037,51049,51015,51028,51066,51010,51020,51035,51007,51046,50996,50997,51040,51003,51056,51016,51026,51045,51011,51006,51000,51041,51024,51042,51048,51039,51009,51023,51029,51064,51052,51005,51018,51027,50993,51004,51043,51065,50992,51047]

for case_number in case_number_list:

   # Case numbers help run the simulation in chunks such that a 48GB memory machine supports it
   if case_number==1:
      norad_id_list=norad_id_list[0:41]
      start_date,end_date = '2024-02-01','2024-02-15'
   elif case_number==2:
      norad_id_list=norad_id_list[0:41]
      start_date,end_date = '2024-02-15','2024-03-02'
   elif case_number==3:
      norad_id_list=norad_id_list[41:]
      start_date,end_date = '2024-02-01','2024-02-15'
   elif case_number==4:
      norad_id_list=norad_id_list[41:]
      start_date,end_date = '2024-02-15','2024-03-02'


   for norad_id in tqdm.tqdm(norad_id_list):    
      
      longitudes, latitudes, local_times=get_sat_tracks(norad_id,start_date,end_date)
      for idx,longitude in enumerate(longitudes):       

         latitude=latitudes[idx]
         local_time_HH=int(local_times[idx].strftime('%H'))
         y,x=(math.floor((longitude+180)/deg2px)-1),(math.floor((90-latitude)/deg2px)-1)

         if (local_time_HH>8 & local_time_HH<17) & (im[x,y]>10):
            im_revisits[x,y]=im_revisits[x,y]+1
            local_time_distibution.append(local_time_HH)


   tiff.imwrite('revisits{}.tif'.format(case_number),im_revisits)

