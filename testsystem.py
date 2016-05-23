#!/usr/bin/python
# =========================================================================
"""
*       Filename:  testsystem.py
*    Description:  The worker fetches FeatureRequests out of the database
*                  and exectues them. The results will record in the database.
*                  After a FeatureRequest is executed, the worker terminates
*                  and has to be restarted. There should constantly run 
*                  several worker instances.
*          Usage:  > testsystem.py
*        Created:  Do April 28 20:58:46 2016
*         Author:  (2016), Pascal Schuler   pascal.schuler@da-cons.de
*        Company:  da-cons GmbH, http://www.da-cons.de/
*        Contact:  support@da-cons.de"""
# =========================================================================

# Imports -{{{-------------------------------------------------------------
import sys
import mysql.connector
import time
#import git
import smtplib
import os
import subprocess
import stat

#-}}}----------------------------------------------------------------------

# functions -{{{-----------------------------------------------------------
def getConnection():
    try:
        connection = mysql.connector.connect(host = 'localhost', user = 'root', passwd = 'mysql', db = 'testsystem')
    except:
        print ("ERROR: No connection to server! Aborting...")
        sys.exit(-1)
    return connection
#-}}}----------------------------------------------------------------------

# Main -{{{----------------------------------------------------------------
def main(argv):
    os.chdir("/home/testsystem/TestCases")
    os.popen("git pull")
    os.chdir("/home/testsystem/CropScoreModule")
    os.chdir("git pull")
    os.chdir("/home/testsystem/TestCases")
    #os.chdir("C:\\Users\\Pascal\\Documents\\GitHub")
    
    #repo = git.Repo( 'C:/Users/Pascal/Documents/GitHub' )
    #repo.git.status()
    
    #g = git.Git('C:/Users/Pascal/Documents/GitHub')
    #g = git.cmd.Git(git_dir)
    #g = repo.remotes.origin
    #g.pull()
    print("ge")
    connection = getConnection()
    cursor = connection.cursor()
    #dirList = os.listdir('C:\\Users\\Pascal\\Documents\\GitHub\\*.py')
    dirList = os.listdir('C:\\Users\\Pascal\\Documents\\GitHub')

    dirList.sort()
    i = 300
    for sFile in dirList:
        if sFile.endswith('.py'):
            print(sFile)
            cursor.execute("SELECT COUNT(*) FROM testsystem WHERE test = '" + sFile + "'")
       
            if int(str(cursor.fetchone()[0])) == 0:
                cursor.execute("INSERT INTO testsystem(id, test,path,predecessorid) VALUES(" + str(i) + ",'" + sFile + "','C:/Users/Pascal/Documents/GitHub/" + sFile + "',0)")
                connection.commit()
                i = i + 1
    #cursor.execute("SELECT id FROM testsystem WHERE test NOT LIKE '%Compile%")
    #testIDs = str (cursor.fetchall()).replace("[(","").replace(")]","").replace(" ","").replace(",","")
    #splitTestIDs = testIDs.split(")(")
    #for testID in splitTestIDs:
        #cursor.execute("SELECT COUNT(*) FROM testsystem WHERE test LIKE" + testname + "Compiled")

        
    cursor.execute("SELECT id FROM testsystem ORDER BY predecessorid ASC")
    testIDs = str (cursor.fetchall()).replace("[(","").replace(")]","").replace(" ","").replace(",","")
    #print(testIDs)
    remainingTests = 1
    while int(remainingTests) > 0:
        cursor.execute("SELECT COUNT(*) FROM testsystem WHERE testDate != '" + time.strftime('%Y-%m-%d', time.localtime()) + "'")
        remainingTests = str (cursor.fetchall()).replace("[(","").replace(")]","").replace(" ","").replace(",","")

        splitTestIDs = testIDs.split(")(")
    
        for testID in splitTestIDs:
            #print(testID)
            cursor.execute("SELECT predecessorID FROM testsystem WHERE id = " + testID)
            predecessorID = str (cursor.fetchone()[0])
            if int(predecessorID != 0):
                cursor.execute("SELECT DATE_FORMAT(testdate, '%Y-%m-%d') FROM testsystem WHERE id= " + predecessorID)
                preTestDate = str (cursor.fetchall()).replace("[(","").replace(")]","").replace(" ","").replace(",","").replace("'","")
                cursor.execute("SELECT DATE_FORMAT(testdate, '%Y-%m-%d') FROM testsystem WHERE id= " + testID)
                testDate = str(cursor.fetchall()).replace("[(","").replace(")]","").replace(" ","").replace(",","").replace("'","")
            if ((int(predecessorID) == 0) or (preTestDate == time.strftime('%Y-%m-%d', time.localtime()))) and testDate != time.strftime('%Y-%m-%d', time.localtime()):    
                print(testID)
                print(testDate)
                #print(time.strftime('%Y-%m-%d', time.localtime()))
                preReturnValue = 0
                if int(predecessorID) > 0:
                    cursor.execute("SELECT returnValue FROM testsystem WHERE id = " + predecessorID)
                    preReturnValue = str(cursor.fetchall()[0]).replace("(","").replace(")","").replace(",","")
                print(preReturnValue)
                returnValue=0
                if int(preReturnValue) > 0:
                    returnValue = '1'
                    output = "Not executable"
                    print("UPDATE testsystem SET returnValue = " + returnValue + " AND output = '" + output + "' WHERE Id = " + testID)
                    cursor.execute("UPDATE testsystem SET returnValue = " + returnValue + ", output = '" + output + "' WHERE Id = " + testID)
                    connection.commit()
                else:
                    cursor.execute("SELECT path FROM testsystem WHERE id=" + testID)
                    path = str(cursor.fetchone()[0])
                    os.chmod(path,stat.S_IXUSR)
                    try:
                        output = subprocess.check_output([path,"/home/testsystem/TestCases/Tulips.jpg","/home/testsystem"])
                    except:
                        returnValue = subprocess.call("exit 1", shell=True)
                    if int(returnValue) > 0:
                        returnValue = '1'
                        print ("error")
                        cursor.execute("SELECT test FROM testsystem WHERE id = " + testID)
                        testname = str(cursor.fetchone()[0])
                        value = subprocess.check_output(['git', 'log',"--name-only", "--pretty=medium", testname])
                        splitValues = str(value).split("Author:")
                        #print(splitValues[1].split("Date")[0].split("<")[0])
                        lastUser = splitValues[1].split("Date")[0].split("<")[0]
                        #print(splitValues[1].split("Date")[1].split(" ")[7])
                        month = splitValues[1].split("Date")[1].split(" ")[4]
                        day = splitValues[1].split("Date")[1].split(" ")[5]
                        year = splitValues[1].split("Date")[1].split(" ")[7]
                        #processingDate = time.strftime('%Y-%m-%d', year-month-day)
                        t = (int(year), time.strptime(month,'%b').tm_mon, int(day), 0, 0, 0,0, 0, 0)
                        t = time.mktime(t)
                        processingDate = time.strftime("%b %d %Y", time.gmtime(t))
                        output = "error"
                        testDate = time.strftime('%Y-%m-%d', time.localtime())
                        #print(testDate)
                        cursor.execute("UPDATE testsystem SET returnValue = " + returnValue + ", output = '" + output + "', lastUser = '" + lastUser + "', testDate = '" + testDate + "', processingDate = '" + processingDate + "'WHERE ID = " + testID)
                        connection.commit()
                    elif int(returnValue) == 0:
                        print("no error")
                        returnValue = '0' #correct to 0
                        output = ''
                        lastUser = ''
                        processingDate = ''
                        testDate = time.strftime('%Y-%m-%d', time.localtime())
                        cursor.execute("UPDATE testsystem SET returnValue = '" + returnValue + "', output = null, lastUser = null, testDate = '" + testDate + "', processingDate = null WHERE ID = " + testID)
                        connection.commit()
    cursor.execute("SELECT count(*) FROM testsystem WHERE returnValue > 0")
    rows_count = str (cursor.fetchone()[0])
    print(rows_count)
    fromaddr = 'testsystem.CropScore@gmail.com'
    toaddrs  = '90.pascal@web.de'
    username = 'testsystem.CropScore@gmail.com'
    password = 'testsystem_da-cons'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    
    if int(rows_count) == 0:    
        msg = "\r\n".join([
      "Subject: Success!",
      "",
      "All tests were executed successfully!"
      ])
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
        print('yes')
    else:
        cursor.execute("SELECT test, id, lastUser, processingDate, output FROM testsystem WHERE returnValue > 0")
        rows = str (cursor.fetchone())
        i = 0
        message = ""
        #print(test)
          #  test = str (cursor.fetchone())
        while i < int(rows_count):
            print(rows)
            
            
        #while test is not None:
         #   print(test)
          #  test = str (cursor.fetchone())
            test = rows.split(",")[0].replace("(","").replace("'","")
            testId = rows.split(",")[1].replace("'","")
            lastUser = rows.split(",")[2].replace("'","")
            processingDate = rows.split(",")[3].replace("'","")
            output = rows.split(",")[4].replace(")","").replace("'","")
            print(test)
            print(testId)
            print(lastUser)
            print(processingDate)
            print(output)
            message = message + test + "(id: " + testId + ") lastly changed by " + lastUser + " at " + processingDate + " returned the following error message: " + output + "\n"
            rows = str (cursor.fetchone())
            i = i + 1
            
        msg = "\r\n".join([
      "Subject: Error!",
      "",
      message
      ])
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
    
#-}}}----------------------------------------------------------------------

if __name__ == '__main__': 
    main(sys.argv[1:])
    sys.exit(0)
# --- EOF -----------------------------------------------------------------

