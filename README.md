MDF files are a common file type for engineering data, and I work extensively with them when working with Carnegie Mellon Racing. As we drive the car, we collect data which is returned as an mdf file. This contains important vehicle data like speed, steering data, accelerations, etc. In the vehicle dynamics team, we analyze this data to learn more about the car, so my app takes mdf files and places them into human-readable tables.

The app includes two tables in the schema. The signals table tracks all the collected signals alongside the timestamp signal. Each column has a signal name, and then integers/floats of the signal value for each timestep (0.5 second increments). The second table is the metadat table, which includes relevant data about the file like the name and version (depends on the mdf file)

To run the app, simply naviagte to the Streamlit link provided in my portfolio, and wake up the app. Then load an mdf file (I have included a few sample files in the github repo) and follow the on screen instructions

CRUD Operations:

Create: Use the upload button to upload a sample mdf file, then press the Process File to Database button and the SQL database will be created for you

Read: The tables are displayed in a spreadsheet like format in the app. You can maximize the window and scroll through the data

Update: Click on any cell to add a new value and then press the Save Changes to Database button

Delete: Select any cell or row to delete data. Functionality for deleting columns is not provided since the code already hides zero data columns (columns with all zeros) and in the context of what this app would be used for, deleting columns is incorrect practice.
