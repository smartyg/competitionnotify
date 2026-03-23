#!/usr/bin/python

import smtplib, ssl
smtp_server = "mail.hardgaatie.nl"
sender_email = "wedstrijden@hardgaatie.nl"
password = ""# recreatieschaatsen"
port = 587
context = ssl.create_default_context()

receiver_email = "goedhart.martijn@gmail.com"
message = """\
Subject: Een test email

Dit is een test vanuit Python."""

try:
  server = smtplib.SMTP(smtp_server, port)
  server.ehlo()
  server.starttls(context=context)
  server.ehlo()
  server.login(sender_email, password)
  server.sendmail(sender_email, receiver_email, message)
except Exception as e:
  print(e)
finally:
  server.quit()
