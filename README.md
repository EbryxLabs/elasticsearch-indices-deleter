# What is it
Hint's in the name. It's simple script that is capable of deleting Elasticsearch indices based on the creation_date meta data of the index. 

# What problem it solves 
No more hassle to cater for index patterns like my_index_pattern-yyyy-mm-dd or gazillion others or anything

# How it does it
- Fetches a list of indices from Elasticsearch
- Checks whether some name string defined it config file is contained in the fetched indices list from ES
- Once name is matched, it fetches index settings from Elasticsearch
- Based on index settings parameter `creation_date`, which defines the creation date of index, script determines the age of index
- If age is more than allowed max age for that string/index pattern, index is deleted


# How to use it
- Linux command line:
  ```
  python3 /path/to/elasticsearch-indices-deleter.py --config /path/to/config/file
  ```
- Set the above mentioned command as a cron job and voila
- Can also be used from Lambda but lambda package would need to be created for that
- Check the shared sample config file. Keys defined in JSON config are self explanatory


## Config file
  ```
  {
        "ES_IP": "IP of ES",
        "ES_PORT": "Port of ES",
        "indices_to_delete": {
                "mention_index_name_that_is_to_be deleted_here": max_age_of_index_in_days
        }
  }
  ```

- Consider we have several indices:
  - index1-yyyy-mm-dd
  - index2
  - index3-dd-mm-yyyy
  - some-index
  
- Now Dictionary keys under **'indices_to_delete'** can be like:
  - **"index": 5** === This will delete all indices that contain word "index" and index was created more than 5 days ago
  - **"index1": 6** === This will delete all indices that contain word "index1" and index was created more than 6 days ago
  - **"some": 10** === This will delete all indices that contain word "some" and index was created more than 10 days ago