# LabJack DAQ
LabJack data aquisition script in python3.

- python3 `__daq__.py` to start collecting data

   - path to LabJack must be stated in `__daq__.py`

- data archive handled by `__cache__.py`

- database backup handled by `__daq2db__.py`

The inputs to be recorded are handled by modules found in `MODULES/`. Check the module template.py to get started: it has extensive documentation, you can use it as a template. Without modification the template.py module can read two pheiffer full range gauges differentially across AIN0-1 and AIN2-3.

Outside of connecting to the labjack (`__daq__.py`) and database (`__daq2db__.py`), the modules are the only scripts that should be edited and added to. 

## Details

This document will provide a walkthrough for data acquisition with a LabJack using python3. 

TL;DR

The DAQ package connects to a LabJack over a serial/network connection, reads voltages at some interval, then writes them to a csv file. When the data file reaches a specified size, it is closed, archived, and sent to a database; a new file is opened for writing. A buffer file is also created for live viewing and online analysis; this functionality can be turned off. For the ETS, the buffer script launches a control script, which uses results from the online analysis to manage cryogen transfer.

### Walkthrough

`__daq__.py`

* open `__daq__.py`
   * NOTE: the values contained by the scanRate, chunkTime, and archTime parameters may be altered. A module must be written for each sensor suite. It should be loaded in the “add sensor module” section, and the sensor names/numbers should be specified using the “for name in module.names()” loop - the format is contained under the “usage” line. The serial number for the LabJack must be specified in the handle field. The aAddresses dictionary must be updated with values from the module – the format is contained under the “usage” line. Do not change any other values.
* `# Magic numbers` held at the top; scanRate is the rate of data acquisition, in Hz; chunkTime is the amount of data (specified by seconds) to be stored in each csv file; archTime is the amount of data to be stored in each data archive
* `# Setup environment` The environment is setup. If a directory does not exist (first run), it is created
* `# Add the sensor modules` The modules are loaded. A module contains the information about sensors and the database which, in general, will differ for each user. I.e., if three thermocouples are read at AIN0-5, then that information will be contained in a module. In the ETS DAQ script, three modules are loaded: thermocouple, level, and frg. The format for a module is standardized; see the section on modules for more information. Sensor names and identification strings must be loaded – use the ‘for loop’ for thermocouple, level, or frg as a template. The sensor names are used to poll the LabJack for voltages/values in the main loop.
    Pass values to buffer The buffer script will call the buffer_output function to retrieve parameters
   * if `__name__ == '__main__'`: The main function:
   * Connect to the labjack connect to the LabJack using the handle
   * `aAddresses, aDataTypes, aValues = {},{},{}` Add the addresses (contained in modules), you may simply copy the format specified by an existing module.
   * `for file in os.listdir(DATA):` If the DAQ script was interrupted, there will exist an incomplete file in the DATA directory – this file will be moved to the CRASH directory
   * `# Launch buffer` The buffer script is launched (not essential, can comment out)
   * `# Launch DAQ Loop` The main loop:
      * `ts[1] = dt.datetime.utcnow().timestamp()` The time is recorded
      * `filename = os.path.join(DATA,'Ljdata_%i.csv'%ts[0])` The data file is defined, using a unix timestamp as a uid
      * `if not os.path.exists(filename)`: If the data file does not exist, it is created. The header and sensor identifier are written.
      * `for strname in sensor['ident']`: For each sensor contained in the names dictionary, the voltages/values are read, and stored in results
      * `if os.path.exists(filename)`: The values contained in results are written to the data filename
      * `if (ts[1]-ts[0]) > chunkTime`: If the data file reaches the file size limit, it is passed to the `__cache__.py` script so that it may be uploaded to the database, and so that a copy may be compressed and archived locally
      * `if (scanTime-procTime) > 0`: If the loop completes faster than the specified data collection rate, wait.

`__cache__.py`

* open `__cache__.py`
   * NOTE: this script should not be altered
* `import __dbfilter__ as dbfilter` The database deadtime filter is loaded. This module is used to reduce the data if ‘nothing interesting’ is happening: for a data file, if the values do not change a sufficient amount, all values are averaged over the data file period, and that single line is uploaded to the database. The dbfilter also contains the path to the database.
* `# Try to send data to the DB import the daq2db module`. Create a new data file by processing the old data file using the dbfilter script. Upload the new data file to the database. If the data is changing a sufficient amount, the new data file will be a copy of the old data file; otherwise the new data file is a single value for each sensor.
* `# Archive the data` Compress the old data file, and send it to the archive.
* `# Cleanup Remove` the old data file and the new data file from the DATA directory

`__dbfilter__.py`

* open `__dbfilter__.py`
   * NOTE: only the string contained within the dbname() function, and the skew/gskew parameters should be altered
* `def dbname():` Specify the name of the database – this name is called by the cache script, and passed to the daq2db script
* `def condition(sensor,time):` This function uses the mean and median of the data, and the gradient of the data, to determine if it is changing sufficiently. The skew and gskew parameters are used to determine if the transient condition is true. The values of skew and gskew will vary based on the apparatus – they should be tuned with real data collected during a transient and stationary period. If any field is determined to be transient, the parameter k increments by 1.
*  `def deadtime(filename):` if k > 0, the new data file is a copy of the old data file. If k = 0, the data is stationary, and the new data file is the average of the old data file.

`__dbmodule__.py`

* Written by Tessa for interfacing with the couchdb database.  

`__buffer__.py`

* This script opens a buffer, and provides online data analysis used to automate the cryogen supply. The analysis is specific to the ETS system, however, omitting the gradient and __autovalve__.py script will make this script run as a regular buffer, with data averaged under a specific interval.

`__valve__.py`

* This script connects to a relay that manages the state of a solenoid valve. Requires manual input.

`__autovalve__.py`

* The cryogen automation script – looks for a power decrease in the cryostat (cold finger no longer engaged), then opens the valve. When the dewar is filled, the cryogen will flow over the overfill sensor, and the valve will close.


