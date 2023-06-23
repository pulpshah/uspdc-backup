import os
import datetime
import pandas as pd

def pickle(*dfs):
    # Get current date and time
    now = datetime.datetime.now()
    
    # Create the outer directory name based on current month and day
    outer_dir_name = now.strftime("%m_%d")
    outer_dir_path = os.path.join("scored_debates", outer_dir_name)
    
    # Create the directory if it doesn't already exist
    os.makedirs(outer_dir_path, exist_ok=True)
    
    for df in dfs:
        # Get the name of the dataframe
        df_name = [k for k,v in globals().items() if v is df][0]
        
        # Create the filename based on the dataframe name and current time
        file_name = df_name + "_" + now.strftime("%I_%M") + '.pkl'
        
        # Full file path
        file_path = os.path.join(outer_dir_path, file_name)
        
        # Save dataframe as pickle file
        df.to_pickle(file_path)
        
    print("Dataframes saved successfully")
