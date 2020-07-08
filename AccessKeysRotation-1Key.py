import boto3,datetime,time,sys
iam = boto3.client("iam")
ses = boto3.client('ses')
SENDER = 'devops@yieldmo.com'
SUBJECT = 'AWS IAM Access Key rotation (Access Key is too old.)'
CHARSET = "UTF-8"
def send_email(RCPT, CHARSET, BODY_HTML, SUBJECT, SENDER ):
    response = ses.send_email(Destination={'ToAddresses': [RCPT,],}, Message={'Body': {'Html': {'Charset': CHARSET,'Data': BODY_HTML,},},'Subject': {'Charset': CHARSET,'Data': SUBJECT,},},Source=SENDER)
    return(response)
def list_access_keys(usr):
    rsp = iam.list_access_keys(UserName=usr)
    return(rsp)
def list_users():
    rsp = iam.list_users()
    return(rsp)
def lambda_handler(event,context):
    print(event)
    for user in [ user['UserName'] for user in iam.list_users()['Users'] ]:
        try:
            active = list_access_keys(user)['AccessKeyMetadata'][0]['Status']
            print(active)
            if active == 'Active':
                aKdata = iam.list_access_keys(UserName=user)
                uTagData = iam.list_user_tags(UserName=user)['Tags']
                actDayLst = []
                for accKeydata in  aKdata['AccessKeyMetadata']:
                    aKName = accKeydata['AccessKeyId']
                    aKdate = accKeydata['CreateDate']
                    aKdate = aKdate.strftime("%Y-%m-%d %H:%M:%S")
                    curDate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    aKd = time.mktime(datetime.datetime.strptime(aKdate, "%Y-%m-%d %H:%M:%S").timetuple())
                    curD = time.mktime(datetime.datetime.strptime(curDate, "%Y-%m-%d %H:%M:%S").timetuple())
                    actDay = (curD - aKd)/60/60/24 
                    actDayLst.append(aKName)
                    actDayLst.append(actDay)
                    BODY_HTML = """<html>
                    <head></head>
                    <body>
                      <h1>Your account Access Key is too old (<DAYS> days old)</h1>
                      <p> Please create a new Access Key using the AWS CLI as follows: </p>
                      <p><code><span style="padding-left:4em">$aws iam create-access-key --user-name <USERNAME></span></code></p>
                      <p> Use the following command to configure your laptop with the new Access Key: </p>
                      <p><code><span style="padding-left:4em">$aws configure</span></code></p>
                      <p> To delete the old Access Key use the following command:</p>
                      <p><code><span style="padding-left:4em">$aws iam delete-access-key --access-key-id <ACCESSKEY_ID> --user-name <USERNAME></span></code></p>
                    </body>
                    </html>
                                """
                if actDay >= 90:
                    if len(uTagData) > 0:
                        for tag in uTagData:
                            if 'OwnerEmailAddress' in tag['Key']:
                                RCPT = tag['Value']
                                if len(actDayLst) == 2:
                                    print(f"User {user} access keys are too old, sending email...")
                                    aK1Name = actDayLst[0]
                                    aK1ds = round(int(actDayLst[1]))
                                    bdyHtml = BODY_HTML.replace("<DAYS>",str(aK1ds)).replace("<USERNAME>",user).replace("<ACCESSKEY_ID>",aK1Name)
                                    send_email(RCPT, CHARSET, bdyHtml, SUBJECT, SENDER)
                            else:
                                print(f"User {user} does not have the OwnerEmailAddress tag")    
            else:
                print(f'{user} keys is inactive, ignoring...')
                pass
        except IndexError:
            print(f'{user} has no key')
