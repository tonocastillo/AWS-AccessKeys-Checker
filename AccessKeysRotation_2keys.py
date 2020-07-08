import boto3,datetime,time
iam = boto3.client("iam")
ses = boto3.client('ses')
SENDER = 'ADMIN@EXAMPLE.COM '
SUBJECT = 'Multiple IAM user Access Keys found! Need only 1'
CHARSET = "UTF-8"
def send_email(RCPT, CHARSET, BODY_HTML, SUBJECT, SENDER ):
    response = ses.send_email(Destination={'ToAddresses': [RCPT,],}, Message={'Body': {'Html': {'Charset': CHARSET,'Data': BODY_HTML,},},'Subject': {'Charset': CHARSET,'Data': SUBJECT,},},Source=SENDER)
    return(response)
def lambda_handler(event,context):
    users_list = iam.list_users()['Users']
    for user in users_list:
        uName = user['UserName']
        aKdata = iam.list_access_keys(UserName = uName)
        uTagData = iam.list_user_tags(UserName=uName)['Tags']
        actKeyLst = []
        for accKeydata in  aKdata['AccessKeyMetadata']:
            aKName = accKeydata['AccessKeyId']
            actKeyLst.append(aKName)
            BODY_HTML = """<html>
            <head></head>
            <body>
              <h1>Your IAM username '<USERNAME>'  have 2 IAM Access Keys:</h1>
              <p><code> 1) <ACCESSKEY_ID1></code></p>
              <p><code> 2) <ACCESSKEY_ID2></code></p>
              <p> One of those keys must be deleted.</p>
              <p> To confirm what key is in use, run: </p>
              <p><code><span style="padding-left:4em">$cat ~/.aws/credentials</span></code><p>
              <p> Delete the key that is <b>NOT</b> in use with one of the commands below:</p>
              <p><code><span style="padding-left:4em">$aws iam delete-access-key --access-key-id <ACCESSKEY_ID1> --user-name <USERNAME></span></code></p>
              <p><code><span style="padding-left:4em">$aws iam delete-access-key --access-key-id <ACCESSKEY_ID2> --user-name <USERNAME></span></code></p>
            </body>
            </html>
                        """
            if len(uTagData) > 0:
                for tag in uTagData:
                    if 'OwnerEmailAddress' in tag['Key']:
                        RCPT = tag['Value']
                        if len(actKeyLst) == 2:
                            print(f"User '{uName}' has 2 access keys, sending email...")
                            aK1Name = actKeyLst[0]
                            aK2Name = actKeyLst[1]
                            bdyHtml = BODY_HTML.replace("<USERNAME>",uName).replace("<ACCESSKEY_ID1>",aK1Name).replace("<ACCESSKEY_ID2>",aK2Name)
                            print(f"email sent to {user}")
#                            send_email(RCPT, CHARSET, bdyHtml, SUBJECT, SENDER)
