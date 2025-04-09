import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters, \
    OnSiteOrRemoteFilters, SalaryBaseFilters
import csv
import os

# !!!Run 'pip install linkedin-jobs-scraper' first!!!
# Parser: https://github.com/spinlud/py-linkedin-jobs-scraper?tab=readme-ov-file
# !!!For the best performance use 'LI_AT_COOKIE=<cookie token> python3 parsing.py' to run. This allows authorisation.!!!
# to obtain '<cookie token>' look in github repository above

save_to = 'jobs.csv'

if os.path.exists(save_to):
  os.remove(save_to)

with open(save_to, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["title", "company", "date", "link", "skills", "description"])


    # Change root logger level (default is WARN)
    logging.basicConfig(level=logging.INFO)


    # Fired once for each successfully processed job
    def on_data(data: EventData):
        dirty = [data.title, data.company, data.date, data.link]
        for i in range(len(dirty)):
            dirty[i] = str(dirty[i]).replace("\n", "").replace(",", "")
        _job_description = [str(data.skills).replace(",", ";"), data.description.strip().replace("\n", "")]
        _job = dirty + _job_description
        writer.writerow(_job)


    # Fired once for each page (25 jobs)
    def on_metrics(metrics: EventMetrics):
        print('[ON_METRICS]', str(metrics))


    def on_error(error):
        print('[ON_ERROR]', error)


    def on_end():
        print('[ON_END]')


    scraper = LinkedinScraper(
        chrome_executable_path=None,  # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
        chrome_binary_location=None,  # Custom path to Chrome/Chromium binary (e.g. /foo/bar/chrome-mac/Chromium.app/Contents/MacOS/Chromium)
        chrome_options=None,  # Custom Chrome options here
        headless=True,  # Overrides headless mode only if chrome_options is None
        max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
        slow_mo=0.5,  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
        page_load_timeout=40  # Page load timeout (in seconds)    
    )

    # Add event listeners
    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)

    queries = [
        Query(
            query='Machine Learning',
            options=QueryOptions(
                locations=['Austria', 'Germany', 'Switzerland'],
                apply_link=False,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
                skip_promoted_jobs=True,  # Skip promoted jobs. Default to False.
                limit=300,
                filters=QueryFilters(
                    relevance=RelevanceFilters.RECENT,
                    time=TimeFilters.ANY,
                    type=[TypeFilters.INTERNSHIP, TypeFilters.FULL_TIME, TypeFilters.PART_TIME],
                    on_site_or_remote=[OnSiteOrRemoteFilters.ON_SITE, OnSiteOrRemoteFilters.HYBRID, OnSiteOrRemoteFilters.REMOTE]
                    # experience=[ExperienceLevelFilters.MID_SENIOR]
                )
            )
        ),
    ]

    scraper.run(queries)
