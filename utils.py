import json
import pandas as pd

def log(s):
    with open("./log.txt", "a") as f:
        f.write(str(s))

def read_settings_from_file(path: str):
    with open(path) as f:
        d = json.load(f)
        return d
    
def clean_up(jobs:pd.DataFrame, settings, save_as_new_file = False, save_to = None):
    excluded_titles = settings["titles_to_exclude"].lower().split(", ")
    excluded_companies = settings["companies_to_exclude"].lower().split(", ")
    jobs_to_exclude = set()
    
    for i in range(len(jobs)):
        for title in excluded_titles:
            if title in jobs.loc[i, "title"].lower(): 
                jobs_to_exclude.add(i)
                break

        
        for company in excluded_companies:
            if company in jobs.loc[i, "company"].lower(): 
                jobs_to_exclude.add(i)
                break

        # TODO: Assumptions
        
        jobs.loc[i, "description"] = str(jobs.loc[i, "description"]).replace("About the job", "").strip().lower()
        jobs.loc[i, "skills"] = str(jobs.loc[i, "skills"]).replace(";", ",").strip().lower()
    log(list(jobs_to_exclude))
    jobs.drop(labels=list(jobs_to_exclude), axis="index", inplace=True)
    jobs.reset_index(inplace=True)
    log(jobs)
    if save_as_new_file:
        jobs.to_csv(save_to, sep=',', index=False)

    return jobs
    
if __name__ == "__main__":
    settings_path = "./settings.json"
    jobs = pd.read_csv("./jobs.csv")
    settings = read_settings_from_file(settings_path)
    jobs = clean_up(jobs, settings)
    print(jobs)