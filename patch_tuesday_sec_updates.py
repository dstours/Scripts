#!/usr/bin/env python
import csv
from datetime import datetime, date
import datetime
import calendar
from itertools import izip
import pandas as pd
import json
import os
import requests
import traceback
import smtplib
import mimetypes
import sys
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def main():
    #Set dates as variables
    today = datetime.datetime.now()
    today_formatted = today.strftime("%-m/%d/%Y")
    current_month = date.today().month
    current_year = date.today().year

    #Determine patch Tuesday and format how the json data displays it.
    second_tuesday = calendar.Calendar(1).monthdatescalendar(current_year,current_month)[2][0]
    second_tuesday_formatted = datetime.datetime.strptime(str(second_tuesday), '%Y-%m-%d').strftime('%-m/%d/%Y')
    second_tuesday_ymd = datetime.datetime.strptime(str(second_tuesday), '%Y-%m-%d').strftime('%Y%m%d')

    if today_formatted == second_tuesday_formatted:


        #Pull Patch Tuesday from Microsoft json and write to formatted_patches.csv.
        f = csv.writer(open("formatted_patches.csv", "wb+"))
        f.writerow(['Date', 'Bulletin Number', 'KB Number', 'Title', 'Bulletin Rating'])

        conn = requests.get('https://technet.microsoft.com/security/bulletin/services/GetBulletins?searchText=&sortField=0&sortOrder=1&currentPage=1&bulletinsPerPage=100&locale=en-us')
        if conn.status_code == 200:
            parsed_json = json.loads(conn.text)
            for listitem in parsed_json['b']:
                j_date =  listitem['d']
                j_bulletin = listitem['Id']
                j_kb = listitem['KB']
                j_title = listitem['Title']
                j_rating = listitem['Rating']

                f.writerow([j_date,
                            j_bulletin,
                            j_kb,
                            j_title,
                            j_rating])
        else:
            print 'Fetch from Microsoft Technet failed'

        #Create dictionary from formatted_patches.csv so we can filter patches relevant to the current patch Tuesday.
        a_patches = {}
        reader = csv.reader(open("formatted_patches.csv", "rU"))
        for i, rows in enumerate(reader):
            if i == 0: continue
            k = rows[0]
            v = rows[1:]
            if not k in a_patches:
                a_patches[k] = [v]
            else:
                a_patches[k].append(v)

        for key, value in a_patches.items():
             if value != a_patches[second_tuesday_formatted]:
                 a_patches.pop(key)

        #Create a new dictionary based on the formatted data from above. We will also store the data in headers we define in the CSV.     
        f_patches = []
        f_headers = ['Date', 'Bulletin Number', 'KB Number', 'Title', 'Bulletin Rating']

        for key, value in a_patches.iteritems():
            for entry in value:
                f_patches.append([key] + entry)

        #Write formatted data to a new csv named yyyyMMddpatches.csv 
        df_out = pd.DataFrame(f_patches, columns=f_headers)
        df_out.to_csv(second_tuesday_ymd + 'patches.csv', index=False)

        #format CSV to Jira Markdown and store output.txt as variable 'data'
        infile = second_tuesday_ymd + 'patches.csv'
        outfile = 'output.txt'

        outf = None
        try:
            # The count is for changing the format for Headers
            count = 0
            outf = open(outfile, 'w')

            with open(infile, 'r') as inf:
                for line in inf:
                    # If count is 0, it's the Header
                    if count == 0:
                        tmp = '||' + line.strip().replace(',', '||') + '||'
                        outf.write(tmp + '\n')
                        
                        # Disable Header formatting for the CSV data
                        count = 1

                    else:
                        # Convert all commas to pipes
                        tmp = '|' + line.strip().replace(',', '|') + '|'
                            
                        # Search for all instances of |
                        places = find(tmp, '|')
                        
                        # The default index(base 0) 
                        DEFAULT_CORRECT = 1

                        # There should always be 12 pipes if we follow the format
                        # So if there are more than 12 pipes in a line, we know 
                        # that some commas in the Title column were accidentally
                        # converted
                        count = tmp.count('|')
                        
                        # Find modulo
                        if count > 12:
                            diff = count % 12
                        
                        # For each extra pipe we find, we can assume that every
                        # pipe after the second pipe is actually a mistake
                        # so what we do is turn the entire line into a list and
                        # convert the modulo pipes back to commas
                            for i in diff:
                                tmp2[places[DEFAULT_CORRECT + (i+1)]] = ','                        
                        
                        # Convert the list back to a string
                        tmp2 = list(tmp)
                        tmp2 = ''.join(tmp2)
                        outf.write(tmp2 + '\n')
                            
        #except Exception, e:
            #traceback.print_exc()
            #sys.exit(-1)

        finally:
            if outf:
                outf.close()

        #Store output.txt as data variable
        with open('output.txt', 'r') as myfile:
            data=myfile.read()

        #SMTP Config
        emailfrom = ""
        emailto = ""
        fileToSend = second_tuesday_ymd + 'patches.csv'

        msg = MIMEMultipart()
        msg["From"] = emailfrom
        msg["To"] = emailto
        msg["Subject"] = "Patch Tuesday Security Updates: " + second_tuesday_ymd
        msg.preamble = "Patch Tuesday Security Updates: " + second_tuesday_ymd
        body = data

        ctype, encoding = mimetypes.guess_type(fileToSend)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split("/", 1)


        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
        msg.attach(attachment)

        content = MIMEText(body, 'plain')
        msg.attach(content)

        server = smtplib.SMTP('smtp ip',25)
        server.sendmail(emailfrom, emailto, msg.as_string())
        server.quit()

        #Cleanup
        os.remove(second_tuesday_ymd + 'patches.csv')
        os.remove('formatted_patches.csv')
        os.remove('output.txt')

    else:
        sys.exit()

main()
