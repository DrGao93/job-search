import subprocess
import time
import mysql.connector
import signal

'''
> Create all search combinations using boards x titles + ignores
> Use chrome-cli to lookup one combination on google
    While 1:
        Grab links from all search results on page
        While links are present:
            If company name/link is not in db:
                Open one link
                Record process number
                While process is present in list of open chrome tabs:
                    Sleep for x seconds
                Enter company name and URL in db
    
'''

def waitForPageToLoad(pageId):
    # Check status of page
    cmd = subprocess.Popen(['chrome-cli', 'info', '-t', str(pageId)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout,_ = cmd.communicate()

    # While page is Not loaded
    while stdout.decode('utf-8').split('\n')[3][9:] != "No":
        time.sleep(1)
        # Check status of page
        cmd = subprocess.Popen(['chrome-cli', 'info', '-t', str(pageId)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,_ = cmd.communicate()
    # print("Loaded page ID:", str(pageId))
    return

def waitForPageToClose(pageId):
    # Check status of page
    cmd = subprocess.Popen(['chrome-cli', 'info', '-t', str(pageId)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout,_ = cmd.communicate()

    # While page is not closed
    while stdout.decode('utf-8') != '':
        time.sleep(1)
        # Check status of page
        cmd = subprocess.Popen(['chrome-cli', 'info', '-t', str(pageId)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,_ = cmd.communicate()
    # print("User closed page ID:", str(pageId))
    return

def openChromePage(url, newTab=False):
    if newTab:
        cmd = subprocess.Popen(['chrome-cli', 'open', url, '-n'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        cmd = subprocess.Popen(['chrome-cli', 'open', url], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = cmd.communicate()
    return stdout, stderr,int(stdout.decode('utf-8').split('\n', 1)[0][4:])

def closeChromePage(pageId):
    cmd = subprocess.Popen(['chrome-cli', 'close', '-t', str(pageId)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return cmd.communicate()

def handlePotentialCaptchaForm(pageId):
    # If a captcha shows up on your google search page, this function will pause execution
    # It will check every 5 seconds if the captcha was completed by the user or not.
    stdout = subprocess.check_output(['chrome-cli', 'execute', '(function() { if(document.querySelector("#captcha-form") != null){ return "Captcha on Page"; } else{ return "No Captcha"; } })();', '-t', str(pageId)])
    output = stdout.decode('utf-8')[:-1]
    while output == "Captcha on Page":
        time.sleep(5) # Wait for 5 seconds while user solves google captcha
        stdout = subprocess.check_output(['chrome-cli', 'execute', '(function() { if(document.querySelector("#captcha-form") != null){ return "Captcha on Page"; } else{ return "No Captcha"; } })();', '-t', str(pageId)])
        output = stdout.decode('utf-8')[:-1]
    return

def jobIsAvailable(query, jobPageId):
    # Check if job page clearly says that the job is not available
    if "hire.withgoogle.com" in query:
        stdout = subprocess.check_output(['chrome-cli', 'execute', '(function() { if(document.querySelector("body>div>div").querySelector("h1") == null){ return "Job Available"; } else{ return "Job Not available"; } })();', '-t', str(jobPageId)])
        output = stdout.decode('utf-8')[:-1]
        if output == "Job Not available":
            print("Job is not available")
            return False
    elif "jobs.lever.co" in query:
        stdout = subprocess.check_output(['chrome-cli', 'execute', '(function() { return document.querySelector("title").innerHTML; })();', '-t', str(jobPageId)])
        output = stdout.decode('utf-8')[:-1]
        if output == "Not found –&nbsp;404 error":
            print("Job is not available")
            return False
    elif "boards.greenhouse.io" in query:
        stdout = subprocess.check_output(['chrome-cli', 'execute', '(function() { var popup = document.querySelector("#flash_pending"); if( popup != null && popup.innerHTML == "The job you are looking for is no longer open."){ return "Job is not available" } else{ return "Job is available"} })();', '-t', str(jobPageId)])
        output = stdout.decode('utf-8')[:-1]
        if output == "Job is not available":
            print("Job is not available")
            return False
    elif "jobvite.com" in query:
        stdout = subprocess.check_output(['chrome-cli', 'execute', '(function() { var popup = document.querySelectorAll(".jv-page-error-header")[0]; if( popup != null && popup.innerText == "The job listing no longer exists."){ return "Job is not available" } else{ return "Job is available"} })();', '-t', str(jobPageId)])
        output = stdout.decode('utf-8')[:-1]
        if output == "Job is not available":
            print("Job is not available")
            return False
    elif "workable.com" in query:
        stdout = subprocess.check_output(['chrome-cli', 'execute', '(function() { return window.location.href; })();', '-t', str(jobPageId)])
        output = stdout.decode('utf-8')[:-1]
        if "not_found=true" in output:
            print("Job is not available")
            return False
    elif "smartrecruiters.com" in query:
        stdout = subprocess.check_output(['chrome-cli', 'execute', '(function() { var popup = document.querySelector("#st-apply"); if( popup != null && popup.innerHTML == "Sorry, this job has expired"){ return "Job is not available" } else{ return "Job is available"} })();', '-t', str(jobPageId)])
        output = stdout.decode('utf-8')[:-1]
        if "Job is not available" in output:
            print("Job is not available")
            return False
        
    return True

def jobLinkIsNew(db, dbCursor, url):
    # Check if the job link found through google X-ray search is new or not
    cursor = db.cursor()
    cursor.execute('SELECT link FROM jobs WHERE link="'+url+'";')
    row = cursor.fetchone()
    cursor.close()
    cursor = db.cursor()
    if row == None:
        cursor.execute('SELECT link FROM unavailable_jobs WHERE link="'+url+'";')
        unavail_row = cursor.fetchone()
        cursor.close()
        if unavail_row == None:
            return True
    return False

def dbInsert(db, dbCursor, table, link):
    # Insert into database
    insertStmt = 'INSERT INTO '+table+' (link) VALUES ("'+link+'")'
    dbCursor.execute(insertStmt)
    db.commit()

def getGoogleSearchResultList(pageId):
    # Get google search results for X-ray search
    return subprocess.check_output(['chrome-cli', 'execute', getGoogleSearchResultExtractorJS(), '-t', str(pageId)]).split()

'''
> JS function to parse a google search results page and return all links found in it
    Used on shell like: chrome-cli execute <fn>
    Output:
        Type: str
        Format: jobvite.com/tesla/software-engineer\n
                lever.co/microsoft/product-manager\n
                jobvite.com/tesla/product-manager\n
'''
def getGoogleSearchResultExtractorJS():
    # Return js function string that extracts search results from google
    s = '(function() { '
    s +=     'console.log("Starting fn"); '
    s +=     'var nodes = document.querySelectorAll("#search>div>div>div.g"); '
    s +=     'console.log("Starting loop"); '
    s +=     'var titles = []; '
    s +=     'for (var i = 0; i < nodes.length ; i++) {'
    s +=         'if(nodes[i].classList.contains("g-blk")){continue;} '
    s +=         'console.log("Grabbing Link"); '
    s +=         'titles.push(nodes[i].querySelector("div.rc>div.r>a")); '
    s +=         'console.log("Grabbed Link"); '
    s +=     '} '
    s +=     'return titles.join("\\n"); '
    s += '})();'

    return s

def main():

    boards = [
        "site:hire.withgoogle.com",
        "site:jobs.lever.co",
        "site:boards.greenhouse.io",
        "site:jobvite.com",
        "site:workable.com -site:resources.workable.com",
        "site:jobs.smartrecruiters.com"
    ]

    titles = []

    # Ignore job pages which have the following keywords in their title (generally also their position description)
    ignores = [
        "sr",
        "senior",
        "principal"
    ]

    # Setup connect to local SQL database
    mySQLDB = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="job_applications"
    )

    cursor = mySQLDB.cursor()

    def keyBoardInterrupt(signal, frame):
        print("\nRecieved keyboard interrupt.\nClosing DB connection...")
        mySQLDB.close()
        exit(0)

    signal.signal(signal.SIGINT, keyBoardInterrupt)

    # Open the chrome settings page in a new window. This new window will be where all job applications will open up
    print("Opening new Tab for session")
    stdout, stderr, sessionId = openChromePage('chrome://settings', newTab=True)

    # Make a list of all google queries using job boards info and titles info
    baseSearch = "https://www.google.com/search?q="
    queries = []
    for board in boards:
        query = baseSearch + '+'.join(board.split(' '))
        query += '+-intitle:' + '+-intitle:'.join(ignores)
        for title in titles:
            temp = query + '+' + '+'.join(title.split(' '))
            queries.append(temp)

    # Load results in increments of 10 for each google query
    for pageIncrement in range(100):
        # Go over each google query in a for loop
        for query in queries:
            # Open google query link
            stdout, stderr, queryPageId = openChromePage(query+'&start='+str(pageIncrement*10))
            waitForPageToLoad(queryPageId)
            handlePotentialCaptchaForm(queryPageId)
            print(query)
            for job in getGoogleSearchResultList(queryPageId):
                if jobLinkIsNew(mySQLDB, cursor, job.decode('utf-8')):
                    stdout,stderr,jobPageId = openChromePage(job)
                    waitForPageToLoad(jobPageId)
                    if jobIsAvailable(query, jobPageId):
                        waitForPageToClose(jobPageId)
                        dbInsert(mySQLDB, cursor, 'jobs', job.decode('utf-8'))
                    else:
                        dbInsert(mySQLDB, cursor, 'unavailable_jobs', job.decode('utf-8'))
                        closeChromePage(jobPageId)
            # Done with 10 jobs for position x from job board y, moving to next job board
            # Close current google search query page and open a new query page with different lookup
            stdout,stderr = closeChromePage(queryPageId)
    return

main()