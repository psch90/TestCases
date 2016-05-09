#!/usr/bin/python
# =========================================================================
"""
*       Filename:  testsystem.py
*    Description:  The worker fetches FeatureRequests out of the database
*                  and exectues them. The results will record in the database.
*                  After a FeatureRequest is executed, the worker terminates
*                  and has to be restarted. There should constantly run 
*                  several worker instances.
*          Usage:  > worker.py -debug (optional)
*        Created:  Mon Oct  5 12:06:48 2015
*         Author:  (2015-2016), Dr. Michael Kreim michael.kreim@da-cons.de
*                  (2015-2016), Pascal Schuler   pascal.schuler@da-cons.de
*        Company:  da-cons GmbH, http://www.da-cons.de/
*        Contact:  support@da-cons.de"""
# =========================================================================

# Imports -{{{-------------------------------------------------------------
import sys
import mysql.connector
import time
import git
import smtplib


#-}}}----------------------------------------------------------------------

# functions -{{{-----------------------------------------------------------
def getConnection():
    try:
        connection = mysql.connector.connect(host = 'localhost', user = 'root', passwd = 'dumitri', db = 'testsystem')
    except:
        print ("ERROR: No connection to server! Aborting...")
        sys.exit(-1)
    return connection
#-}}}----------------------------------------------------------------------

# Main -{{{----------------------------------------------------------------
def main(argv):
    repo = git.Repo( 'C:/Users/Pascal/Documents/GitHub' )
    repo.git.status()
    
    #g = git.Git('C:/Users/Pascal/Documents/GitHub')
    #g = git.cmd.Git(git_dir)
    #g = repo.remotes.origin
    #g.pull()
    print("ge")
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM Testsystem")
    testIDs = str (cursor.fetchall()).replace("[(","").replace(")]","").replace(" ","").replace(",","")
    print(testIDs)
    splitTestIDs = testIDs.split(")(")
    
    for testID in splitTestIDs:
        print(testID)
        cursor.execute("SELECT predecessorID FROM Testsystem WHERE id = " + testID)
        predecessorID = str (cursor.fetchone()[0])
        cursor.execute("SELECT returnValue FROM Testsystem WHERE id = " + predecessorID)
        preReturnValue = str(cursor.fetchall()[0]).replace("(","").replace(")","").replace(",","")
        print(preReturnValue)
        returnValue=0
        if int(preReturnValue) > 0:
            returnValue = '1'
            output = "Not executable"
            print("UPDATE Testsystem SET returnValue = " + returnValue + " AND output = '" + output + "' WHERE Id = " + testID)
            cursor.execute("UPDATE Testsystem SET returnValue = " + returnValue + ", output = '" + output + "' WHERE Id = " + testID)
            connection.commit()
        else:
            if int(returnValue) > 0:
                returnValue = '1'
                print ("error")
                lastUser = "psch"
                processingDate = '2015-06-05'
                output = "error"
                testDate = time.strftime('%Y-%m-%d', time.localtime())
                print(testDate)
                cursor.execute("UPDATE Testsystem SET returnValue = " + returnValue + ", output = '" + output + "', lastUser = '" + lastUser + "', testDate = '" + testDate + "', processingDate = '" + processingDate + "'WHERE ID = " + testID)
                connection.commit()
            elif int(returnValue) == 0:
                print("no error")
                returnValue = '0' #correct to 0
                output = ''
                lastUser = ''
                processingDate = ''
                testDate = time.strftime('%Y-%m-%d', time.localtime())
                cursor.execute("UPDATE Testsystem SET returnValue = '" + returnValue + "', output = null, lastUser = null, testDate = '" + testDate + "', processingDate = null WHERE ID = " + testID)
                connection.commit()
    cursor.execute("SELECT count(*) FROM Testsystem WHERE returnValue > 0")
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
        cursor.execute("SELECT test, id, lastUser, processingDate, output FROM Testsystem WHERE returnValue > 0")
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

