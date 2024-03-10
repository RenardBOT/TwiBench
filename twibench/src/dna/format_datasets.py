import pandas as pd
import os
import sys

# Retrieving config file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
import csv


if __name__ == '__main__':
    datasets_path, datasets_list, formatted_datasets_path = Config().getDatasetsConfig()
    dna_path = os.path.join(formatted_datasets_path, "dna")

    if not os.path.exists(dna_path):
        os.makedirs(dna_path)


    for dataset in datasets_list:
        dataset_path = os.path.join(datasets_path, dataset)


        print("dataset : ", dataset)

        # -------------------------------------------------------------
        # --------------------- CRESCI-2017----------------------------
        # -------------------------------------------------------------

        if dataset == "cresci-2017":
            datasets_list = ["social_spambots_1", "social_spambots_2","social_spambots_3","genuine_accounts"]
            cresci_2017_subdatasets = os.listdir(dataset_path)

            cresci_2017_subdatasets = [subdataset for subdataset in cresci_2017_subdatasets if subdataset in datasets_list]
            
            dna_path_dataset = os.path.join(dna_path, dataset)
            for subdataset in cresci_2017_subdatasets:
                subdataset_path = os.path.join(dataset_path, subdataset)
                tweets_path = os.path.join(subdataset_path, "tweets.csv")

                dataframe = pd.read_csv(tweets_path, encoding="ISO-8859-1",low_memory=False)

                dataframe = dataframe[["text", "user_id", "in_reply_to_status_id", "retweeted_status_id", "timestamp"]]
                dataframe = dataframe.dropna(subset=["user_id"])
                dataframe["user_id"] = dataframe["user_id"].astype(float)
                dataframe["user_id"] = dataframe["user_id"].astype(int)
                
                # Add a DNA column representing the gene of the tweet.
                # - A if it is a tweet, 
                # - C if it is a reply (in_reply_to_status_id is not zero)
                # - T if it is a retweet (retweeted_status_id is not zero)
                dataframe["DNA"] = "A"
                dataframe.loc[dataframe["in_reply_to_status_id"] != 0, "DNA"] = "C"
                dataframe.loc[dataframe["retweeted_status_id"] != 0, "DNA"] = "T"

                # In a .txt file, write for each line :
                # - the user_id
                # - the DNA string (concatenation of all the DNA of the tweets of the user ordered by timestamp)
                # formatted like this : <user_id> <DNA_string>
                max_dna_length = 999
                dataframe = dataframe.groupby("user_id").agg({"DNA": lambda x: "".join(x)[:max_dna_length]})
                dataframe = dataframe.reset_index()

                # si genuine_accounts ajouter colonne label "HUMAN" sinon "BOT"
                if subdataset == "genuine_accounts":
                    dataframe["label"] = "HUMAN"
                else:
                    dataframe["label"] = "BOT"

                
                #dataframe.to_csv(os.path.join(output_path,".csv"), sep=" ", header=False, index=False)
                # write in csv file in formattd_datasets/dna/cresci-2017-<subdataset>.csv
                dna_file_path = os.path.join(dna_path, dataset +'_'+subdataset + ".csv")
                dataframe.to_csv(dna_file_path,index=False)

            