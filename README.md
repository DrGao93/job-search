# job-search
An OSX tool to help widen your job search net!

## Description
This is a tool limited OSX users because of it's dependancy on chrome-cli (which is only available for OSX as of now.) This tool allows you to perform __quick and efficient x-ray search__ for fresh jobs based on your search preference.

#### What is X-ray/Boolean search?
- X-ray search is a method that is used to locate highly relevant precise results from specific websites [source](https://resources.workable.com/hr-terms/what-is-google-x-ray-search)
- The following example shows an X-ray search phrase that looks for backend engineering jobs on lever that are for juniors or new grad engineers:
_Example:_ `site:jobs.lever.co backend engineer -intitle:senior -intitle:sr`

## How does this work?
- Once you setup the local database and command line tools correctly, you can launch the script from your terminal.
- This script will first setup a connection with your local mysql database and will open the settings page on a new chrome tab.
- It will then create all possible search combinations based on your job boards preferences and your job titles preferences
> _**Example:**_
_job_titles_ = ['fullstack engineer', 'backend engineer']
_boards_ = ['jobs.lever.co', 'jobvite.com']
_ignores_ = ['sr', 'senior']
Combinations:
`site:jobs.lever.co fullstack engineer -intitle:senior -intitle:sr`
`site:jobs.lever.co backend engineer -intitle:senior -intitle:sr`
`site:jobvite.com fullstack engineer -intitle:senior -intitle:sr`
`site:jobvite.com backend engineer -intitle:senior -intitle:sr`
- Next, it will perform a google search for the first combination
> Warning: Google does tend to detect these automated searches and may show a captcha page before showing search results. If this happens, the script will pause execution until you clear the captcha. When the captcha is cleared, google proceed to perform the search you requested and the script continues execution as normal.
- Next, it will extract all 10 links from the google search results page
- Next, it will open one result from the 10 links and open it in a new tab for you
- If this job application page is invalie (and the script can detect it), it will close the job page and mark it in the database as an unavailable job page.
- If the job application page is valid, the script will pause execution and wait for you to finish applying to this job.
> Remember: This script assumes that you will be applying to any valid job page that it shows you. The moment you close the job page, it will mark it as a job link you have already applied to and will not show you that result again.
- Once you are done applying to this job, close the job application page.
- The script will then mark that job application page as a job you have already applied to and will not show you that result.
- The script will resume execution and show you the next available job. If all job links are completed, it will proceed to fetch google search results for the next combination.
- Once it has exhausted 10 jobs for each combination, it will proceed to fetch the next 10 search results for each combination in the same order.

## Getting Started
1. This tool makes use of [chrome-cli](https://github.com/prasmussen/chrome-cli#installation "Link to chrome-cli GitHub page"), so head on over to their github project page and install the tool

2. Verify the install by checking chrome-cli version using the following command
`chrome-cli version`

3. Create a MySQL database on your local machine using the following SQL query:
`CREATE TABLE unavailable_jobs (link VARCHAR(999));`
`CREATE TABLE jobs (link VARCHAR(999));`

> _**Note:**_ If you don't have SQL installed on your local machine, please read this [article on medium](https://medium.com/employbl/how-to-install-mysql-on-mac-osx-5b266cfab3b6)

4. In order to setup the script and customize your x-ray search, head over to [speedup.py](https://github.com/raj-aayush/job-search/blob/master/speedup.py#L167) and populate the 3 arrays - `job_titles`, `sites_to_search` and `ignores` with information relevant to your search. Please read the following notes to understand what information each array needs.
> _**Note:**_`job_titles`array contains a list of job titles you would like to that you would like to perform the x-ray search for. For a new-grad software engineer, the following titles might be relevant:
>> fullstack engineer
>> backend engineer
>> systems engineer
>> software developer

> _**Note:**_`sites_to_search`array contains a list of websites on which you want to perform the X-ray search. There is a default list of websites that covers a good portion of popular job boards like jobvite and lever that should provide a good starting point for most users.

> _**Note:**_`ignores`array contains a list of words that you do not want in your job title. For intance, a new grad engineer would probably not want "senior" or "sr" in their job title.

5. Navigate to project folderand enter the following command: `python speedup.py`