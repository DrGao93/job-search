# job-search
An OSX tool to help widen your job search net!

## Description
This is a tool limited OSX users because of it's dependancy on chrome-cli (which is only available for OSX as of now.) This tool allows you to perform __quick and efficient x-ray search__ for fresh jobs based on your search preference.


## Getting Started
1. This tool makes use of [chrome-cli](https://github.com/prasmussen/chrome-cli#installation "Link to chrome-cli GitHub page"), so head on over to their github project page and install the tool

2. Verify the install by checking chrome-cli version using the following command
`chrome-cli version`

3. Create a MySQL database on your local machine using the following SQL query:
`CREATE TABLE unavailable_jobs (link VARCHAR(999));`
`CREATE TABLE jobs (link VARCHAR(999));`

> _**Note:**_ If you don't have SQL installed on your local machine, please read this [article on medium](https://medium.com/employbl/how-to-install-mysql-on-mac-osx-5b266cfab3b6)

4. In order to setup the script and customize your x-ray search, head over to [speedup.py]() and populate the 3 arrays - `job_titles`, `sites_to_search` and `ignores` with information relevant to your search. Please read the following notes to understand what information each array needs.
> _**Note:**_`job_titles`array contains a list of job titles you would like to that you would like to perform the x-ray search for. For a new-grad software engineer, the following titles might be relevant:
>> fullstack engineer
>> backend engineer
>> systems engineer
>> software developer

> _**Note:**_`sites_to_search`array contains a list of websites on which you want to perform the X-ray search. There is a default list of websites that covers a good portion of popular job boards like jobvite and lever that should provide a good starting point for most users.

> _**Note:**_`ignores`array contains a list of words that you do not want in your job title. For intance, a new grad engineer would probably not want "senior" or "sr" in their job title.

5. Navigate to project folderand enter the following command: `python speedup.py`