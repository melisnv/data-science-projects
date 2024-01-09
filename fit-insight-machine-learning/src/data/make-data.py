import pandas as pd
from glob import glob

files = glob("../../data/raw/MetaMotion/*.csv")

def read_data(files):
    data_path = "../../data/raw/MetaMotion\\"
    f = files[0]

    participant = f.split("-")[0].replace(data_path,"")
    label = f.split("-")[1]
    category = f.split("-")[2].rstrip("123")

    df = pd.read_csv(f)
    df

    df["participant"] = participant
    df["label"] = label
    df["category"] = category

    acc_df = pd.DataFrame()
    gyr_df = pd.DataFrame()

    acc_set = 1
    gyr_set = 1

    for f in files:
        participant = f.split("-")[0].replace(data_path,"")
        label = f.split("-")[1]
        category = f.split("-")[2].rstrip("123").rstrip("_MetaWear_2019")
        
        df = pd.read_csv(f)
        df["participant"] = participant
        df["label"] = label
        df["category"] = category

        if "Accelerometer" in f:
            df["set"] = acc_set
            acc_set += 1
            acc_df = pd.concat([acc_df,df])
        if "Gyroscope" in f:
            df["set"] = gyr_set
            gyr_set += 1
            gyr_df = pd.concat([gyr_df,df])


    acc_df.index = pd.to_datetime(acc_df['epoch (ms)'], unit="ms")
    gyr_df.index =  pd.to_datetime(gyr_df['epoch (ms)'], unit="ms")

    acc_df = acc_df.drop(['epoch (ms)',	'time (01:00)', 'elapsed (s)'], axis=1)
    gyr_df = gyr_df.drop(['epoch (ms)',	'time (01:00)', 'elapsed (s)'], axis=1)

    return acc_df, gyr_df


acc_df, gyr_df = read_data(files=files)

merged_data = pd.concat([acc_df.iloc[:,:3], gyr_df], axis=1)
merged_data.columns = ["acc_x",
                       "acc_y",
                       "acc_z",
                       "gyr_x",
                       "gyr_y",
                       "gyr_z",
                       "participant",
                       "label",
                       "category",
                       "set"]

# Frequency Conversion

sampling = {'acc_x':'mean',
            'acc_y':'mean',
            'acc_z':'mean',
            'gyr_x':'mean',
            'gyr_y':'mean',
            'gyr_z':'mean',
            'label':'last',
            'category':'last',
            'participant':'last',
            'set':'last'}

# A Grouper allows the user to specify a groupby instruction for an object.
# freq : str / frequency object, defaults to None. This will groupby the specified frequency if the target selection (via key or level) is a datetime-like object.
days = [g for n,g in merged_data.groupby(pd.Grouper(freq="D"))]
data_sampled = pd.concat([df.resample(rule="200ms").apply(sampling).dropna() for df in days])

data_sampled["set"] = data_sampled["set"].astype("int")

# Export dataset
data_sampled.to_pickle("../../data/intermediate/01_data_processed.pkl")