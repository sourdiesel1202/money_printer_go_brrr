import boto3
from botocore.exceptions import ClientError
def generate_mpd_html_table(mpb_csv):
    table_header_str = "".join([f"<th><b>{x}</b></th>" for x in mpb_csv[0]])
    table_data_str = ""
    for i in range(1, len(mpb_csv)):
         table_data_str = table_data_str + f"<tr>{''.join([f'<td>{x}</td>' for x in mpb_csv[i]])}</tr>"

    css = """table.darkTable {
  font-family: "Arial Black", Gadget, sans-serif;
  border: 2px solid #000000;
  background-color: #4A4A4A;
  width: 100%;
  height: 200px;
  text-align: center;
  border-collapse: collapse;
}
table.darkTable td, table.darkTable th {
  border: 1px solid #4A4A4A;
  padding: 3px 2px;
}
table.darkTable tbody td {
  font-size: 13px;
  color: #E6E6E6;
}
table.darkTable tr:nth-child(even) {
  background: #888888;
}
table.darkTable thead {
  background: #000000;
  border-bottom: 3px solid #000000;
}
table.darkTable thead th {
  font-size: 15px;
  font-weight: bold;
  color: #E6E6E6;
  text-align: center;
  border-left: 2px solid #4A4A4A;
}
table.darkTable thead th:first-child {
  border-left: none;
}

table.darkTable tfoot {
  font-size: 12px;
  font-weight: bold;
  color: #E6E6E6;
  background: #000000;
  background: -moz-linear-gradient(top, #404040 0%, #191919 66%, #000000 100%);
  background: -webkit-linear-gradient(top, #404040 0%, #191919 66%, #000000 100%);
  background: linear-gradient(to bottom, #404040 0%, #191919 66%, #000000 100%);
  border-top: 1px solid #4A4A4A;
}
table.darkTable tfoot td {
  font-size: 12px;
}"""

    body_html = f"""<html>
    <head>
    <style>
    {css}
    </style>
    </head>
    <body>
<table class="darkTable">
    <tr>{table_header_str}</tr>
    {table_data_str}
    </table>

    </body>
    </html>"""


    return body_html
def send_email(sender, recipient, subject, body_html, body_text="Amazon SES Test (Python)\r\nThis email was sent with Amazon SES using the AWS SDK for Python (Boto)."):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    # sender = "andrew.smiley937@gmail.com"

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    # recipient = "andrew.smiley937@gmail.com"

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-2"

    # The subject line for the email.
    # subject = "Amazon SES Test (SDK for Python)"

    # The email body for recipients with non-HTML email clients.
    body_text = (body_text
                 )

    # The HTML body of the email.
    # body_html = <html>
    # <head></head>
    # <body>
    #   <h1>Amazon SES Test (SDK for Python)</h1>
    #   <p>This email was sent with
    #     <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
    #     <a href='https://aws.amazon.com/sdk-for-python/'>
    #       AWS SDK for Python (Boto)</a>.</p>
    # </body>
    # </html>
    #             """

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=sender,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])