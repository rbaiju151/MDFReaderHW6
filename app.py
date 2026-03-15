import streamlit as st
import pandas as pd
import sqlite3
from asammdf import MDF, Signal
import io

# --- 1. Database Setup ---
@st.cache_resource
def get_db_connection():
    # Using a local file instead of in-memory so data persists between Streamlit reruns
    conn = sqlite3.connect("mdf_app.db", check_same_thread=False)
    return conn

conn = get_db_connection()

st.title("MDF to SQL Database Manager")

# --- 2. Data Ingestion (Create) ---
st.header("1. Upload MDF File")
uploaded_file = st.file_uploader("Upload a .mdf or .mf4 file", type=["mdf", "mf4"])

if uploaded_file is not None:
    # We only want to parse and insert into SQL if we haven't already
    if st.button("Process File to Database"):
        with st.spinner("Extracting data..."):
            # Load into asammdf
            file_bytes = io.BytesIO(uploaded_file.read())
            mdf = MDF(file_bytes)
            
            # Convert to Pandas DataFrame (asammdf natively supports this)
            df = mdf.to_dataframe(raster=0.5, reduce_memory_usage=True)
            # The timebase is usually the index; let's make it a standard column
            df.reset_index(inplace=True)
            df.rename(columns={'timestamps': 'Time'}, inplace=True)
            
            # Push DataFrame to SQLite (Create)
            df.to_sql("signal_data", conn, if_exists="replace", index=False)
            
            # Extract basic metadata (simplified for this example)
            meta_dict = {"File Name": uploaded_file.name, "Version": mdf.version}
            meta_df = pd.DataFrame(list(meta_dict.items()), columns=["Field", "Value"])
            meta_df.to_sql("metadata", conn, if_exists="replace", index=False)
            
            st.success("Data successfully written to SQLite!")

# --- 3. View and Edit Data (Read & Update) ---
st.header("2. View and Edit Data")

# Check if tables exist in the database before trying to read them
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)

if "signal_data" in tables['name'].values:
    st.subheader("Signal Data")
    # Read from SQLite
    df_signals = pd.read_sql("SELECT * FROM signal_data", conn)
    
    # Streamlit's data editor allows cell-level editing
    edited_signals = st.data_editor(df_signals, num_rows="dynamic", key="signal_editor")
    
    # Update SQLite if changes are saved
    if st.button("Save Signal Changes to Database"):
        edited_signals.to_sql("signal_data", conn, if_exists="replace", index=False)
        st.success("Signal database updated!")

if "metadata" in tables['name'].values:
    st.subheader("Metadata")
    df_meta = pd.read_sql("SELECT * FROM metadata", conn)
    
    edited_meta = st.data_editor(df_meta, num_rows="dynamic", key="meta_editor")
    
    if st.button("Save Metadata Changes to Database"):
        edited_meta.to_sql("metadata", conn, if_exists="replace", index=False)
        st.success("Metadata database updated!")

# --- 4. Export (Read & Package) ---
st.header("3. Export back to MDF")
if "signal_data" in tables['name'].values:
    if st.button("Generate MDF for Download"):
        with st.spinner("Packaging MDF..."):
            # Fetch latest data from SQL
            final_df = pd.read_sql("SELECT * FROM signal_data", conn)
            
            # Create a new MDF object
            new_mdf = MDF()
            time_array = final_df['Time'].values
            
            # Append each column as a signal
            signals_to_append = []
            for col in final_df.columns:
                if col != 'Time':
                    sig = Signal(
                        samples=final_df[col].values,
                        timestamps=time_array,
                        name=col
                    )
                    signals_to_append.append(sig)
            
            new_mdf.append(signals_to_append)
            
            # Save to an in-memory buffer for the download button
            mdf_buffer = io.BytesIO()
            new_mdf.save(mdf_buffer)
            mdf_buffer.seek(0)
            
            st.download_button(
                label="Download Edited MDF",
                data=mdf_buffer,
                file_name="edited_output.mdf",
                mime="application/octet-stream"
            )