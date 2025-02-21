from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse,HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import AgentDataForm
from .models import AgentData
import pandas as pd
from django.views.generic import View
from django.http import JsonResponse
import numpy as np
import pymysql.cursors
from sqlalchemy import create_engine
from django.db import connection
import json
import datetime
import datetime as dt
from datetime import timedelta
 

import re
import random
import base64
# from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
#import squarify
import matplotlib.pyplot as plt
import seaborn as sns
import io
import urllib, base64
from unidecode import unidecode
import codecs
from os import path 
from wordcloud import WordCloud 
import os

# class create for new word summary by junaid 21 May 2024
# class Word:
#     def __init__(self, word, start, end, confidence, punctuated_word, speaker, speaker_confidence, sentiment, sentiment_score):
#         self.word = word
#         # self.start = start
#         # self.end = end
#         # self.confidence = confidence
#         # self.punctuated_word = punctuated_word
#         # self.speaker = speaker
#         # self.speaker_confidence = speaker_confidence
#         # self.sentiment = sentiment
#         # self.sentiment_score = sentiment_score
        
#         self.start = float(start) if start != "None" else None
#         self.end = float(end) if end != "None" else None
#         self.confidence = float(confidence) if confidence != "None" else None
#         self.punctuated_word = punctuated_word
#         self.speaker = int(speaker) if speaker != "None" else None
#         self.speaker_confidence = float(speaker_confidence) if speaker_confidence != "None" else None
#         self.sentiment = sentiment if sentiment != "None" else None
#         self.sentiment_score = float(sentiment_score) if sentiment_score != "None" else None
# # class create for new word summary by junaid 21 May 2024


# ===================== code added by junaid 11 june 2024 Block Started
# class work with data_formatter function
class Word:
    def __init__(self, word, start, end, confidence, punctuated_word, speaker, speaker_confidence, sentiment=None, sentiment_score=None):
        self.word = word
        self.start = start
        self.end = end
        self.confidence = confidence
        self.punctuated_word = punctuated_word
        self.speaker = speaker
        self.speaker_confidence = speaker_confidence
        self.sentiment = sentiment
        self.sentiment_score = sentiment_score

# ===================== code added by junaid 11 june 2024 Block Ended


def connection():
	conn = pymysql.connect(
		host = "192.168.0.180",
		user = "root",
		password = "Opo@1234",
		database = "test_sbivoiceanalytics",
		charset='utf8mb4')
	return conn

# def vm_connection():
# 	conn = pymysql.connect(
# 		host = "192.168.0.180",
# 		user = "root",
# 		password = "Opo@1234",
# 		database = "VAmodel_db",
# 		charset='utf8mb4')
# 	return conn



def master(request):
	return render(request,'master.html')

# def checkldap(username,password):
# 	try:
# 		token = win32security.LogonUser(username,'onepointone.in',password,win32security.LOGON32_LOGON_NETWORK, win32security.LOGON32_PROVIDER_DEFAULT)
# 		return 1
# 	except:
# 		return 0

@csrf_exempt
def login(request):
	if request.method == "POST":
		conn = connection()
		username = request.POST.get('username')
		password = request.POST.get('password')
		print(username,password)
		# userinfo = pd.read_sql(f"SELECT * FROM users where opoid = '{username}' and password='{password}' limit 1;",conn)
		userinfo = pd.read_sql("SELECT opoid, name, role FROM users WHERE opoid = %s AND password = %s LIMIT 1;", conn, params=(username, password))
		print(userinfo)

		conn.close()
		if(len(userinfo)>=1):
			name = str(userinfo["name"][0])
			role = str(userinfo["role"][0])
			print("Name:"+str(userinfo["name"][0]),"Role:"+str(userinfo["role"][0]))
			print(username)
			request.session['name'] = name
			request.session['opoid'] = username
			request.session['role'] = role
			print(request.session.get('opoid'))
			data = "1"

			return HttpResponse(json.dumps({'data':data}), content_type="application/json")

		else:
			# messages.error(request,'User not register..!')
			data = "3"
			return HttpResponse(json.dumps({'data':data}), content_type="application/json")
		
	else:
		return render(request,'login.html')


def dashboard(request):
	user = request.session.get('opoid')
	if not request.session.session_key:
		request.session.save()
	session_id = request.session.session_key
	if user is None:
		return redirect('/')
	else:
		conn = connection()
		# datastatus = pd.read_sql(f"SELECT COUNT(id) AS call_evaluted, FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral,FORMAT(AVG(qualityscore),2) as quality_score FROM calltrans where calldate >= DATE_SUB(CURDATE(), INTERVAL 6 DAY);",conn)
		datastatus = pd.read_sql("SELECT COUNT(id) AS call_evaluted, FORMAT(AVG(positivescore), 2) AS positive, FORMAT(AVG(negativescore), 2) AS negative, FORMAT(AVG(neutralscore), 2) AS neutral,FORMAT(AVG(qualityscore), 2) AS quality_score FROM calltrans WHERE calldate >= CURDATE() - INTERVAL 6 DAY;", conn)
		# datastatus = pd.read_sql("SELECT COUNT(id) AS call_evaluted, FORMAT(AVG(positivescore), 2) AS positive, FORMAT(AVG(negativescore), 2) AS negative, FORMAT(AVG(neutralscore), 2) AS neutral, FORMAT(AVG(qualityscore), 2) AS quality_score FROM calltrans WHERE calldate >= CURDATE() - INTERVAL 6 DAY;", conn)


		# print(datastatus)

		#df_highlight_data = pd.read_sql(f"SELECT COUNT(*) AS call_evaluted, FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral FROM calltrans WHERE calldate >= DATE_SUB(NOW(), INTERVAL 8 DAY);",conn)
		
		evaluated_call = datastatus['call_evaluted'][0]
		
		positive_call = datastatus['positive'][0]
		negative_call = datastatus['negative'][0]
		neutral_call = datastatus['neutral'][0]
		quality_score = datastatus['quality_score'][0]
		

		date_list = []
	
		pdate = datetime.datetime.today() - datetime.timedelta(days=1)
		for x in range(7):
		    Date = pdate - datetime.timedelta(days=x)
		    date_list.append(Date.strftime("%Y-%m-%d"))
		 
		
		#chart - 1
		#by calldate
		# df_tc_date = pd.read_sql(f"SELECT DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate, COUNT(calldate) AS total_call FROM calltrans WHERE calldate >= DATE_SUB(NOW(), INTERVAL 7 DAY) GROUP BY calldate;",conn)
		
		# df_tc_date = pd.read_sql("SELECT DATE(calldate) AS lastdate, COUNT(*) AS total_call FROM calltrans WHERE calldate >= DATE_SUB(NOW(), INTERVAL 7 DAY) GROUP BY DATE(calldate);", conn)
		# df_tc_date = pd.read_sql("SELECT DATE(calldate) AS lastdate, COUNT(*) AS total_call FROM calltrans WHERE calldate >= CURDATE() - INTERVAL 7 DAY GROUP BY lastdate;", conn)

		
		df_tc_date = pd.read_sql("SELECT DATE(calldate) AS lastdate, COUNT(*) AS total_call FROM calltrans WHERE calldate >= CURDATE() - INTERVAL 7 DAY " "GROUP BY DATE(calldate);", conn)
		# query = "CALL GetCallCountsByDate();"
		# df_tc_date = pd.read_sql(query, conn)
		# print(df_tc_date )
		


		#by created_at	
		dc = df_tc_date.to_dict('records')
		
		
		data = []
		print(data)
		data1 = []
		for i in df_tc_date.to_dict('records'):
			data.append(i)
		
		
		dt1 = {}

		n={}
		n1={}
		n2={}

		final_gp1 = {}
		for index, i in  enumerate(date_list):
		    value_get_flag = False
		    for j  in  data:
		        n = {}
		        if(j['lastdate'] == i):
		           n[f'lastdate_{i}'] = j['total_call']
		           n1['date'] = i
		           n1['call'] = j['total_call']

		           
		           final_gp1[f'lastdate_{index}'] = j['total_call']
		           value_get_flag = True
		    #print(value_get_flag)
		    if(value_get_flag == False):
		           n[f'lastdate_{i}'] = 0
		           final_gp1[f'lastdate_{index}'] = 0
		           n1['date'] = i
		           n1['call'] = 0

		    elif(value_get_flag == True):
		        n1[f'lastdate_{i}'] = 0

		db_date = {}
		for index,i in enumerate(data):
			db_date[f'day_{index}']=i['total_call']

		#chart - 2
		# df_pnn_data = pd.read_sql(f"SELECT DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate," 
		# 	"FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral FROM calltrans WHERE calldate >= DATE_SUB(NOW(), INTERVAL 7 DAY) GROUP BY calldate;",conn)
		
		df_pnn_data = pd.read_sql("SELECT DATE(calldate) AS lastdate, FORMAT(AVG(positivescore), 2) AS positive, FORMAT(AVG(negativescore), 2) AS negative, FORMAT(AVG(neutralscore), 2) AS neutral FROM calltrans WHERE calldate >= CURDATE() - INTERVAL 7 DAY GROUP BY lastdate;", conn)
		# df_pnn_data = pd.read_sql("SELECT DATE(calldate) AS lastdate, FORMAT(AVG(positivescore), 2) AS positive, FORMAT(AVG(negativescore), 2) AS negative, FORMAT(AVG(neutralscore), 2) AS neutral FROM calltrans WHERE calldate >= CURDATE() - INTERVAL 7 DAY GROUP BY lastdate;", conn)


		# print(df_pnn_data)

		
		sizes,label,unique,wordcldtxt = wordtree('NO')
		unique = list(unique)
		try:
			img = generate_wordcloud(wordcldtxt)
		except Exception as e:
			img = 'hello'
			print(e)
		pnn_data = []
		for i in df_pnn_data.to_dict('records'):
			# print(i)
			pnn_data.append(i)

		# disp_qry = pd.read_sql(f"select CONCAT(disposition, '-',subdisposition) as disposition, COUNT(*) AS disposition_count from calltrans where calldate >= DATE_SUB(NOW(), INTERVAL 7 DAY)  GROUP BY disposition,subdisposition HAVING disposition REGEXP '^[^0-9]+$'  order by count(*) desc;",conn)
		
		# disp_qry = pd.read_sql("SELECT CONCAT(disposition, '-', subdisposition) AS disposition, COUNT(*) AS disposition_count FROM calltrans WHERE calldate >= CURDATE() - INTERVAL 7 DAY GROUP BY disposition, subdisposition HAVING disposition NOT REGEXP '[0-9]'ORDER BY disposition_count DESC;", conn)
		# disp_qry = pd.read_sql("SELECT CONCAT(disposition, '-', subdisposition) AS disposition, COUNT(*) AS disposition_count FROM calltrans WHERE calldate >= CURDATE() - INTERVAL 7 DAY AND disposition NOT REGEXP '[0-9]' GROUP BY disposition, subdisposition ORDER BY disposition_count DESC;", conn)
		
		
		query = """SELECT CONCAT(disposition, '-', subdisposition) AS disposition, COUNT(*) AS disposition_count FROM calltrans WHERE calldate >= CURDATE() - INTERVAL 7 DAY AND NOT REGEXP_LIKE(disposition, '[0-9]') GROUP BY disposition, subdisposition ORDER BY disposition_count DESC;"""
		# query = "CALL GetDispositionSummary()"
		disp_qry = pd.read_sql(query, conn )
		print(disp_qry )
		# disp_qry=pd.read_sql(query, conn)
		

		# print(disp_qry)

		
		disposition_average_count = []

		disp_qry = disp_qry.to_dict('split')
		#print(disp_qry)
		for i in disp_qry['data']:
			disposition_average_count.append({"title":""+i[0]+"","count":i[1]},)
		
		#print(disposition_average_count)		
		#print(x)
		#print(disp_qry)

		# qty_dt = """
		#    SELECT 
		#    CAST((SUM(CASE WHEN t1.accountvalidation  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)  * 100 )as decimal(18,1)) AS `Account Validation`,
 

		# 	 CAST((SUM(CASE WHEN t1.appropriatecallclosing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Appropriate call closing`,
		# 	 CAST((SUM(CASE WHEN t1.appropriateprobing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Appropriate Probing`,


		# 	 CAST((SUM(CASE WHEN t1.datacapturing_remarks = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Data Capturing / Remarks`,
		# 	 CAST((SUM(CASE WHEN t1.disposition  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Disposition.1`,
		# 	 CAST((SUM(CASE WHEN t1.empathy  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Empathy `,


		# 	 CAST((SUM(CASE WHEN t1.grammarandsentenceformation  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Grammar and Sentence Formation`,




		# 	 CAST((SUM(CASE WHEN t1.purposeofcall  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Purpose of call`,
		# 	 CAST((SUM(CASE WHEN t1.rpc  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `RPC`,
		# 	 CAST((SUM(CASE WHEN t1.self_companyintroduction  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Self / Company Introduction`,

		# 	 CAST((SUM(CASE WHEN t1.standardgreeting  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Standard Greeting`

		# 	 FROM sbitest_ai AS t1 join calltrans c on t1.connid = c.connid where
		# 	 """
		
		# ====================================== New QUERY with Percentage and Count Start ===============================
		# qty_dt = """
		# 		SELECT 
		# 			CAST((SUM(CASE WHEN t1.accountvalidation  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)  * 100 )as decimal(18,1)) AS `Account Validation`,
		# 			SUM(CASE WHEN t1.accountvalidation = 'Not MET' THEN 1 ELSE 0 END) AS `Count of Account Validation MET count`,

		# 			CAST((SUM(CASE WHEN t1.appropriatecallclosing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Appropriate call closing`,
		# 			SUM(CASE WHEN t1.appropriatecallclosing = 'Not MET' THEN 1 ELSE 0 END) AS `Appropriate call closing MET count`,

		# 			CAST((SUM(CASE WHEN t1.appropriateprobing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Appropriate Probing`,
		# 			SUM(CASE WHEN t1.appropriateprobing = 'Not MET' THEN 1 ELSE 0 END) AS `Appropriate Probing MET count`,

		# 			CAST((SUM(CASE WHEN t1.datacapturing_remarks = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Data Capturing / Remarks`,
		# 			SUM(CASE WHEN t1.datacapturing_remarks = 'Not MET' THEN 1 ELSE 0 END) AS `Data Capturing / Remarks MET count`,

		# 			CAST((SUM(CASE WHEN t1.disposition  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Disposition.1`,
		# 			SUM(CASE WHEN t1.disposition = 'Not MET' THEN 1 ELSE 0 END) AS `Disposition.1 MET count`,

		# 			CAST((SUM(CASE WHEN t1.empathy  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Empathy `,
		# 			SUM(CASE WHEN t1.empathy = 'Not MET' THEN 1 ELSE 0 END) AS `Empathy MET count`,

		# 			CAST((SUM(CASE WHEN t1.grammarandsentenceformation = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100) AS decimal(18,1)) AS `Grammar and Sentence Formation`,
		# 			SUM(CASE WHEN t1.grammarandsentenceformation = 'Not Met' THEN 1 ELSE 0 END) AS `Grammar and Sentence Formation MET count`,

		# 			CAST((SUM(CASE WHEN t1.purposeofcall  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Purpose of call`,
		# 			SUM(CASE WHEN t1.purposeofcall = 'Not Met' THEN 1 ELSE 0 END) AS `Purpose of call MET count`,

		# 			CAST((SUM(CASE WHEN t1.rpc  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `RPC`,
		# 			SUM(CASE WHEN t1.rpc = 'Not Met' THEN 1 ELSE 0 END) AS `RPC MET count`,

		# 			CAST((SUM(CASE WHEN t1.self_companyintroduction  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Self / Company Introduction`,
		# 			SUM(CASE WHEN t1.self_companyintroduction = 'Not Met' THEN 1 ELSE 0 END) AS `Self / Company Introduction MET count`,

		# 			CAST((SUM(CASE WHEN t1.standardgreeting  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Standard Greeting`,
		# 			SUM(CASE WHEN t1.standardgreeting = 'Not Met' THEN 1 ELSE 0 END) AS `Standard Greeting MET count`
		# 		FROM 
		# 			sbitest_ai AS t1
		# 		JOIN 
		# 			calltrans AS c ON t1.connid = c.connid
				
		# 		WHERE 
		# """
		qty_dt = """
					SELECT 
						CAST(SUM(CASE WHEN t1.accountvalidation = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `Account Validation`,
						SUM(CASE WHEN t1.accountvalidation = 'Not MET' THEN 1 ELSE 0 END) AS `Count of Account Validation MET count`,
						
						CAST(SUM(CASE WHEN t1.appropriatecallclosing = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `Appropriate call closing`,
						SUM(CASE WHEN t1.appropriatecallclosing = 'Not MET' THEN 1 ELSE 0 END) AS `Appropriate call closing MET count`,
						
						CAST(SUM(CASE WHEN t1.appropriateprobing = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `Appropriate Probing`,
						SUM(CASE WHEN t1.appropriateprobing = 'Not MET' THEN 1 ELSE 0 END) AS `Appropriate Probing MET count`,
						
						CAST(SUM(CASE WHEN t1.datacapturing_remarks = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `Data Capturing / Remarks`,
						SUM(CASE WHEN t1.datacapturing_remarks = 'Not MET' THEN 1 ELSE 0 END) AS `Data Capturing / Remarks MET count`,
						
						CAST(SUM(CASE WHEN t1.disposition = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `Disposition.1`,
						SUM(CASE WHEN t1.disposition = 'Not MET' THEN 1 ELSE 0 END) AS `Disposition.1 MET count`,
						
						CAST(SUM(CASE WHEN t1.empathy = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `Empathy`,
						SUM(CASE WHEN t1.empathy = 'Not MET' THEN 1 ELSE 0 END) AS `Empathy MET count`,
						
						CAST(SUM(CASE WHEN t1.grammarandsentenceformation = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `Grammar and Sentence Formation`,
						SUM(CASE WHEN t1.grammarandsentenceformation = 'Not MET' THEN 1 ELSE 0 END) AS `Grammar and Sentence Formation MET count`,
						
						CAST(SUM(CASE WHEN t1.purposeofcall = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `Purpose of call`,
						SUM(CASE WHEN t1.purposeofcall = 'Not MET' THEN 1 ELSE 0 END) AS `Purpose of call MET count`,
						
						CAST(SUM(CASE WHEN t1.rpc = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `RPC`,
						SUM(CASE WHEN t1.rpc = 'Not MET' THEN 1 ELSE 0 END) AS `RPC MET count`,
						
						CAST(SUM(CASE WHEN t1.self_companyintroduction = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `Self / Company Introduction`,
						SUM(CASE WHEN t1.self_companyintroduction = 'Not MET' THEN 1 ELSE 0 END) AS `Self / Company Introduction MET count`,
						
						CAST(SUM(CASE WHEN t1.standardgreeting = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(18,1)) AS `Standard Greeting`,
						SUM(CASE WHEN t1.standardgreeting = 'Not MET' THEN 1 ELSE 0 END) AS `Standard Greeting MET count`
					FROM 
						sbitest_ai AS t1
					JOIN 
						calltrans AS c ON t1.connid = c.connid
					WHERE 
						c.calldate BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
					"""


		# ====================================== New QUERY with Percentage and Count End ===============================

		
		# quality_attr = pd.read_sql(f"{qty_dt} DATE(c.calldate) <= CURDATE() and  DATE(c.calldate) > DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 7 DAY), '%Y-%m-%d') ",conn)
		# quality_attr = quality_attr.to_dict('records')
		#print("============",len(quality_attr[0]))

		# cur = conn.cursor()
		# cur.execute(f"{qty_dt} DATE(c.calldate) <= CURDATE() and  DATE(c.calldate) > DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 7 DAY), '%Y-%m-%d') ")
		# row = cur.fetchone()
		cur = conn.cursor()
		cur.execute(qty_dt)
		row = cur.fetchone()
		# print(row)
		print("row :",row)
		print("row type :",type(row))

		if all(element is not None for element in row):
			finallist = [
				{"key": "Account Validation", "value": int(row[0]), "count": int(row[1])},
				{"key": "Appropriate call closing", "value": int(row[2]), "count": int(row[3])},
				{"key": "Appropriate Probing", "value": int(row[4]), "count": int(row[5])},
				{"key": "Data Capturing / Remarks", "value": int(row[6]), "count": int(row[7])},
				{"key": "Disposition", "value": int(row[8]), "count": int(row[9])},
				{"key": "Empathy", "value": int(row[10]), "count": int(row[11])},
				{"key": "Grammar and Sentence Formation", "value": int(row[12]), "count": int(row[13])},
				{"key": "Purpose of call", "value": int(row[14]), "count": int(row[15])},
				{"key": "RPC", "value": int(row[16]), "count": int(row[17])},
				{"key": "Self / Company Introduction", "value": int(row[18]), "count": int(row[19])},
				{"key": "Standard Greeting", "value": int(row[20]), "count": int(row[21])},
			]
		else:
			finallist = [
				{"key": "Account Validation", "value": 0, "count": 0},
				{"key": "Appropriate call closing", "value": 0, "count": 0},
				{"key": "Appropriate Probing", "value": 0, "count": 0},
				{"key": "Data Capturing / Remarks", "value": 0, "count": 0},
				{"key": "Disposition", "value": 0, "count": 0},
				{"key": "Empathy", "value": 0, "count": 0},
				{"key": "Grammar and Sentence Formation", "value": 0, "count": 0},
				{"key": "Purpose of call", "value": 0, "count": 0},
				{"key": "RPC", "value": 0, "count": 0},
				{"key": "Self / Company Introduction", "value": 0, "count": 0},
				{"key": "Standard Greeting", "value": 0, "count": 0},
			]



		#print(qualityScore.to_dict('records'))
		
		#data_list = [{'Opening': 99.9781, 'Self Company Introduction': 100.0, 'Verification': 100.0, 'RPC': 99.9343, 'Assertiveness Confident': 99.5257, 'Enthu Energy': 95.1328, 'Professionalism Casual': 100.0, 'Speech Clarity ClearExplanation': 100.0, 'Pace Customer Language': 100.0, 'Personalization': 45.3371, 'Active Listening No Repetition': 98.723, 'Dead Air': 82.7933, 'Hold Protocol': 91.1778, 'Negotiation Skils': 99.2922, 'Urgency Creation': 61.4273, 'Objection Handling Rebuttals': 28.5464, 'Due Date communication': 26.3938, 'Summarization': 97.0811, 'Appropriate closing': 48.7595, 'Complete Information': 99.9781, 'Correct Information': 100.0, 'PTP Detail FPTP': 100.0, 'Script Adherence': 100.0, 'Proactive Information': 0.0949, 'Data Capturing Remarks': 100.0, 'Disclaimer': 65.7983}]
		# print("------------------")
		# sorted_list = []
		# #print(len(quality_attr[0]))
		# for index, key in enumerate(quality_attr[0]):
		# 	val = quality_attr[0].get(key)
		# 	#print(val)
		# 	sorted_list.append({'key':key,'value':val},)
			#print(index, key)

		#print(sorted_list)
		# sorted_list = sorted(quality_attr[0].items(), key=lambda x: float(x[1]))
		# print(sorted_list)
		# print(len(sorted_list))
		# print("------------------")
		#finallist = []
		# finallist = sorted_list
		# for i in range(len(sorted_list)):
		#     finallist.append({'key':sorted_list[i][0],'value':sorted_list[i][1]},)
		#print(finallist)

		# qualityScore = pd.read_sql(f"SELECT ROUND(AVG(s.score), 2) as qualityscore FROM sbivoiceanalytics.sbitest_ai s JOIN sbivoiceanalytics.calltrans c ON s.connid = c.connid WHERE DATE(c.calldate) <= CURDATE() AND DATE(c.calldate) > DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 7 DAY), '%Y-%m-%d');",conn)
		qualityScore = pd.read_sql("""SELECT ROUND(AVG(s.score), 2) AS qualityscore FROM test_sbivoiceanalytics.sbitest_ai s JOIN test_sbivoiceanalytics.calltrans c ON s.connid = c.connid WHERE c.calldate BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE();""", conn)
		# qualityScore=pd.read_sql("CALL GetQualityScoreForLastWeek()", conn)
		# print(qualityScore )

		#word_freq = pd.read_sql(f"SELECT word, COUNT(*) AS word_count FROM (SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(fulltranscript, ' ', n), ' ', -1) AS word FROM calltrans JOIN (SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 ) AS numbers ON CHAR_LENGTH(fulltranscript)  -CHAR_LENGTH(REPLACE(fulltranscript, ' ', '')) >= n-1 where calldate >= DATE_SUB(NOW(), INTERVAL 7 DAY)) AS words GROUP BY word ORDER BY word_count DESC limit 10;", conn)
		#word_freq = word_freq.to_dict('records')
		
		# word_freq = pd.read_sql(f"SELECT Word_Occurrence AS word, COUNT(*) AS word_count FROM sbivoiceanalytics.WordFinder WHERE DATE(calldate) >= DATE_SUB(NOW(), INTERVAL 7 DAY) AND Word_Occurrence != '' GROUP BY Word_Occurrence ORDER BY word_count DESC LIMIT 10;", conn)
		# print(word_freq)
		word_freq = pd.read_sql("""SELECT Word_Occurrence AS word, COUNT(*) AS word_count FROM test_sbivoiceanalytics.WordFinder WHERE calldate >= CURDATE() - INTERVAL 7 DAY AND Word_Occurrence != '' GROUP BY Word_Occurrence ORDER BY word_count DESC LIMIT 10;""", conn)
		print(word_freq)
		# query = "CALL GetTopWords();"
		# word_freq = pd.read_sql(query, conn)

		word_freq = word_freq.to_dict('records')
		# print(word_freq)


		# #=================== Added By Junaid 11 June 2024 Block Started 

		# # if word_freq return empty list then  
		# if word_freq:
		# 	word_freq_dict = {row['word']: row['word_count'] for row in word_freq}	
		# else:
		# 	word_freq_dict = "No Data found:1,Missing:2,Not present:3,Nonexistent:4,Lacking:5"
		# 	word_freq_dict = {word.strip(): int(count) for word, count in (item.split(':') for item in word_freq_dict.split(','))}

		# #=================== Added By Junaid 11 June 2024 Block Ended


		# wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq_dict)
		# img = wordcloud.to_image()
		# buffer = io.BytesIO()
		# img.save(buffer, 'png')
		# b64 = base64.b64encode(buffer.getvalue())	
		# conn.close()
		# todate = datetime.datetime.now()
		# # Calculate the todate which is fromdate + 7 days
		# fromdate= todate - timedelta(days=7)
		# fromdate = fromdate.strftime("%Y-%m-%d")
		# todate = todate.strftime("%Y-%m-%d")

		
		# context = {'fromdate':fromdate,'todate':todate,'calldata':dc,'evaluated_call':evaluated_call,'positive':positive_call,'negative':negative_call,'neutral':neutral_call,'sentiment':pnn_data,'sizes':str(sizes)[1:-1].replace("'",'"'),'label':str(label)[1:-1].replace("'",'"'),"wordcloud":str(b64)[2:-3],'qa_score':qualityScore.to_dict('records'),'attribut_val':finallist,'disp_qry':disposition_average_count,'word_freq':word_freq}
		# return render(request,'dashboard.html',context)


		# if word_freq return empty list then  
		if word_freq:
			word_freq_dict = {row['word']: row['word_count'] for row in word_freq}	
		else:
			word_freq_dict = "No Data found:1,Missing:2,Not present:3,Nonexistent:4,Lacking:5"
			word_freq_dict = {word.strip(): int(count) for word, count in (item.split(':') for item in word_freq_dict.split(','))}


		wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq_dict)
		img = wordcloud.to_image()
		buffer = io.BytesIO()
		img.save(buffer, 'png')
		b64 = base64.b64encode(buffer.getvalue())	
		#=================== Added By Junaid 11 June 2024 Block Ended


		#=================== New word_freq and graph Added By Junaid 19 June 2024 Block Started 
		# word_freq = pd.read_sql(f"SELECT Word_Occurrence AS word, COUNT(*) AS word_count FROM sbivoiceanalytics.WordFinder WHERE date(calldate) BETWEEN '{fromdate}' AND '{todate}' AND Word_Occurrence != 'No Word Found: 0' AND Word_Occurrence != '' GROUP BY Word_Occurrence ORDER BY word_count DESC LIMIT 10;", conn)
		# word_freq1 = pd.read_sql(f"SELECT word, SUM(word_count) AS total_count FROM sbivoiceanalytics.word_search_results where date(calldate)='2024-05-15' GROUP BY word order by total_count desc;", conn)
		
		# word_freq1 = pd.read_sql(f"SELECT word, SUM(word_count) AS total_count FROM sbivoiceanalytics.word_search_results WHERE DATE(calldate) >= DATE_SUB(NOW(), INTERVAL 7 DAY) GROUP BY word order by total_count desc;", conn)
		# print(word_freq1)
		
		word_freq1 = pd.read_sql(""" SELECT word, SUM(word_count) AS total_count FROM test_sbivoiceanalytics.word_search_results  WHERE calldate >= CURDATE() - INTERVAL 7 DAY GROUP BY word ORDER BY total_count DESC;""", conn)
		# query = "CALL GetRecentWordFrequencyFirst();"
		# word_freq1 = pd.read_sql(query, conn)
		word_freq1 = word_freq1.to_dict('records') 
		# print()
		# print()
		# print('word_freq1 :\n',type(word_freq1))
		# print('\n\nword_freq1 :\n',word_freq1)
		# print('\n\nword_freq1 :\n',word_freq1)
		# print()
		# print()

		# if word_freq return empty list then  
		if word_freq1:
			word_freq_dict1 = {row['word']: row['total_count'] for row in word_freq1}	
		else:
			word_freq_dict1 = "No Data found:1,Missing:2,Not present:3,Nonexistent:4,Lacking:5"
			word_freq_dict1 = {word.strip(): int(count) for word, count in (item.split(':') for item in word_freq_dict1.split(','))}

		wordcloud1 = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq_dict1)
		img1 = wordcloud1.to_image()
		buffer1 = io.BytesIO()
		img1.save(buffer1, 'png')
		B64 = base64.b64encode(buffer1.getvalue())

		# print(word_freq)

		conn.close()

		# print("positive_call :",positive_call)
		# print("negative_call :",negative_call)
		# print("neutral :",neutral_call)
		# print("qualityScore.to_dict('records') :",qualityScore.to_dict('records'))

		todate = datetime.datetime.now()
		# Calculate the todate which is fromdate + 7 days
		fromdate= todate - timedelta(days=7)
		fromdate = fromdate.strftime("%Y-%m-%d")
		todate = todate.strftime("%Y-%m-%d")

		# context = {'fromdate':fromdate,'todate':todate,'calldata':dc,'evaluated_call':evaluated_call,'positive':positive_call,'negative':negative_call,'neutral':neutral_call,'sentiment':pnn_data,'sizes':str(sizes)[1:-1].replace("'",'"'),'label':str(label)[1:-1].replace("'",'"'),"wordcloud":str(b64)[2:-3],'qa_score':qualityScore.to_dict('records'),'attribut_val':finallist,'disp_qry':disposition_average_count,'word_freq':word_freq }
		context = {'fromdate':fromdate,'todate':todate,'calldata':dc,'evaluated_call':evaluated_call,'positive':positive_call,'negative':negative_call,'neutral':neutral_call,'sentiment':pnn_data,'sizes':str(sizes)[1:-1].replace("'",'"'),'label':str(label)[1:-1].replace("'",'"'),"wordcloud":str(b64)[2:-3],'qa_score':qualityScore.to_dict('records'),'attribut_val':finallist,'disp_qry':disposition_average_count,'word_freq':word_freq ,'word_freq1':word_freq1 , "wordcloud1":str(B64)[2:-3]}
		return render(request,'dashboard.html',context)

		#=================== New word_freq and graph Added By Junaid 19 June 2024 Block Ended 


def dashboard_date_filter(request):
	user = request.session.get('opoid')
	if user is None:
		return redirect('/')
	else:
		if request.method =='POST':
			fromdate = request.POST.get('startdata')
			todate = request.POST.get('enddata')
			request.session['fromdate_dash'] = fromdate
			request.session['todate_dash'] = todate

			print(fromdate, todate)
			conn = connection()
			
			# datastatus = pd.read_sql(f"SELECT COUNT(id) AS call_evaluted, FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral,FORMAT(AVG(qualityscore),2) as quality_score FROM calltrans where calldate BETWEEN '{fromdate}' and '{todate}' ",conn)
			# datastatus = pd.read_sql(""" SELECT  COUNT(id) AS call_evaluted,  ROUND(AVG(positivescore), 2) AS positive,  ROUND(AVG(negativescore), 2) AS negative, ROUND(AVG(neutralscore), 2) AS neutral,  ROUND(AVG(qualityscore), 2) AS quality_score FROM calltrans  WHERE calldate BETWEEN %s AND %s """, conn, params=[fromdate, todate])
			datastatus = pd.read_sql("SELECT COUNT(id) AS call_evaluted, FORMAT(AVG(positivescore), 2) AS positive, FORMAT(AVG(negativescore), 2) AS negative, FORMAT(AVG(neutralscore), 2) AS neutral, FORMAT(AVG(qualityscore), 2) AS quality_score FROM calltrans WHERE calldate BETWEEN %s AND %s", conn, params=[fromdate, todate])


			# print(datastatus)

			#df_highlight_data = pd.read_sql(f"SELECT COUNT(*) AS call_evaluted, FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral FROM calltrans WHERE calldate BETWEEN '{fromdate}' and '{todate}'",conn)
			#print(df_highlight_data)
			evaluated_call = datastatus['call_evaluted'][0]
			print(evaluated_call)
			positive_call = datastatus['positive'][0]
			negative_call = datastatus['negative'][0]
			neutral_call = datastatus['neutral'][0]
			quality_score = datastatus['quality_score'][0]
			


			date_list = []
		
			pdate = datetime.datetime.today() - datetime.timedelta(days=1)
			for x in range(7):
			    Date = pdate - datetime.timedelta(days=x)
			    date_list.append(Date.strftime("%Y-%m-%d"))
			
			 
			
			#chart - 1
			#by calldate
			# df_tc_date = pd.read_sql(f"SELECT DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate, COUNT(calldate) AS total_call FROM calltrans WHERE calldate BETWEEN '{fromdate}' and '{todate}' GROUP BY calldate order by calldate",conn)
			
			df_tc_date = pd.read_sql(""" SELECT DATE(calldate) AS lastdate,  COUNT(*) AS total_call  FROM calltrans  WHERE calldate BETWEEN %s AND %s  GROUP BY DATE(calldate)  ORDER BY DATE(calldate)""", conn, params=[fromdate, todate])
			# query = "CALL GetCallData(%s, %s)"
			# df_tc_date = pd.read_sql(query, conn, params=(fromdate, todate))

			# print(df_tc_date )

			#by created_at
			dc = df_tc_date.to_dict('records')
			print(dc)
			

			#chart - 2
			# df_pnn_data = pd.read_sql(f"SELECT DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate, FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral FROM calltrans WHERE date(calldate) BETWEEN '{fromdate}' and '{todate}' GROUP BY calldate;",conn)
			# df_pnn_data = pd.read_sql("""SELECT  DATE(calldate) AS lastdate, ROUND(AVG(positivescore), 2) AS positive, ROUND(AVG(negativescore), 2) AS negative, ROUND(AVG(neutralscore), 2) AS neutral FROM calltrans WHERE DATE(calldate) BETWEEN %s AND %s GROUP BY DATE(calldate)""", conn, params=[fromdate, todate])
			
			# df_pnn_data = pd.read_sql("SELECT DATE(calldate) AS lastdate, FORMAT(AVG(positivescore), 2) AS positive, FORMAT(AVG(negativescore), 2) AS negative, FORMAT(AVG(neutralscore), 2) AS neutral FROM calltrans WHERE DATE(calldate) BETWEEN %s AND %s GROUP BY calldate;", conn, params=[fromdate, todate])
			query = "CALL GetPnnData(%s, %s)"
			df_pnn_data = pd.read_sql(query, conn, params=(fromdate, todate))

			# print(df_pnn_data)
			
			sizes,label,unique,wordcldtxt = wordtree_filter('NO', fromdate, todate)
			unique = list(unique)
			try:
				img = generate_wordcloud(wordcldtxt)
			except Exception as e:
				img = 'hello'
				print(e)
			pnn_data = []
			for i in df_pnn_data.to_dict('records'):
				# print(i)
				pnn_data.append(i)

			#disp_qry = pd.read_sql(f"select disposition, COUNT(*) AS disposition_count from calltrans where calldate BETWEEN '{fromdate}' and '{todate}'  GROUP BY disposition HAVING disposition REGEXP '^[^0-9]+$' order by count(*) desc;",conn)
			
			# disp_qry = pd.read_sql(f"select CONCAT(disposition, '-',subdisposition) as disposition, COUNT(*) AS disposition_count from calltrans where calldate BETWEEN '{fromdate}' and '{todate}'  GROUP BY disposition,subdisposition  HAVING disposition REGEXP '^[^0-9]+$' order by count(*) desc;",conn)
			
			
			# disp_qry = pd.read_sql("""SELECT  CONCAT(disposition, '-', subdisposition) AS disposition,  COUNT(*) AS disposition_count FROM calltrans WHERE calldate BETWEEN %s AND %s AND disposition NOT REGEXP '[0-9]' -- Filter out disqualifying rows earlier GROUP BY disposition, subdisposition ORDER BY disposition_count DESC;""", conn, params=[fromdate, todate])
			# changes
			# query = """
			# 				SELECT CONCAT(disposition, '-', subdisposition) AS disposition, COUNT(*) AS disposition_count
			# 				FROM calltrans
			# 				WHERE calldate BETWEEN %s AND %s
			# 				AND disposition NOT REGEXP '[0-9]'
			# 				GROUP BY disposition, subdisposition
			# 				ORDER BY disposition_count DESC;
			# 				"""
			# disp_qry = pd.read_sql(query, conn, params=[fromdate, todate])
			# disp_qry = pd.read_sql("""CALL GetDispositionCounts(%s, %s);""", conn, params=[fromdate, todate])
			disp_qry = pd.read_sql("""CALL  GetDispositionSummaryResult(%s, %s);""", conn, params=[fromdate, todate])
			print(disp_qry)
		

			disposition_average_count = []

			disp_qry = disp_qry.to_dict('split')
			#print(disp_qry)
			
			for i in disp_qry['data']:
				disposition_average_count.append({"title":""+i[0]+"","count":i[1]},)
			
			
			#print(disposition_average_count)		
			#print(x)
			#print(disp_qry)


				# ====================================== OLD QUERY Only with Percentage ===============================
			# 	qty_dt = """
			# 	SELECT 
			#    CAST((SUM(CASE WHEN t1.accountvalidation  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)  * 100 )as decimal(18,1)) AS `Account Validation`,
	

			# 	 CAST((SUM(CASE WHEN t1.appropriatecallclosing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Appropriate call closing`,
			# 	 CAST((SUM(CASE WHEN t1.appropriateprobing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Appropriate Probing`,


			# 	 CAST((SUM(CASE WHEN t1.datacapturing_remarks = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Data Capturing / Remarks`,
			# 	 CAST((SUM(CASE WHEN t1.disposition  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Disposition.1`,
			# 	 CAST((SUM(CASE WHEN t1.empathy  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Empathy `,
			# 	 CAST((SUM(CASE WHEN t1.grammarandsentenceformation  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Grammar and Sentence Formation`,




			# 	 CAST((SUM(CASE WHEN t1.purposeofcall  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Purpose of call`,
			# 	 CAST((SUM(CASE WHEN t1.rpc  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `RPC`,
			# 	 CAST((SUM(CASE WHEN t1.self_companyintroduction  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Self / Company Introduction`,

			# 	 CAST((SUM(CASE WHEN t1.standardgreeting  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Standard Greeting`

			# 	 FROM sbitest_ai AS t1 join calltrans c on t1.connid = c.connid where
				
			# 	 """
			# ====================================== OLD QUERY Only with Percentage ===============================
			
			# ====================================== New QUERY with Percentage and Count ===============================

			# qty_dt = """
			# 		SELECT 
			# 			CAST((SUM(CASE WHEN t1.accountvalidation  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)  * 100 )as decimal(18,1)) AS `Account Validation`,
			# 			SUM(CASE WHEN t1.accountvalidation = 'Not MET' THEN 1 ELSE 0 END) AS `Count of Account Validation MET count`,

			# 			CAST((SUM(CASE WHEN t1.appropriatecallclosing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Appropriate call closing`,
			# 			SUM(CASE WHEN t1.appropriatecallclosing = 'Not MET' THEN 1 ELSE 0 END) AS `Appropriate call closing MET count`,

			# 			CAST((SUM(CASE WHEN t1.appropriateprobing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Appropriate Probing`,
			# 			SUM(CASE WHEN t1.appropriateprobing = 'Not MET' THEN 1 ELSE 0 END) AS `Appropriate Probing MET count`,

			# 			CAST((SUM(CASE WHEN t1.datacapturing_remarks = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Data Capturing / Remarks`,
			# 			SUM(CASE WHEN t1.datacapturing_remarks = 'Not MET' THEN 1 ELSE 0 END) AS `Data Capturing / Remarks MET count`,

			# 			CAST((SUM(CASE WHEN t1.disposition  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Disposition.1`,
			# 			SUM(CASE WHEN t1.disposition = 'Not MET' THEN 1 ELSE 0 END) AS `Disposition.1 MET count`,

			# 			CAST((SUM(CASE WHEN t1.empathy  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) AS `Empathy `,
			# 			SUM(CASE WHEN t1.empathy = 'Not MET' THEN 1 ELSE 0 END) AS `Empathy MET count`,

			# 			CAST((SUM(CASE WHEN t1.grammarandsentenceformation = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100) AS decimal(18,1)) AS `Grammar and Sentence Formation`,
			# 			SUM(CASE WHEN t1.grammarandsentenceformation = 'Not Met' THEN 1 ELSE 0 END) AS `Grammar and Sentence Formation MET count`,

			# 			CAST((SUM(CASE WHEN t1.purposeofcall  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Purpose of call`,
			# 			SUM(CASE WHEN t1.purposeofcall = 'Not Met' THEN 1 ELSE 0 END) AS `Purpose of call MET count`,

			# 			CAST((SUM(CASE WHEN t1.rpc  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `RPC`,
			# 			SUM(CASE WHEN t1.rpc = 'Not Met' THEN 1 ELSE 0 END) AS `RPC MET count`,

			# 			CAST((SUM(CASE WHEN t1.self_companyintroduction  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Self / Company Introduction`,
			# 			SUM(CASE WHEN t1.self_companyintroduction = 'Not Met' THEN 1 ELSE 0 END) AS `Self / Company Introduction MET count`,

			# 			CAST((SUM(CASE WHEN t1.standardgreeting  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)* 100 )as decimal(18,1)) `Standard Greeting`,
			# 			SUM(CASE WHEN t1.standardgreeting = 'Not Met' THEN 1 ELSE 0 END) AS `Standard Greeting MET count`
			# 		FROM 
			# 			sbitest_ai AS t1
			# 		JOIN 
			# 			calltrans AS c ON t1.connid = c.connid
					
			# 		WHERE 
			# """
			qty_dt = """
						SELECT 
							CAST(SUM(CASE WHEN t1.accountvalidation = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `Account Validation`,
							SUM(CASE WHEN t1.accountvalidation = 'Not MET' THEN 1 ELSE 0 END) AS `Count of Account Validation MET count`,

							CAST(SUM(CASE WHEN t1.appropriatecallclosing = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `Appropriate call closing`,
							SUM(CASE WHEN t1.appropriatecallclosing = 'Not MET' THEN 1 ELSE 0 END) AS `Appropriate call closing MET count`,

							CAST(SUM(CASE WHEN t1.appropriateprobing = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `Appropriate Probing`,
							SUM(CASE WHEN t1.appropriateprobing = 'Not MET' THEN 1 ELSE 0 END) AS `Appropriate Probing MET count`,

							CAST(SUM(CASE WHEN t1.datacapturing_remarks = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `Data Capturing / Remarks`,
							SUM(CASE WHEN t1.datacapturing_remarks = 'Not MET' THEN 1 ELSE 0 END) AS `Data Capturing / Remarks MET count`,

							CAST(SUM(CASE WHEN t1.disposition = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `Disposition.1`,
							SUM(CASE WHEN t1.disposition = 'Not MET' THEN 1 ELSE 0 END) AS `Disposition.1 MET count`,

							CAST(SUM(CASE WHEN t1.empathy = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `Empathy`,
							SUM(CASE WHEN t1.empathy = 'Not MET' THEN 1 ELSE 0 END) AS `Empathy MET count`,

							CAST(SUM(CASE WHEN t1.grammarandsentenceformation = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `Grammar and Sentence Formation`,
							SUM(CASE WHEN t1.grammarandsentenceformation = 'Not Met' THEN 1 ELSE 0 END) AS `Grammar and Sentence Formation MET count`,

							CAST(SUM(CASE WHEN t1.purposeofcall = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `Purpose of call`,
							SUM(CASE WHEN t1.purposeofcall = 'Not Met' THEN 1 ELSE 0 END) AS `Purpose of call MET count`,

							CAST(SUM(CASE WHEN t1.rpc = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `RPC`,
							SUM(CASE WHEN t1.rpc = 'Not Met' THEN 1 ELSE 0 END) AS `RPC MET count`,

							CAST(SUM(CASE WHEN t1.self_companyintroduction = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `Self / Company Introduction`,
							SUM(CASE WHEN t1.self_companyintroduction = 'Not Met' THEN 1 ELSE 0 END) AS `Self / Company Introduction MET count`,

							CAST(SUM(CASE WHEN t1.standardgreeting = 'MET' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(18,1)) AS `Standard Greeting`,
							SUM(CASE WHEN t1.standardgreeting = 'Not Met' THEN 1 ELSE 0 END) AS `Standard Greeting MET count`
						FROM 
							sbitest_ai AS t1
						JOIN 
							calltrans AS c ON t1.connid = c.connid
						WHERE 
							c.calldate BETWEEN %s AND %s
					"""



			# ====================================== New QUERY with Percentage and Count ===============================



			# quality_attr = pd.read_sql(f"{qty_dt} c.calldate BETWEEN '{fromdate}' and '{todate}' ",conn)
			# quality_attr = quality_attr.to_dict('records')
			# print(f"\nquality_attr : {quality_attr}\n")
			
			# cur = conn.cursor()
			# cur.execute(f"{qty_dt} c.calldate BETWEEN '{fromdate}' and '{todate}' ")
			# row = cur.fetchone()
			cur = conn.cursor()
			cur.execute(qty_dt, (fromdate, todate))
			row = cur.fetchone()
			# print(row)
			# print("row :",row)
			#print("============",len(quality_attr[0]))
			
			# print("------------------")

			# for index, key in enumerate(quality_attr[0]):
			# 	val = quality_attr[0].get(key)
			# 	sorted_list.append({'key':key,'value':val},)

			# finallist = []
		
			print("------------------")
			#finallist = []
			# finallist = sorted_list
			if row:
				finallist = [
					{"key": "Account Validation", "value": int(row[0]), "count": int(row[1])},
					{"key": "Appropriate call closing", "value": int(row[2]), "count": int(row[3])},
					{"key": "Appropriate Probing", "value": int(row[4]), "count": int(row[5])},
					{"key": "Data Capturing / Remarks", "value": int(row[6]), "count": int(row[7])},
					{"key": "Disposition", "value": int(row[8]), "count": int(row[9])},
					{"key": "Empathy", "value": int(row[10]), "count": int(row[11])},
					{"key": "Grammar and Sentence Formation", "value": int(row[12]), "count": int(row[13])},
					{"key": "Purpose of call", "value": int(row[14]), "count": int(row[15])},
					{"key": "RPC", "value": int(row[16]), "count": int(row[17])},
					{"key": "Self / Company Introduction", "value": int(row[18]), "count": int(row[19])},
					{"key": "Standard Greeting", "value": int(row[20]), "count": int(row[21])},
				]
			else:
				finallist = [
					{"key": "Account Validation", "value": 0, "count": 0},
					{"key": "Appropriate call closing", "value": 0, "count": 0},
					{"key": "Appropriate Probing", "value": 0, "count": 0},
					{"key": "Data Capturing / Remarks", "value": 0, "count": 0},
					{"key": "Disposition", "value": 0, "count": 0},
					{"key": "Empathy", "value": 0, "count": 0},
					{"key": "Grammar and Sentence Formation", "value": 0, "count": 0},
					{"key": "Purpose of call", "value": 0, "count": 0},
					{"key": "RPC", "value": 0, "count": 0},
					{"key": "Self / Company Introduction", "value": 0, "count": 0},
					{"key": "Standard Greeting", "value": 0, "count": 0},
				]

			# for i in range(len(sorted_list)):
			#     finallist.append({'key':sorted_list[i][0],'value':sorted_list[i][1]},)
			#print(finallist)

			# qualityScore = pd.read_sql(f" SELECT ROUND(AVG(score),2) as qualityscore from sbitest_ai sa join sbivoiceanalytics.calltrans ct on ct.connid=sa.connid WHERE date(ct.calldate) BETWEEN '{fromdate}' and '{todate}';",conn)
			query = """SELECT ROUND(AVG(sa.score), 2) AS qualityscore FROM sbitest_ai sa JOIN test_sbivoiceanalytics.calltrans ct  ON ct.connid = sa.connid WHERE ct.calldate BETWEEN %s AND %s;"""
			qualityScore = pd.read_sql(query, conn, params=(fromdate, todate))
			# query = "CALL GetQualityScore(%s, %s)"
			# qualityScore = pd.read_sql(query, conn, params=(fromdate, todate))
			# # print(qualityScore)

			# word_freq = pd.read_sql(f"SELECT Word_Occurrence AS word,count(*) AS word_count FROM sbivoiceanalytics.WordFinder where date(calldate) between '{fromdate}' and '{todate}' and Word_Occurrence !='No Word Found: 0' group by Word_Occurrence ORDER BY word_count DESC LIMIT 10", conn)
			# word_freq = word_freq.to_dict('records')
			
			#=================== Added By Junaid 11 June 2024 Block Started 

			# word_freq = pd.read_sql(f"SELECT Word_Occurrence AS word, COUNT(*) AS word_count FROM sbivoiceanalytics.WordFinder WHERE date(calldate) BETWEEN '{fromdate}' AND '{todate}' AND Word_Occurrence != 'No Word Found: 0' AND Word_Occurrence != '' GROUP BY Word_Occurrence ORDER BY word_count DESC LIMIT 10;", conn)
			# word_freq = word_freq.to_dict('records')

			# # print()
			# # print()
			# # print("word_freq :\n",type(word_freq))
			# # print("\n\nword_freq :\n",word_freq)
			# # print("\n\nword_freq :\n",word_freq)
			# # print()
			# # print()
			

			# # if word_freq return empty list then  
			# if word_freq:
			# 	word_freq_dict = {row['word']: row['word_count'] for row in word_freq}	
			# else:
			# 	word_freq_dict = "No Data found:1,Missing:2,Not present:3,Nonexistent:4,Lacking:5"
			# 	word_freq_dict = {word.strip(): int(count) for word, count in (item.split(':') for item in word_freq_dict.split(','))}

			# # word_freq_dict = {row['word']: row['word_count'] for row in word_freq}

			# wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq_dict)
			# img = wordcloud.to_image()
			# buffer = io.BytesIO()
			# img.save(buffer, 'png')
			# b64 = base64.b64encode(buffer.getvalue())
			# #plt.figure(figsize=(10, 5))

			# #=================== Added By Junaid 11 June 2024 Block Ended


			#=================== New word_freq and graph Added By Junaid 19 June 2024 Block Started 
			# word_freq = pd.read_sql(f"SELECT Word_Occurrence AS word, COUNT(*) AS word_count FROM sbivoiceanalytics.WordFinder WHERE date(calldate) BETWEEN '{fromdate}' AND '{todate}' AND Word_Occurrence != 'No Word Found: 0' AND Word_Occurrence != '' GROUP BY Word_Occurrence ORDER BY word_count DESC LIMIT 10;", conn)
			# word_freq1 = pd.read_sql(f"SELECT word, SUM(word_count) AS total_count FROM sbivoiceanalytics.word_search_results where date(calldate)='2024-05-15' GROUP BY word order by total_count desc;", conn)
			
			# word_freq1 = pd.read_sql(f"SELECT word, SUM(word_count) AS total_count FROM sbivoiceanalytics.word_search_results where date(calldate) between '{fromdate}' and '{todate}' GROUP BY word order by total_count desc;", conn)
			# query = """ SELECT word, SUM(word_count) AS total_count FROM test_sbivoiceanalytics.word_search_results WHERE calldate BETWEEN %s AND %s GROUP BY word  ORDER BY total_count DESC;"""
			# word_freq1 = pd.read_sql(query, conn, params=(fromdate, todate))
			
			# word_freq1 = pd.read_sql("SELECT word, SUM(word_count) AS total_count FROM sbivoiceanalytics.word_search_results WHERE DATE(calldate) BETWEEN %s AND %s GROUP BY word ORDER BY total_count DESC;", conn, params=[fromdate, todate])
			# print(word_freq1)
			
			query = "CALL GetWordFrequency(%s, %s);"
			word_freq1 = pd.read_sql(query, conn, params=[fromdate, todate])
			word_freq1 = word_freq1.to_dict('records')
			 
			
			# print()
			# print()
			# print('word_freq1 :\n',type(word_freq1))
			# print('\n\nword_freq1 :\n',word_freq1)
			# print('\n\nword_freq1 :\n',word_freq1)
			# print()
			# print()

			# if word_freq return empty list then  
			if word_freq1:
				word_freq_dict1 = {row['word']: row['total_count'] for row in word_freq1}	
			else:
				word_freq_dict1 = "No Data found:1,Missing:2,Not present:3,Nonexistent:4,Lacking:5"
				word_freq_dict1 = {word.strip(): int(count) for word, count in (item.split(':') for item in word_freq_dict1.split(','))}

			wordcloud1 = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq_dict1)
			img1 = wordcloud1.to_image()
			buffer1 = io.BytesIO()
			img1.save(buffer1, 'png')
			B64 = base64.b64encode(buffer1.getvalue())

			# print(word_freq)
			#=================== New word_freq and graph Added By Junaid 19 June 2024 Block Ended 


			conn.close()
			print()
			print("finallist :",finallist)
			print()
			print("evaluated_call :",evaluated_call)
			print()

			context = {'calldata':dc,'evaluated_call':evaluated_call,'positive':positive_call,'negative':negative_call,'neutral':neutral_call,'sentiment':pnn_data,'sizes':str(sizes)[1:-1].replace("'",'"'),'label':str(label)[1:-1].replace("'",'"'),'qa_score':qualityScore.to_dict('records'),'attribut_val':finallist,'disp_qry':disposition_average_count,'fromdate':fromdate,'todate':todate,'word_freq1':word_freq1 , "wordcloud1":str(B64)[2:-3]}
			# context = {'calldata':dc,'evaluated_call':evaluated_call,'positive':positive_call,'negative':negative_call,'neutral':neutral_call,'sentiment':pnn_data,'sizes':str(sizes)[1:-1].replace("'",'"'),'label':str(label)[1:-1].replace("'",'"'),"wordcloud":str(b64)[2:-3],'qa_score':qualityScore.to_dict('records'),'attribut_val':finallist,'disp_qry':disposition_average_count,'fromdate':fromdate,'todate':todate,'word_freq':word_freq ,'word_freq1':word_freq1 , "wordcloud1":str(B64)[2:-3]}
			# context = {'calldata':dc,'evaluated_call':evaluated_call,'positive':positive_call,'negative':negative_call,'neutral':neutral_call,'sentiment':pnn_data,'sizes':str(sizes)[1:-1].replace("'",'"'),'label':str(label)[1:-1].replace("'",'"'),"wordcloud":str(b64)[2:-3],'qa_score':qualityScore.to_dict('records'),'attribut_val':finallist,'disp_qry':disposition_average_count,'fromdate':fromdate,'todate':todate,'word_freq':word_freq }
			return render(request,'dashboard.html',context)
		else:
			return redirect('dashboard')


			

def attribute_view(request):
	conn = connection()
	#fromdate = request.session.get('fromdate_dash')
	#todate = request.session.get('todate_dash')
	label = request.GET.get('label').replace(" ", "")
	label = label.replace('/', '_')
	# if label == 'Disposition':
	# 	label='Disposition1'
	# if label == 'DIYAdherence':
	# 	label='Proactive_Information'
	# if label == 'PTPDetailFPTP':
	# 	label='PTP_Detail_FPTP'
	# if label == 'ScriptAdherence':
	# 	label='Script_Adherence'


	fromdate=request.GET.get('fromdate') 
	todate=request.GET.get('todate')
	print(label)
  	 
	pos_call = pd.read_sql(f" SELECT c.*,t.* FROM  sbivoiceanalytics.calltrans c join sbivoiceanalytics.sbitest_ai t on t.connid = c.connid where date(c.calldate) between '{fromdate}' and '{todate}' and t.{label}='Not Met'",conn)
	# query = f"""SELECT c.*, t.* FROM sbivoiceanalytics.calltrans AS c JOIN sbivoiceanalytics.sbitest_ai AS t ON t.connid = c.connid WHERE DATE(c.calldate) BETWEEN %s AND %s AND t.{label} = 'Not Met'"""
	# query = f"""
	# 				SELECT 
	# 					c.id, c.connid, c.processname, c.opoid, c.tlopoid, c.disposition, c.subdisposition,
	# 					c.calltype, c.qualityscore, c.fulltranscript, c.summary, c.wordssummary, c.created_at,
	# 					c.filepath, c.positivescore, c.negativescore, c.neutralscore, c.calldate, c.calltime,
	# 					c.silence_sec, c.total_duration, c.quality_data,
	# 					t.id AS t_id, t.connid AS t_connid, t.transcript, t.score, t.accountvalidation,
	# 					t.appropriatecallclosing, t.appropriateprobing, t.datacapturing_remarks, t.disposition AS t_disposition,
	# 					t.empathy, t.grammarandsentenceformation, t.purposeofcall, t.rpc, t.self_companyintroduction,
	# 					t.standardgreeting, t.created_at AS t_created_at
	# 				FROM sbivoiceanalytics.calltrans AS c
	# 				JOIN sbivoiceanalytics.sbitest_ai AS t ON t.connid = c.connid
	# 				WHERE c.calldate BETWEEN %s AND %s
	# 				AND t.{label} = 'Not Met'
	# 				"""

	# params = [fromdate, todate]
	# pos_call = pd.read_sql(query, conn, params=params)
	print(pos_call)

	pos_call['calltime'] = pos_call['calltime'].astype('str').str.split().str[-1]
	
	conn.close()
	
	page = request.GET.get('page', 1)
	# items_per_page = 50  # Number of items to display per page
	items_per_page = 10
	
	paginator = Paginator(pos_call.to_dict('records'), items_per_page)
	try:
		pos_call_page = paginator.page(page)
	except PageNotAnInteger:
		pos_call_page = paginator.page(1)
	except EmptyPage:
		pos_call_page = paginator.page(paginator.num_pages)
	context = {'data':pos_call_page,'label':label,'fromdate':fromdate,'todate':todate}
	return render(request,'attribute_view.html',context)


def generate_wordcloud(wordcldtxt):
	wordcloud = WordCloud(background_color='white',font_path = 'static/img/TiroDevanagariHindi-Regular.ttf',max_font_size=50).generate(str(wordcldtxt)[1:-1])
	print("==============")
	print("==============")
	img = wordcloud.to_image()
	buffer = io.BytesIO()
	img.save(buffer, 'png')
	b64 = base64.b64encode(buffer.getvalue())

	return b64

def wordtree(connid):
	if connid == "NO":
		sql="select id,fulltranscript from calltrans where calldate >= DATE_SUB(NOW(), INTERVAL 7 DAY) LIMIT 10"
	else:
		sql=f"select id,fulltranscript from calltrans where connid='{connid}'"
	
	con=connection()
	df=pd.read_sql(sql, con)
	wordcldtxt = ' '.join(df['fulltranscript']).lower().split()
	wordcount=pd.Series(' '.join(df['fulltranscript']).lower().split()).value_counts()[:100]
	wordcount=wordcount.reset_index()
	colors=['#fae588','#f79d65','#f9dc5c','#e8ac65','#e76f51','#ef233c','#b7094c'] #color palette
	sns.set_style(style="whitegrid") # set seaborn plot style
	sizes= wordcount[wordcount.columns[1]]# proportions of the categories
	label= list(wordcount["index"])
	unique = set(label).intersection(set(label))
	sizes = list(sizes)
	con.close()
	return sizes,label,unique,wordcldtxt



def wordtree_filter(connid, fromdate, todate):
	if connid == "NO":
		sql=f"select id,fulltranscript from calltrans where calldate BETWEEN '{fromdate}' and '{todate}'"
	else:
		sql=f"select id,fulltranscript from calltrans where connid='{connid}'"
	con=connection()
	df=pd.read_sql(sql, con)
	wordcldtxt = ' '.join(df['fulltranscript']).lower().split()
	wordcount=pd.Series(' '.join(df['fulltranscript']).lower().split()).value_counts()[:100]
	wordcount=wordcount.reset_index()
	colors=['#fae588','#f79d65','#f9dc5c','#e8ac65','#e76f51','#ef233c','#b7094c'] #color palette
	sns.set_style(style="whitegrid") # set seaborn plot style
	sizes= wordcount[wordcount.columns[1]]# proportions of the categories
	label= list(wordcount["index"])
	unique = set(label).intersection(set(label))
	sizes = list(sizes)
	con.close()
	return sizes,label,unique,wordcldtxt



# def reports(request):
# 	user = request.session.get('opoid')
# 	if user is None:
# 		return redirect('/')
# 	else:
# 		conn = connection()
# 		getdata = request.POST.get('searchdata')
# 		firstdate = request.POST.get('first_date')
# 		lastdate = request.POST.get('last_date')
# 		my_data = []
# 		df_get_date = pd.read_sql(f"SELECT * FROM calltrans WHERE calldate BETWEEN DATE_FORMAT('{firstdate}', '%Y-%m-%d') AND DATE_FORMAT('{lastdate}', '%Y-%m-%d');",conn)
# 		conn.close()
# 		for i in df_get_date.to_dict('records'):
# 			my_data.append(i)

	
# 		conn.close()
# 		context = {'data':my_data,'fdate':firstdate,'ldate':lastdate}
# 		return render(request,'reports.html',context)

def getsubdisp(request):
	selectedDisp = request.GET.get('d')
	conn = connection()
	df_get_data = pd.read_sql(f"""select distinct subdisposition from calltrans where date(calldate)='2023-12-27' and disposition='{selectedDisp}';""",conn)
	# query = """ SELECT DISTINCT subdisposition FROM calltrans WHERE calldate >= %s AND calldate < %s AND disposition = %s;"""
	# params = ('2023-12-27 00:00:00', '2023-12-28 00:00:00', selectedDisp)
	# df_get_data = pd.read_sql(query, conn, params=params)
	df_get_data = df_get_data.to_dict('records')
	#select distinct subdisposition from calltrans where date(calldate)='2023-12-27' and disposition='Interested'
	return HttpResponse(json.dumps({'data':df_get_data}), content_type="application/json")

def disp_getdates(start_date_str,end_date_str,typex):
    start_date = dt.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Calculate the number of days in the date range
    num_days = (end_date - start_date).days + 1

    # Create an empty list to store the substrings
    date_substrings = []

    # Generate the substrings for each date within the specified range
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        formatted_date = current_date.strftime('%Y-%m-%d')
        #substring = f"CAST((SUM(CASE WHEN ta.{typex} = 'MET' THEN 1 ELSE 0 END) / COUNT(*)  * 100 )as decimal(18,2)) AS '{formatted_date}',"
        substring = f"CAST((SUM(CASE WHEN ta.{typex} = 'MET' AND c.calldate = '{formatted_date}' THEN 1 ELSE 0 END) / COUNT(CASE WHEN c.calldate = '{formatted_date}' THEN 1 ELSE NULL END) * 100) AS DECIMAL(18, 2)) AS '{formatted_date}',"
        date_substrings.append(substring)

    # Join the substrings into a single string
    result_string = " ".join(date_substrings)
    return result_string[0:-1]


# ========================== new Cloud word report Added by Junaid 19 June 2024 Block Started ==========================

def reports(request):
	user = request.session.get('opoid')
	if user is None:
		return redirect('/')
	else:
		conn = connection()
		getdata = request.POST.get('searchdata')
		firstdate = request.POST.get('first_date')
		lastdate = request.POST.get('last_date')
		print(getdata,firstdate,lastdate)
		my_data = []
		df_get_data = None
		downloadpath = None

		if getdata == '1':
			# df_get_data = pd.read_sql(f"select c.connid,c.calldate,c.opoid,c.processname,c.disposition,c.subdisposition,c.total_duration, ta.score,c.positivescore,c.negativescore,c.neutralscore,c.fulltranscript,ta.accountvalidation,ta.appropriatecallclosing,ta.appropriateprobing,ta.datacapturing_remarks,ta.disposition,ta.empathy,ta.grammarandsentenceformation,ta.purposeofcall,ta.rpc,ta.self_companyintroduction,ta.standardgreeting from calltrans c join sbivoiceanalytics.sbitest_ai ta on c.connid =ta.connid where c.calldate between DATE_FORMAT('{firstdate}', '%Y-%m-%d') AND DATE_FORMAT('{lastdate}', '%Y-%m-%d');",conn)
			query = """SELECT c.connid, c.calldate, c.opoid,c.processname,c.disposition,c.subdisposition,c.total_duration,ta.score,c.positivescore,c.negativescore,c.neutralscore,c.fulltranscript,ta.accountvalidation, ta.appropriatecallclosing,ta.appropriateprobing,ta.datacapturing_remarks, ta.disposition AS ta_disposition, ta.empathy, ta.grammarandsentenceformation,ta.purposeofcall,ta.rpc,ta.self_companyintroduction, ta.standardgreeting FROM calltrans c JOIN sbivoiceanalytics.sbitest_ai ta ON  c.connid = ta.connid WHERE  c.calldate BETWEEN %s AND %s; """
			df_get_data = pd.read_sql(query, conn, params=[firstdate, lastdate])
			#df_get_data = df_get_data.to_dict('records')
			filename = random.randint(10000,99999)
			df_get_data = df_get_data.to_excel(f'media/DumpReport_{filename}.xlsx', index=False)
			downloadpath = f"/media/DumpReport_{filename}.xlsx"
			 
		elif getdata =='2':
			query = """SELECT c.opoid AS EmployeeID,COUNT(*) AS Total_Calls, AVG(c.silence_sec) AS Silence_duration, ROUND(AVG(sa.score), 2) AS CQ_scores,ROUND(AVG(c.positivescore), 2) AS Positive,ROUND(AVG(c.negativescore), 2) AS Negative,ROUND(AVG(c.neutralscore), 2) AS Neutral FROM calltrans c JOIN sbitest_ai sa ON c.connid = sa.connid  WHERE  c.calldate BETWEEN %s AND %s GROUP BY c.opoid;"""
			df_get_data = pd.read_sql(query, conn, params=[firstdate, lastdate])
# 			df_get_data = pd.read_sql(f"""Select c.opoid as EmployeeID,
# count(*) as Total_Calls,
# avg(c.silence_sec) as Silence_duration,
# FORMAT(avg(sa.score),2) as CQ_scores,
# FORMAT(avg(c.positivescore),2) as Positive,
# FORMAT(avg(c.negativescore),2) as Negative ,
# FORMAT(avg(c.neutralscore),2) as Neutral 
# from calltrans c join sbitest_ai sa on c.connid = sa.connid  
# WHERE calldate BETWEEN  DATE_FORMAT('{firstdate}', '%Y-%m-%d') AND DATE_FORMAT('{lastdate}', '%Y-%m-%d') group by c.opoid""",conn)

			df_get_data = df_get_data.to_dict('records')
		elif getdata =='3':
			query = """SELECT  c.disposition AS Disposition,c.subdisposition AS SubDisposition,COUNT(*) AS Total_count,ROUND(SUM(c.total_duration) / 1000, 2) AS Call_duration,AVG(c.silence_sec) AS Silence_duration,ROUND(AVG(sa.score), 2) AS CQ_scores,ROUND(AVG(c.positivescore), 2) AS Positive,ROUND(AVG(c.negativescore), 2) AS Negative,ROUND(AVG(c.neutralscore), 2) AS Neutral FROM calltrans c JOIN sbitest_ai sa ON c.connid = sa.connid WHERE c.calldate BETWEEN %s AND %s GROUP BY c.disposition, c.subdisposition; """
			df_get_data = pd.read_sql(query, conn, params=[firstdate, lastdate])
			df_get_data = df_get_data.to_dict('records')
# 			df_get_data = pd.read_sql(f"""Select c.disposition as Disposition,c.subdisposition as SubDisposition,count(*) as Total_count,ROUND(sum(c.total_duration)/1000,2) as Call_duration,avg(c.silence_sec) as Silence_duration,
# FORMAT(avg(sa.score),2) as CQ_scores,FORMAT(avg(c.positivescore),2) as Positive,FORMAT(avg(c.negativescore),2) as Negative ,
# FORMAT(avg(c.neutralscore),2) as Neutral from calltrans c join sbitest_ai sa on c.connid = sa.connid WHERE calldate  BETWEEN DATE_FORMAT('{firstdate}', '%Y-%m-%d') AND DATE_FORMAT('{lastdate}', '%Y-%m-%d')  group by disposition,subdisposition;""",conn)
		elif getdata =='4':
		 	# df_get_data = pd.read_sql(f"""Select c.subdisposition as Disposition,count(*) as Total_count,ROUND(sum(c.total_duration)/1000,2) as Call_duration,avg(c.silence_sec) as Silence_duration, FORMAT(avg(sa.score),2) as CQ_scores,FORMAT(avg(c.positivescore),2) as Positive,FORMAT(avg(c.negativescore),2) as Negative , FORMAT(avg(c.neutralscore),2) as Neutral from calltrans c join sbitest_ai sa on c.connid = sa.connid WHERE calldate  BETWEEN DATE_FORMAT('{firstdate}', '%Y-%m-%d') AND DATE_FORMAT('{lastdate}', '%Y-%m-%d')  group by subdisposition;""",conn)
			query = """ SELECT c.subdisposition AS Disposition,COUNT(*) AS Total_count,ROUND(SUM(c.total_duration) / 1000, 2) AS Call_duration,AVG(c.silence_sec) AS Silence_duration,ROUND(AVG(sa.score), 2) AS CQ_scores,ROUND(AVG(c.positivescore), 2) AS Positive,ROUND(AVG(c.negativescore), 2) AS Negative,ROUND(AVG(c.neutralscore), 2) AS Neutral FROM  calltrans c JOIN sbitest_ai sa  ON  c.connid = sa.connid  WHERE  c.calldate BETWEEN %s AND %s GROUP BY  c.subdisposition;"""
			df_get_data = pd.read_sql(query, conn, params=[firstdate, lastdate])
			df_get_data = df_get_data.to_dict('records')
		elif getdata == '8':
			# df_get_data = pd.read_sql(f"SELECT WordFinder.opoid, WordFinder.connid, WordFinder.Word_Occurrence, calltrans.fulltranscript, WordFinder.calldate from WordFinder join calltrans on WordFinder.connid = calltrans.connid  where WordFinder.calldate between DATE_FORMAT('{firstdate}', '%Y-%m-%d') AND DATE_FORMAT('{lastdate}', '%Y-%m-%d') and WordFinder.Word_Occurrence!='';",conn)
			query = """ SELECT WordFinder.opoid,WordFinder.connid,WordFinder.Word_Occurrence,calltrans.fulltranscript,WordFinder.calldate FROM WordFinder JOIN calltrans ON WordFinder.connid = calltrans.connid  WHERE WordFinder.calldate BETWEEN %s AND %s AND WordFinder.Word_Occurrence != '';"""
			df_get_data = pd.read_sql(query, conn, params=[firstdate, lastdate])
			#df_get_data = df_get_data.to_dict('records')
			#print(df_get_data)
			reportname='WordCloudReport' 
			filename = random.randint(10000,99999)  
			df_get_data = df_get_data.to_excel(f'media/dumps/WordCloudReport_{filename}.xlsx', index=False)
			downloadpath = f"/media/dumps/WordCloudReport_{filename}.xlsx"
			df_get_data = [{'total_count':filename}]
		elif getdata == '9':
			# df_get_data = pd.read_sql(f"SELECT c.connid, processname, opoid, tlopoid, c.disposition, subdisposition, calltype, t.score, fulltranscript, positivescore, negativescore, neutralscore, calldate, calltime, silence_sec, total_duration, quality_data FROM sbivoiceanalytics.calltrans  c join sbivoiceanalytics.sbitest_ai t on c.connid = t.connid where date(calldate) between '{firstdate}' and '{lastdate}' order by positivescore desc limit 50",conn)
			query = "SELECT c.connid, processname, opoid, tlopoid, c.disposition, subdisposition, calltype, t.score, fulltranscript, positivescore, negativescore, neutralscore, calldate, calltime, silence_sec, total_duration, quality_data FROM test_sbivoiceanalytics.calltrans c JOIN test_sbivoiceanalytics.sbitest_ai t ON c.connid = t.connid WHERE c.calldate BETWEEN %s AND %s ORDER BY c.positivescore DESC LIMIT 50;"
			df_get_data = pd.read_sql(query, conn, params=[firstdate, lastdate])

			#df_get_data = df_get_data.to_dict('records')
			#print(df_get_data)
			filename = random.randint(10000,99999) 
			reportname='Top_50_positivescore' 
			df_get_data = df_get_data.to_excel(f'media/dumps/Top_50_positivescore{filename}.xlsx', index=False)
			downloadpath = f"/media/dumps/Top_50_positivescore{filename}.xlsx"
			df_get_data = [{'total_count':filename}]
		elif getdata == '10':
			# df_get_data = pd.read_sql(f"SELECT c.connid, processname, opoid, tlopoid, c.disposition, subdisposition, calltype, t.score, fulltranscript, positivescore, negativescore, neutralscore, calldate, calltime, silence_sec, total_duration, quality_data FROM sbivoiceanalytics.calltrans  c join sbivoiceanalytics.sbitest_ai t on c.connid = t.connid where date(calldate) between '{firstdate}' and '{lastdate}' order by negativescore desc limit 50",conn)
			query = "SELECT c.connid, processname, opoid, tlopoid, c.disposition, subdisposition, calltype, t.score, fulltranscript, positivescore, negativescore, neutralscore, calldate, calltime, silence_sec, total_duration, quality_data FROM sbivoiceanalytics.calltrans c JOIN sbivoiceanalytics.sbitest_ai t ON c.connid = t.connid WHERE c.calldate BETWEEN %s AND %s ORDER BY c.negativescore DESC LIMIT 50;"
			df_get_data = pd.read_sql(query, conn, params=[firstdate, lastdate])

			#df_get_data = df_get_data.to_dict('records')
			#print(df_get_data)
			filename = random.randint(10000,99999)  
			reportname='Top_50_Negativescore'
			df_get_data = df_get_data.to_excel(f'media/dumps/Top_50_Negativescore{filename}.xlsx', index=False)
			downloadpath = f"/media/dumps/Top_50_Negativescore{filename}.xlsx"
			df_get_data = [{'total_count':filename}]
		
		elif getdata == '4':
			print("----in----")
			start_date_str = firstdate
			end_date_str = lastdate

			posdatestr=getdates(start_date_str, end_date_str,'positivescore')
			negativestr=getdates(start_date_str, end_date_str,'negativescore')
			neutralstr=getdates(start_date_str, end_date_str,'neutralscore')

			querypos=f"""SELECT opoid as EmployeeID,'Positive' AS `Sentiment_scores`,{posdatestr}
			FROM calltrans where calldate between '{start_date_str}' and '{end_date_str}' GROUP BY EmployeeID UNION ALL """

			 
			queryneg=f"""SELECT opoid as EmployeeID,'Negative' AS `Sentiment_scores`,{negativestr} FROM calltrans where calldate between '{start_date_str}' and '{end_date_str}'
			GROUP BY EmployeeID UNION ALL """

			queryneutr=f"""SELECT opoid as EmployeeID,'Neutral' AS `Sentiment_scores`,{neutralstr}  FROM calltrans where calldate between '{start_date_str}' and '{end_date_str}'
			GROUP BY EmployeeID ORDER BY EmployeeID;"""

			


			qry=querypos+queryneg+queryneutr

			df=pd.read_sql(qry,conn)

			# query = """SELECT opoid AS EmployeeID,'Positive' AS Sentiment_scores,{posdatestr} AS Score FROM calltrans WHERE calldate BETWEEN %s AND %s GROUP BY opoid UNION ALL SELECT opoid AS EmployeeID,'Negative' AS Sentiment_scores, {negativestr} AS Score FROM calltrans WHERE calldate BETWEEN %s AND %s GROUP BY  opoid UNION ALL SELECT opoid AS EmployeeID,'Neutral' AS Sentiment_scores,{neutralstr} AS Score FROM calltrans WHERE calldate BETWEEN %s AND %s GROUP BY opoid ORDER BY  EmployeeID;"""
			# query = query.format(
			# 				posdatestr=getdates(start_date_str, end_date_str, 'positivescore'),
			# 				negativestr=getdates(start_date_str, end_date_str, 'negativescore'),
			# 				neutralstr=getdates(start_date_str, end_date_str, 'neutralscore')
			# 			)
			# df = pd.read_sql(query, conn, params=[start_date_str, end_date_str, start_date_str, end_date_str, start_date_str, end_date_str])



			dy_column_name = df.columns
			#df_get_data = df.to_dict('records')
			df_get_data = df.to_html(classes="table table-stripe table-hover mytable", index=False)

		elif getdata == '5':
			print("----in----")
			start_date_str = firstdate
			end_date_str = lastdate
			attrlist = ['Opening', 'Self_Company_Introduction', 'Verification', 'RPC', 'Disclaimer', 'Assertiveness_Confident', 'Enthu_Energy', 'Professionalism_Casual', 'Speech_Clarity_ClearExplanation', 'Pace_Customer_Language', 'Personalization', 'Active_Listening_No_Repetition', 'Dead_Air', 'Hold_Protocol', 'Negotiation_Skils', 'Urgency_Creation', 'Objection_Handling_Rebuttals', 'Due_Date_communication', 'Summarization', 'Appropriate_closing', 'Complete_Information', 'Correct_Information', 'PTP_Detail_FPTP', 'Script_Adherence', 'Proactive_Information', 'Data_Capturing_Remarks']

			qrylist = []

			for i in range(len(attrlist)):
			     qry = disp_getdates(start_date_str, end_date_str, f'{attrlist[i]}')
			     #print(qry)
			     if i == 25:
			         querypos = f"""select c.opoid,'{attrlist[i]}' as 'Attribute_name', {qry} from calltrans 
			             c join VAmodel_db.test_ai ta on c.connid = ta.connid 
			             where c.calldate between '{start_date_str}' and '{end_date_str}'
			             group by c.opoid """
			         qrylist.append(querypos)
			         
			     else:
			         querypos = f"""select c.opoid,'{attrlist[i]}' as 'Attribute_name', {qry} from calltrans 
			        c join VAmodel_db.test_ai ta on c.connid = ta.connid 
			        where c.calldate between '{start_date_str}' and '{end_date_str}'
			        group by c.opoid UNION ALL"""
			         qrylist.append(querypos)


			#print(qrylist[0])
			totalqry = ''
			for i in range(26):
			    totalqry += qrylist[i] + " "
			#print(totalqry)
			df = pd.read_sql(totalqry, conn)
			
			#df_get_data = df.to_dict('records')
			df_get_data = df.to_html(classes="table table-stripe table-hover mytable", index=False)
        
		elif getdata == '6':
			print("---in-----")
			start_date_str = firstdate
			end_date_str = lastdate
			attrlist = ['Opening', 'Self_Company_Introduction', 'Verification', 'RPC', 'Disclaimer', 'Assertiveness_Confident', 'Enthu_Energy', 'Professionalism_Casual', 'Speech_Clarity_ClearExplanation', 'Pace_Customer_Language', 'Personalization', 'Active_Listening_No_Repetition', 'Dead_Air', 'Hold_Protocol', 'Negotiation_Skils', 'Urgency_Creation', 'Objection_Handling_Rebuttals', 'Due_Date_communication', 'Summarization', 'Appropriate_closing', 'Complete_Information', 'Correct_Information', 'PTP_Detail_FPTP', 'Script_Adherence', 'Proactive_Information', 'Data_Capturing_Remarks']

			qrylist = []

			for i in range(len(attrlist)):
			     qry = disp_getdates(start_date_str, end_date_str, f'{attrlist[i]}')
			     #print(qry)
			     if i == 25:
			         querypos = f"""select c.disposition,'{attrlist[i]}' as 'Attribute_name', {qry} from calltrans 
			             c join VAmodel_db.test_ai ta on c.connid = ta.connid 
			             where c.calldate between '{start_date_str}' and '{end_date_str}'
			             group by c.disposition """
			         qrylist.append(querypos)
			         
			     else:
			         querypos = f"""select c.disposition,'{attrlist[i]}' as 'Attribute_name', {qry} from calltrans 
			        c join VAmodel_db.test_ai ta on c.connid = ta.connid 
			        where c.calldate between '{start_date_str}' and '{end_date_str}'
			        group by c.disposition UNION ALL"""
			         qrylist.append(querypos)


			#print(qrylist[0])
			totalqry = ''
			for i in range(26):
			    totalqry += qrylist[i] + " "
			#print(totalqry)
			df = pd.read_sql(totalqry, conn)
			#df_get_data = df.to_dict('records')
			df_get_data = df.to_html(classes="table table-stripe table-hover mytable", index=False)
			#print(df_get_data)

		elif getdata == '7':
			print("---in-----")
			start_date_str = firstdate
			end_date_str = lastdate
			attrlist = ['Opening', 'Self_Company_Introduction', 'Verification', 'RPC', 'Disclaimer', 'Assertiveness_Confident', 'Enthu_Energy', 'Professionalism_Casual', 'Speech_Clarity_ClearExplanation', 'Pace_Customer_Language', 'Personalization', 'Active_Listening_No_Repetition', 'Dead_Air', 'Hold_Protocol', 'Negotiation_Skils', 'Urgency_Creation', 'Objection_Handling_Rebuttals', 'Due_Date_communication', 'Summarization', 'Appropriate_closing', 'Complete_Information', 'Correct_Information', 'PTP_Detail_FPTP', 'Script_Adherence', 'Proactive_Information', 'Data_Capturing_Remarks']

			qrylist = []

			for i in range(len(attrlist)):
			     qry = disp_getdates(start_date_str, end_date_str, f'{attrlist[i]}')
			     #print(qry)
			     if i == 25:
			         querypos = f"""select c.opoid,'{attrlist[i]}' as 'Attribute_name', {qry} from calltrans 
			             c join VAmodel_db.test_ai ta on c.connid = ta.connid 
			             where c.calldate between '{start_date_str}' and '{end_date_str}'
			             group by c.opoid """
			         qrylist.append(querypos)
			         
			     else:
			         querypos = f"""select c.opoid,'{attrlist[i]}' as 'Attribute_name', {qry} from calltrans 
			        c join VAmodel_db.test_ai ta on c.connid = ta.connid 
			        where c.calldate between '{start_date_str}' and '{end_date_str}'
			        group by c.opoid UNION ALL"""
			         qrylist.append(querypos)


			#print(qrylist[0])
			totalqry = ''
			for i in range(26):
			    totalqry += qrylist[i] + " "
			#print(totalqry)
			df = pd.read_sql(totalqry, conn)
			#df_get_data = df.to_dict('records')
			df_get_data = df.to_html(classes="table table-stripe table-hover mytable", index=False)
			#print(df_get_data)

		
		# ========================== new Cloud word report Added by Junaid 19 June 2024 Block Started ==========================
		elif getdata == '11':
			
			# df_get_data = pd.read_sql(f"SELECT WordFinder.opoid, WordFinder.connid, WordFinder.Word_Occurrence, calltrans.fulltranscript, WordFinder.calldate from WordFinder join calltrans on WordFinder.connid = calltrans.connid  where WordFinder.calldate between DATE_FORMAT('{firstdate}', '%Y-%m-%d') AND DATE_FORMAT('{lastdate}', '%Y-%m-%d') and WordFinder.Word_Occurrence!='';",conn)
			# df_get_data = pd.read_sql(f"SELECT * FROM sbivoiceanalytics.word_search_results where date(calldate) between '2024-05-15' and '2024-05-15'",conn)
			
			# df_get_data = pd.read_sql(f"SELECT * FROM sbivoiceanalytics.word_search_results where date(calldate) between '{firstdate}' and '{lastdate}';",conn)
			query = """SELECT * FROM sbivoiceanalytics.word_search_results WHERE calldate BETWEEN %s AND %s;"""
			df_get_data = pd.read_sql(query, conn, params=[firstdate, lastdate])



			#df_get_data = df_get_data.to_dict('records')
			#print(df_get_data)
			reportname=f'WordCloudReport_{firstdate}_to_{lastdate}' 
			filename = random.randint(10000,99999)  
			# df_get_data = df_get_data.to_excel(f'/var/www/html/VA_SBI/voiceanalytucs_sbi/media/dumps/WordCloudReport_{filename}.xlsx', index=False)
			df_get_data = df_get_data.to_excel(f'media/dumps/{reportname}_{filename}.xlsx', index=False)
			
			downloadpath = f"media/dumps/{reportname}_{filename}.xlsx"
			df_get_data = [{'total_count':filename}]
			# ========================== new Cloud word report Added by Junaid 19 June 2024 Block Ended ==========================


		else:
			pass

		# for i in df_get_date.to_dict('records'):
		# 	my_data.append(i)		
		# # print(df_get_date.to_dict('records'))
		conn.close()

		context = {'data':df_get_data,'searchdata':getdata,'fdate':firstdate,'ldate':lastdate,'downloadlink':downloadpath}
		return render(request,'reports.html',context)




def search(request):
	user = request.session.get('opoid')
	print(user)
	if user is None:
		return redirect('/')
	else:
		conn = connection()
		get_opoid_data = None;
		get_opoid_data = request.POST.get('searchdata')
		startdate = request.POST.get('startdata')
		enddate = request.POST.get('enddata')
		print(get_opoid_data, startdate,enddate)

		if get_opoid_data != None:
			if 'OPO' in str(get_opoid_data):
				print("this is opoid enter")
				callsql = pd.read_sql(f"CALL SelectAllCustomers('{get_opoid_data}', '', '{str(startdate)}', '{str(enddate)}', 'OPOID')",conn)
				filename = random.randint(10000,99999)
				df_get_data = callsql.to_excel(f'media/DumpReport_{filename}.xlsx', index=False)
				downloadpath = f"/media/DumpReport_{filename}.xlsx"
				
				#print(callsql.to_dict('records'))
			else:
				print("this is connid enter")
				callsql = pd.read_sql(f"CALL SelectAllCustomers('', '{get_opoid_data}', '{str(startdate)}', '{str(enddate)}', 'Connid')",conn)
				filename = random.randint(10000,99999)
				df_get_data = callsql.to_excel(f'media/DumpReport_{filename}.xlsx', index=False)
				downloadpath = f"/media/DumpReport_{filename}.xlsx"
				#print(callsql.to_dict('records'))

			conn.close()
			context = {'data':callsql.to_dict('records'),'filter_count':len(callsql.to_dict('records')),'startdate':startdate,'enddate':enddate,'downloadpath':downloadpath}
			return render(request,'search.html',context)
		else:
			return render(request,'search.html')


# def join_chat_view(chat_array):
# 	chat_view = []
# 	for i, chat in enumerate(chat_array):
		
# 		if i == 0:
# 			chat_view.append({"speaker": chat["speaker"], "words": [chat["word"]]})

# 		elif chat_view[-1]["speaker"] == chat["speaker"]:
# 			chat_view[-1]["words"].append(chat["word"])
# 		else:
# 			chat_view.append({"speaker": chat["speaker"], "words": [chat["word"]]}) 
# 	return chat_view


#new function added by junaid 21 May 2024
def join_chat_view(chat_array):
	chat_view = []
	for i, chat in enumerate(chat_array):
		if i == 0:
			chat_view.append({"speaker": chat["speaker"], "words": [chat["word"]]})
 
		elif chat_view[-1]["speaker"] == chat["speaker"]:
			chat_view[-1]["words"].append(chat["word"])
		else:
			chat_view.append({"speaker": chat["speaker"], "words": [chat["word"]]}) 
	return chat_view

	
#new function added by junaid 21 May 2024




def replace_apostrophe(text):
    pattern = r'\b(\w+)"\b'
    replaced_text = re.sub(pattern, r"\1", text)
    return replaced_text


# # code added by junaid 21 May 2024
# def data_formatter(data):
#      # Using regular expressions to extract individual words and their attributes
#      pattern = r'Word\(word="([^"]+)", start=([^,]+), end=([^,]+), confidence=([^,]+), punctuated_word="([^"]+)", speaker=([^,]+), speaker_confidence=([^,]+), sentiment=([^,]+), sentiment_score=([^,]+)\)'

#      word_list = re.findall(pattern, data)

#      data = [Word(*word_attrs) for word_attrs in word_list]

#      converted = []
#      for word in data:

#           if word.__dict__['speaker'] is None :
#                del word.__dict__['speaker']
          
#           if word.__dict__['speaker_confidence'] is None :
#                del word.__dict__['speaker_confidence']
          
#           if word.__dict__['sentiment'] is None :
#                del word.__dict__['sentiment']
          
#           if word.__dict__['sentiment_score'] is None :
#                del word.__dict__['sentiment_score']

#           converted.append(word.__dict__)

#      return converted
# # code added by junaid 21 May 2024




# ===================== code added by junaid 11 june 2024 Block Started
# function work with data_formatter class Word 
def data_formatter(data):
    # Define patterns for different data formats
	pattern1 = r'Word\(word="([^"]+)", start=([^,]+), end=([^,]+), confidence=([^,]+), punctuated_word="([^"]+)", speaker=([^,]+), speaker_confidence=([^,]+), sentiment=([^,]+), sentiment_score=([^,]+)\)'
	pattern2 = r'\{.*?\}'
    # Try matching the data with each pattern
	match1 = re.findall(pattern1, data)
	match2 = re.findall(pattern2, data)
	
	if match1:
		data = [Word(*word_attrs) for word_attrs in match1]
		converted = []
		for word in data:
			if word.__dict__['speaker'] is None :
				del word.__dict__['speaker']
			
			if word.__dict__['speaker_confidence'] is None :
				del word.__dict__['speaker_confidence']
				
			if word.__dict__['sentiment'] is None :
				del word.__dict__['sentiment']
				
			if word.__dict__['sentiment_score'] is None :
				del word.__dict__['sentiment_score']
				
			converted.append(word.__dict__)
			
		return converted
	
	elif match2:
		converted = []
		for word_data in match2:
			word_attrs = eval(word_data)
			word = Word(**word_attrs)
			word_dict = word.__dict__
			for key, value in list(word_dict.items()):
				if value is None:
					del word_dict[key]
			converted.append(word_dict)
		
		return converted
    
# ===================== code added by junaid 11 june 2024 Block Ended

def result_data(request):
	conn = connection()
	connid = request.POST.get('search_tearm')
	#print(connid)
	# data = pd.read_sql(f"select *, cast(positivescore as decimal(4,2)) as positive_score, cast(negativescore  as decimal(4,2)) as negative_score, cast(positivescore as decimal(4,2)) as neutral_score from calltrans WHERE connid = '{connid}';",conn)
	query = """SELECT *, CAST(positivescore AS DECIMAL(4,2)) AS positive_score, CAST(negativescore AS DECIMAL(4,2)) AS negative_score, CAST(neutralscore AS DECIMAL(4,2)) AS neutral_score FROM calltrans WHERE connid = %s;"""
	data = pd.read_sql(query, conn, params=[connid])
	
	fulltrans = data['fulltranscript'][0]
	#print(data)
	# fulltranslist = fulltrans.split(" ")
	# dt = data['wordssummary'][0]
	# dt2 = replace_apostrophe(dt)
	# dt3 = json.loads(dt2)
	# chatdata = join_chat_view(dt3)

	#---------- Added By Junaid 21 May 2024 ---------
	calldate = data['calldate'][0]
	# print(calldate)
	#print(data)
	fulltranslist = fulltrans.split(" ")
	dt = data['wordssummary'][0]
	dt1 = replace_apostrophe(dt)
	converted_data = data_formatter(dt1)
	chatdata = join_chat_view(converted_data)

	#---------- Added By Junaid 21 May 2024 --------- 

	#print(chatdata)
	# print("=========")
	# print(data['filepath'][0])
	# print("-------file path----------")
	calldate = data['calldate'][0]
	filepath_str = data['filepath'][0]
	print(filepath_str[filepath_str.rfind('call_'):])
	date_folder_str = str(calldate)
	filename_str = str(data['filepath'][0])
	print("filename: ", filepath_str)
	# print(data['filepath'][0][48:])
	# print(filepath_str.find(str(calldate)))
	audiopath = os.path.join(f"/sbi/{date_folder_str}/{filepath_str[filepath_str.rfind('call_'):]}")
	audiopath = audiopath.replace(".wav" , ".mp3")
	# audiopath = os.path.join(f"/sbi/{date_folder_str}/")
	try:
		with open(audiopath, "rb") as audio_file:
			encoded_audio = base64.b64encode(audio_file.read())
	except Exception as e:
		encoded_audio = None

	# print(encoded_audio)	
		
	#print(fulltranslist)
	print("==================")
	
	# negative_words = ["good", "evening", "dominos", "place", "problem", "receive", "but","complaint","worry","ok","order","बहुत","कैसे","address","no","नहीं","but"];

	negative_words = ["Benefits", "CallHistory", "CIBIL", "Creditcard", "DMet", "Debitcard", "DGHCovidQuestionery","Duedate","EmandateService","EmailID","Frequencymode","FundValue","Laps","Latefee","Late","Maturity","Medicalfee" , "Oncall" , "Onlinepayment" , "Paykroge" , "Paymentterm" , "Re-debit" , "Registration" , "Revival" , "SmartcareApp" , "SMS" , "Status" , "SumAssured" , "TechnicalLaps" , "Tollfreenumber" , "Tradistionpolicy(Endonment)" , "TrainingandQuality" , "UlipPolicy" , "Waiveoff" , "Website"];
	
	common_word = set(negative_words).intersection(fulltranslist)

	if not common_word:
		common_word = ""

	#print(common_word)
	wd = str(common_word).replace("'",'')
	
	transcriptdata = data['fulltranscript'][0]
	print("+++++++")
	#print(fulltranscript)
	print("+++++++")
	sizes,label,unique,wordcldtxt = wordtree(connid)
	img = generate_wordcloud(wordcldtxt)


	# quality attribute
	
	# quality_attr = pd.read_sql(f"select accountvalidation, appropriatecallclosing, appropriateprobing,datacapturing_remarks, disposition, empathy, grammarandsentenceformation,purposeofcall, rpc, self_companyintroduction, standardgreeting,score from sbitest_ai where connid='{connid}' limit 1",conn)
	query = """SELECT accountvalidation, appropriatecallclosing, appropriateprobing, datacapturing_remarks, disposition, empathy, grammarandsentenceformation, purposeofcall, rpc, self_companyintroduction, standardgreeting, score FROM sbitest_ai WHERE connid = %s;"""
	params = (connid,)
	quality_attr = pd.read_sql(query, conn, params=params)
	quality_attr = quality_attr.to_dict('records')
	#print(quality_attr)
	conn.close()

	
	
	# context = {'audiopath':str(audiopath),'data':data,'msg':chatdata,'negativeword':wd[1:-1],'transcript':transcriptdata,'audiodt':str(encoded_audio)[2:-1],"wordcloud":str(img)[2:-3],'attribut_val':quality_attr}
	context = {'audiopath':str(audiopath),'data':data,'msg':chatdata,'negativeword':wd[1:-1],'transcript':transcriptdata,'audiodt':str(encoded_audio)[2:-1],"wordcloud":str(img)[2:-3],'attribut_val':quality_attr}
	return render(request,'resultofdata.html', context)

	

def user_logout(request):
	logout(request) 
	return redirect('/')

def formdata(request):
	if request.method == "POST":
		form = AgentDataForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('dashboard')
	else:
		context = {'data':AgentDataForm()}
		return render(request,'form.html', context)


#positive call 
def positive_call(request):
	conn = connection()
	fromdate = request.GET.get('fromdate')
	todate = request.GET.get('todate')
	date = request.POST.get('datefilter')
	print(date)

	if fromdate is not None: #old condition
	# if fromdate != "": # New Confition added by Junaid 17 May 2024

		# pos_call = pd.read_sql(f"SELECT *, cast(positivescore as decimal(18,1)) AS positiveval FROM calltrans WHERE calldate BETWEEN '{fromdate}' and '{todate}'  ORDER BY calldate,positivescore DESC limit 50",conn)
		pos_call = pd.read_sql(""" SELECT *, CAST(positivescore AS DECIMAL(18,1)) AS positiveval  FROM calltrans  WHERE calldate BETWEEN %s AND %s  ORDER BY calldate, positivescore DESC LIMIT 50""", conn, params=(fromdate, todate))
		pos_call['calltime'] = pos_call['calltime'].astype('str').str.split().str[-1]
	else:
		# pos_call = pd.read_sql(f"SELECT *, cast(positivescore as decimal(18,1)) AS positiveval FROM calltrans where calldate >= DATE_SUB(NOW(), INTERVAL 7 DAY) ORDER BY calldate,positivescore DESC limit 50",conn)
		pos_call = pd.read_sql("""SELECT *, CAST(positivescore AS DECIMAL(18,1)) AS positiveval FROM calltrans  WHERE calldate >= CURDATE() - INTERVAL 7 DAY ORDER BY calldate, positivescore DESC  LIMIT 50""", conn)
		pos_call['calltime'] = pos_call['calltime'].astype('str').str.split().str[-1]
	conn.close()
	context = {'data':pos_call.to_dict('records'),'fromdate':fromdate,'todate':todate}
	return render(request,'positivecall.html',context)


#negative call
def negative_call(request):
	conn = connection()
	fromdate = request.GET.get('fromdate')
	todate = request.GET.get('todate')
	date = request.POST.get('datefilter')
	print(date)
	if fromdate is not None:
		# neg_call = pd.read_sql(f"SELECT *, cast(negativescore as decimal(18,1)) AS negativeval FROM calltrans WHERE calldate BETWEEN '{fromdate}' and '{todate}'  ORDER BY calldate,negativescore DESC limit 50",conn)
		neg_call = pd.read_sql(""" SELECT *, CAST(negativescore AS DECIMAL(18,1)) AS negativeval  FROM calltrans  WHERE calldate BETWEEN %s AND %s ORDER BY calldate, negativescore DESC  LIMIT 50""", conn, params=(fromdate, todate))
		neg_call['calltime'] = neg_call['calltime'].astype('str').str.split().str[-1]
	else:
		# neg_call = pd.read_sql(f"SELECT *, cast(negativescore as decimal(18,1)) AS negativeval FROM calltrans WHERE calldate >= DATE_SUB(NOW(), INTERVAL 7 DAY) ORDER BY calldate,negativescore DESC limit 50",conn)
		neg_call = pd.read_sql(""" SELECT *, CAST(negativescore AS DECIMAL(18,1)) AS negativeval  FROM calltrans WHERE calldate BETWEEN %s AND %s ORDER BY calldate, negativescore DESC  LIMIT 50""", conn, params=(fromdate, todate))
		neg_call['calltime'] = neg_call['calltime'].astype('str').str.split().str[-1]
	conn.close()
	context = {'data':neg_call.to_dict('records'),'fromdate':fromdate,'todate':todate}
	return render(request,'negativecall.html',context)


#neutral call 
def neutral_call(request):
	conn = connection()
	fromdate = request.GET.get('fromdate')
	todate = request.GET.get('todate')
	date = request.POST.get('datefilter')
	print(date)
	if fromdate is not None:
		# neu_call = pd.read_sql(f"SELECT *, cast(neutralscore as decimal(18,1)) AS neutralval FROM calltrans WHERE calldate BETWEEN '{fromdate}' and '{todate}'  ORDER BY calldate,neutralscore DESC limit 50",conn)
		neu_call = pd.read_sql(""" SELECT *, CAST(neutralscore AS DECIMAL(18,1)) AS neutralval FROM calltrans WHERE calldate BETWEEN %s AND %s ORDER BY calldate, neutralscore DESC  LIMIT 50""", conn, params=(fromdate, todate))
		# print(neu_call)
		neu_call['calltime'] = neu_call['calltime'].astype('str').str.split().str[-1]
	else:
		# neu_call = pd.read_sql(f"SELECT *, cast(neutralscore as decimal(18,1)) AS neutralval FROM calltrans WHERE calldate >= DATE_SUB(NOW(), INTERVAL 7 DAY) ORDER BY calldate,neutralscore DESC limit 50",conn)
		seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
		neu_call = pd.read_sql("""SELECT *, CAST(neutralscore AS DECIMAL(18,1)) AS neutralval  FROM calltrans WHERE calldate >= %s ORDER BY calldate, neutralscore DESC LIMIT 50""",conn, params=(seven_days_ago,))
		# print(neu_call)
		neu_call['calltime'] = neu_call['calltime'].astype('str').str.split().str[-1]
	conn.close()
	context = {'data':neu_call.to_dict('records'),'fromdate':fromdate,'todate':todate}
	return render(request,'neutralcall.html',context)


def onclick_graph(request):
	conn = connection()
	#fromdate = request.session.get('fromdate_dash')
	#todate = request.session.get('todate_dash')
	label = request.GET.get('label') #.replace(" ", "")
	fromdate=request.GET.get('fromdate') 
	todate=request.GET.get('todate')
	print(label)
  	 
	# pos_call = pd.read_sql(f"SELECT c.*,w.Word_Occurrence FROM sbivoiceanalytics.WordFinder w join calltrans c on w.connid = c.connid where date(w.calldate) between '{fromdate}' and '{todate}' and w.Word_Occurrence='{urllib.parse.unquote(label)}'",conn)
	query = """ SELECT c.connid, c.calldate, c.calltime, w.Word_Occurrence FROM test_sbivoiceanalytics.WordFinder w JOIN calltrans c ON w.connid = c.connid WHERE DATE(w.calldate) BETWEEN %s AND %s AND w.Word_Occurrence = %s"""
	params = [fromdate, todate, urllib.parse.unquote(label)]
	pos_call = pd.read_sql(query, conn, params=params)
	#print(pos_call)
	pos_call['calltime'] = pos_call['calltime'].astype('str').str.split().str[-1]
	conn.close()
	context = {'data':pos_call.to_dict('records'),'label':label,'fromdate':fromdate,'todate':todate}
	return render(request,'onclick_graph.html',context)


#=================== New graph Added By Junaid 19 June 2024 Block Started 

def onclick_graph1(request):
	label = request.GET.get('label')
	fromdate = request.GET.get('fromdate')
	todate = request.GET.get('todate')
	conn = connection()
	# pos_call = pd.read_sql(f"SELECT c.*,w.word FROM sbivoiceanalytics.word_search_results w join calltrans c on w.connid = c.connid where date(w.calldate) between '{fromdate}' and '{todate}' and w.word='{urllib.parse.unquote(label)}'",conn)
	query = """SELECT c.connid, c.calldate, c.calltime, w.word, c.opoid, c.processname FROM sbivoiceanalytics.word_search_results w JOIN calltrans c ON w.connid = c.connid  WHERE DATE(w.calldate) BETWEEN %s AND %s AND w.word = %s"""
	params = [fromdate, todate, urllib.parse.unquote(label)]
	pos_call = pd.read_sql(query, conn, params=params)
	print(pos_call)
	pos_call['calltime'] = pos_call['calltime'].astype('str').str.split().str[-1]

	
	conn.close()
	page_number = request.GET.get('page', 1)
	items_per_page = 10 
	
	paginator = Paginator(pos_call.to_dict('records'), items_per_page)
	
	try:
		pos_call_page = paginator.page(page_number)
	except PageNotAnInteger:
		pos_call_page = paginator.page(1)
	except EmptyPage:
		pos_call_page = paginator.page(paginator.num_pages)
	
	context = {'data1': pos_call_page,'data': pos_call.to_dict('records'),'label': label,'fromdate': fromdate,'todate': todate}
	return render(request, 'onclick_graph.html', context)

#=================== New graph Added By Junaid 19 June 2024 Block Ended


def select_keyword(request):
	conn = connection()
	df_get_data = pd.read_sql(f"""select KeywordID,Keyword from Keywords;""",conn)
	df_get_data = df_get_data.to_dict('records')
	context = {'data':df_get_data}
	return render(request,'keywords.html',context)
	
def select_keyword_edit(request):
	conn = connection()
	df_get_data = pd.read_sql(f"""select KeywordID,Keyword from Keywords;""",conn)
	df_get_data = df_get_data.to_dict('records')
	context = {'data':df_get_data,'ed':'1'}
	return render(request,'keywords.html',context)
	

def select_keyword_save(request):
	conn = connection()
	KeywordID = request.POST.get('KeywordID')
	Keyword = request.POST.get('Keyword')
	#updatekeyword("update Keywords set Keyword='{Keyword}' where  KeywordID='{KeywordID}';")
	cursor = conn.cursor()
	cursor.execute(f"""update Keywords set Keyword='{Keyword}' where  KeywordID='{KeywordID}';""")
	conn.commit()
	# Close the cursor and connection when done
	cursor.close()
	conn.close()
	return redirect ('/select_keyword')
	#return render(request,'keywords.html',context)

def select_keyword_add(request):
	conn = connection()
	 
	Keyword = request.POST.get('Keyword')
	#updatekeyword("update Keywords set Keyword='{Keyword}' where  KeywordID='{KeywordID}';")
	cursor = conn.cursor()
	cursor.execute(f"""insert into Keywords (Keyword) values ('{Keyword}');""")
	conn.commit()
	# Close the cursor and connection when done
	cursor.close()
	conn.close()
	return redirect ('/select_keyword')
	#return render(request,'keywords.html',context)


# def select_keyword_delete(request):
# 	conn = connection()
# 	KeywordID = request.POST.get('KeywordID')
	 
# 	#updatekeyword("update Keywords set Keyword='{Keyword}' where  KeywordID='{KeywordID}';")
# 	cursor = conn.cursor()
# 	print("delete from Keywords where  KeywordID='{KeywordID}';")
# 	cursor.execute(f"""delete from Keywords where KeywordID='{KeywordID}';""")
# 	conn.commit()
# 	# Close the cursor and connection when done
# 	cursor.close()
# 	conn.close() 
# 	return redirect ('/select_keyword')
# 	#return render(request,'keywords.html',context)


# Modified by Junaid 18 June 2024
def select_keyword_delete(request, KeywordID):
	conn = connection()
	# KeywordID = request.POST.get('KeywordID' , None)
	print('KeywordID :',KeywordID)
	print("delete from Keywords where  KeywordID='{KeywordID}';")

	if KeywordID is None :
		return redirect('select_keyword')

	#updatekeyword("update Keywords set Keyword='{Keyword}' where  KeywordID='{KeywordID}';")
	cursor = conn.cursor()
	cursor.execute(f"""delete from Keywords where KeywordID='{KeywordID}';""")
	conn.commit()
	# Close the cursor and connection when done
	cursor.close()
	conn.close() 
	return redirect ('/select_keyword')
	#return render(request,'keywords.html',context)



# agentview funcation

def agent_search(request):
	conn = connection()
	dispo_query = pd.read_sql(f"select disposition from calltrans where date(calldate) >= '2023-12-25' group by disposition ",conn)
	subdispo_query = pd.read_sql(f"select subdisposition from calltrans where date(calldate) >= '2023-12-25' group by subdisposition",conn)

	
	conn.close()
	# query = "CALL GetDispositions(%s);"
	# dispo_query = pd.read_sql(query, conn, params=['2023-12-25',])
	dispo_query = dispo_query.to_dict('records')
	# query = "CALL GetSubDispositions(%s);"
	# subdispo_query = pd.read_sql(query, conn, params=['2023-12-25',])
	subdispo_query = subdispo_query.to_dict('records')
	context = {'data':dispo_query,'subdispo':subdispo_query}
	return render(request,'agent_search.html',context)

def agent_view(request):
	opoid = request.POST.get("opoid")
	disposition_type = request.POST.get("disposition")
	subdisposition_type = request.POST.get("subdisposition")

	fromdate = request.POST.get("fromdate")
	todate = request.POST.get("todate")
	print(opoid, fromdate, todate)
	conn = connection()
	if fromdate == '' and todate == '':
		print("======================")
		agent_senti_data = pd.read_sql(f"SELECT COUNT(id) AS call_evaluted, FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral, FORMAT(AVG(qualityscore),2) as quality_score FROM calltrans where opoid = '{opoid}'", conn)

		# agent_senti_data = pd.read_sql(""" SELECT COUNT(id) AS call_evaluted, ROUND(AVG(positivescore), 2) AS positive, ROUND(AVG(negativescore), 2) AS negative, ROUND(AVG(neutralscore), 2) AS neutral, ROUND(AVG(qualityscore), 2) AS quality_score FROM calltrans WHERE opoid = %s""", conn, params=(opoid,))
		# print(agent_senti_data)
		# query = "CALL GetAgentSentimentData(%s);"
		# agent_senti_data = pd.read_sql(query, conn, params=[opoid])

		agent_senti_data = agent_senti_data.to_dict('records')[0]
		#print(agent_senti_data)
		# agent_call_7_days = pd.read_sql(f"SELECT DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate, COUNT(calldate) AS total_call FROM calltrans WHERE opoid ='{opoid}' and calldate >= DATE_SUB(NOW(), INTERVAL 8 DAY) GROUP BY calldate",conn)
		
		# agent_call_7_days = pd.read_sql(""" SELECT DATE(calldate) AS lastdate, COUNT(*) AS total_call FROM calltrans WHERE opoid = %s AND calldate >= CURDATE() - INTERVAL 7 DAY GROUP BY DATE(calldate)""", conn, params=(opoid,))
		query = "CALL GetAgentCallDataLast7Days(%s);"
		agent_call_7_days = pd.read_sql(query, conn, params=[opoid])
		print(agent_call_7_days)
		agent_call_7_days = agent_call_7_days.to_dict('records')
		#print(agent_call_7_days)

		qty_dt = """
		SELECT 
		FORMAT(((SUM(CASE WHEN t1.accountvalidation = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question1,


		FORMAT(((SUM(CASE WHEN t1.appropriatecallclosing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question4,
		FORMAT(((SUM(CASE WHEN t1.appropriateprobing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question5,


		FORMAT(((SUM(CASE WHEN t1.datacapturing_remarks  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question8,
		FORMAT(((SUM(CASE WHEN t1.disposition  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question9,
		FORMAT(((SUM(CASE WHEN t1.empathy  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question10,


		FORMAT(((SUM(CASE WHEN t1.grammarandsentenceformation = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question13,



		FORMAT(((SUM(CASE WHEN t1.purposeofcall = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question18,
		FORMAT(((SUM(CASE WHEN t1.rpc = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question19,
		FORMAT(((SUM(CASE WHEN t1.self_companyintroduction = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question20,

		FORMAT(((SUM(CASE WHEN t1.standardgreeting = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question22

		FROM sbitest_ai AS t1 join calltrans c on t1.connid = c.connid where
		
		"""
		# qty_dt = """
		# 			SELECT 
		# 				ROUND((SUM(CASE WHEN t1.accountvalidation = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question1,

		# 				ROUND((SUM(CASE WHEN t1.appropriatecallclosing = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question4,
		# 				ROUND((SUM(CASE WHEN t1.appropriateprobing = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question5,

		# 				ROUND((SUM(CASE WHEN t1.datacapturing_remarks = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question8,
		# 				ROUND((SUM(CASE WHEN t1.disposition = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question9,
		# 				ROUND((SUM(CASE WHEN t1.empathy = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question10,

		# 				ROUND((SUM(CASE WHEN t1.grammarandsentenceformation = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question13,

		# 				ROUND((SUM(CASE WHEN t1.purposeofcall = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question18,
		# 				ROUND((SUM(CASE WHEN t1.rpc = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question19,
		# 				ROUND((SUM(CASE WHEN t1.self_companyintroduction = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question20,

		# 				ROUND((SUM(CASE WHEN t1.standardgreeting = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS question22

		# 			FROM sbitest_ai AS t1
		# 			JOIN calltrans c ON t1.connid = c.connid
		# 			WHERE c.opoid = %s AND c.disposition = %s AND c.subdisposition = %s
		# 		"""
		# quality_attr = pd.read_sql(f"{qty_dt} c.opoid ='{opoid}' and c.disposition = '{disposition_type}' and and c.subdisposition = '{subdisposition_type}'",conn)
		
		quality_attr = pd.read_sql(qty_dt, conn, params=(opoid, disposition_type, subdisposition_type))
		print(quality_attr)
		# query = """CALL GetQualityAttributes(%s, %s, %s);"""
		# quality_attr = pd.read_sql(query, conn, params=[opoid, disposition_type, subdisposition_type])
		quality_attr = quality_attr.to_dict('records')

		# qualityScore = pd.read_sql(f"SELECT ROUND(AVG(score),2) as qualityscore from sbitest_ai WHERE connid in(select connid from calltrans where opoid='{opoid}' and disposition='{disposition_type}' and  Date(calldate) BETWEEN '{fromdate}' and '{todate}');",conn)
		
		qualityScore = pd.read_sql(f"SELECT ROUND(AVG(score),2) as qualityscore from sbitest_ai WHERE connid in (select connid from calltrans where opoid='{opoid}' and disposition='{disposition_type}' and subdisposition='{subdisposition_type}' and  Date(calldate) BETWEEN '{fromdate}' and '{todate}');",conn)


	else:
		print("-------")
		#agent_senti_data = pd.read_sql(f"SELECT COUNT(id) AS call_evaluted, FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral, FORMAT(AVG(qualityscore),2) as quality_score FROM calltrans where opoid = '{opoid}' and calldate BETWEEN '{fromdate}' and '{todate}'", conn)
		
		# agent_senti_data = pd.read_sql(f"SELECT COUNT(*) AS call_evaluted, FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral, FORMAT(AVG(sbivoiceanalytics.sbitest_ai.score),2) as quality_score FROM calltrans join sbivoiceanalytics.sbitest_ai on calltrans.connid = sbivoiceanalytics.sbitest_ai.connid where calltrans.opoid ='{opoid}' and date(calltrans.calldate)   BETWEEN '{fromdate}' and '{todate}' and calltrans.disposition='{disposition_type}' and calltrans.subdisposition='{subdisposition_type}'",conn)
		
		
		# agent_senti_data = pd.read_sql("""SELECT COUNT(*) AS call_evaluted,  FORMAT(AVG(ct.positivescore), 2) AS positive,  FORMAT(AVG(ct.negativescore), 2) AS negative,  FORMAT(AVG(ct.neutralscore), 2) AS neutral,  FORMAT(AVG(sa.score), 2) AS quality_score  FROM  calltrans ct JOIN  test_sbivoiceanalytics.sbitest_ai sa ON ct.connid = sa.connid WHERE ct.opoid = %s AND DATE(ct.calldate) BETWEEN %s AND %s AND ct.disposition = %s AND ct.subdisposition = %s""", conn, params=(opoid, fromdate, todate, disposition_type, subdisposition_type))
		# print(agent_senti_data )
		query = """CALL GetAgentSentimentData2(%s, %s, %s, %s, %s);"""
		agent_senti_data = pd.read_sql(query, conn, params=[opoid, disposition_type, subdisposition_type, fromdate, todate])

		agent_senti_data = agent_senti_data.to_dict('records')[0]
		# print(agent_senti_data)
		#agent_call_7_days = pd.read_sql(f"SELECT DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate, COUNT(calldate) AS total_call FROM calltrans WHERE opoid ='{opoid}' and calldate >= DATE_SUB(NOW(), INTERVAL 8 DAY) GROUP BY calldate",conn)
		#agent_call_7_days = pd.read_sql(f"SELECT DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate, COUNT(calldate) AS total_call FROM calltrans WHERE opoid ='{opoid}' and calldate BETWEEN '{fromdate}' and '{todate}' GROUP BY calldate",conn)
		
		# was using
		# agent_call_7_days = pd.read_sql(f" SELECT DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate, COUNT(calldate) AS total_call FROM calltrans join sbivoiceanalytics.sbitest_ai on calltrans.connid = sbivoiceanalytics.sbitest_ai.connid WHERE opoid ='{opoid}' and calldate  BETWEEN '{fromdate}' and '{todate}' and calltrans.disposition='{disposition_type}' and calltrans.subdisposition='{subdisposition_type}' GROUP BY calldate",conn)
		
		# agent_call_7_days = pd.read_sql("""SELECT  DATE_FORMAT(ct.calldate, '%Y-%m-%d') AS lastdate,  COUNT(*) AS total_call  FROM  calltrans ct JOIN  test_sbivoiceanalytics.sbitest_ai sa ON ct.connid = sa.connid WHERE  ct.opoid = %s  AND ct.calldate BETWEEN %s AND %s AND ct.disposition = %s  AND ct.subdisposition = %s  GROUP BY DATE_FORMAT(ct.calldate, '%Y-%m-%d')""", conn, params=(opoid, fromdate, todate, disposition_type, subdisposition_type))
		# print(agent_call_7_days)
		query = """CALL GetAgentCalls7Days2(%s, %s, %s, %s, %s);"""
		agent_call_7_days = pd.read_sql(query, conn, params=[opoid, disposition_type, subdisposition_type, fromdate, todate])

		agent_call_7_days = agent_call_7_days.to_dict('records')
		print("---------------")
		#print(agent_call_7_days)
		#print(len(agent_call_7_days))
		print("---------------")


		# qty_dt = """

		# 		SELECT 
		# FORMAT(((SUM(CASE WHEN t1.accountvalidation = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question1,


		# FORMAT(((SUM(CASE WHEN t1.appropriatecallclosing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question4,
		# FORMAT(((SUM(CASE WHEN t1.appropriateprobing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question5,


		# FORMAT(((SUM(CASE WHEN t1.datacapturing_remarks  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question8,
		# FORMAT(((SUM(CASE WHEN t1.disposition  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question9,
		# FORMAT(((SUM(CASE WHEN t1.empathy  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question10,


		# FORMAT(((SUM(CASE WHEN t1.grammarandsentenceformation = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question13,




		# FORMAT(((SUM(CASE WHEN t1.purposeofcall = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question18,
		# FORMAT(((SUM(CASE WHEN t1.rpc = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question19,
		# FORMAT(((SUM(CASE WHEN t1.self_companyintroduction = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question20,

		# FORMAT(((SUM(CASE WHEN t1.standardgreeting = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question22

		# FROM sbitest_ai AS t1 join calltrans c on t1.connid = c.connid where
		
		# """
		# qty_dt = """
		# 			SELECT 
		# 				FORMAT((SUM(CASE WHEN t1.accountvalidation = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question1,
		# 				FORMAT((SUM(CASE WHEN t1.appropriatecallclosing = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question4,
		# 				FORMAT((SUM(CASE WHEN t1.appropriateprobing = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question5,
		# 				FORMAT((SUM(CASE WHEN t1.datacapturing_remarks = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question8,
		# 				FORMAT((SUM(CASE WHEN t1.disposition = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question9,
		# 				FORMAT((SUM(CASE WHEN t1.empathy = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question10,
		# 				FORMAT((SUM(CASE WHEN t1.grammarandsentenceformation = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question13,
		# 				FORMAT((SUM(CASE WHEN t1.purposeofcall = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question18,
		# 				FORMAT((SUM(CASE WHEN t1.rpc = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question19,
		# 				FORMAT((SUM(CASE WHEN t1.self_companyintroduction = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question20,
		# 				FORMAT((SUM(CASE WHEN t1.standardgreeting = 'MET' THEN 1 ELSE 0 END) / COUNT(*) * 100), 2) AS question22
		# 			FROM sbitest_ai AS t1
		# 			JOIN calltrans AS c ON t1.connid = c.connid
		# 			WHERE c.opoid = %s
		# 			AND c.disposition = %s
		# 			AND c.subdisposition = %s
		# 			AND DATE(c.calldate) BETWEEN %s AND %s
		# 		"""
		# print(f"{qty_dt} c.opoid ='{opoid}' and c.disposition = '{disposition_type}'and c.subdisposition = '{subdisposition_type}' and DATE(c.calldate) BETWEEN '{fromdate}' and '{todate}'")
		# quality_attr = pd.read_sql(f"{qty_dt} c.opoid ='{opoid}' and c.disposition = '{disposition_type}' and c.subdisposition = '{subdisposition_type}' and DATE(c.calldate) BETWEEN '{fromdate}' and '{todate}' ",conn)
		
		# quality_attr = pd.read_sql(qty_dt, conn, params=(opoid, disposition_type, subdisposition_type, fromdate, todate))
		query = """CALL GetQualityAttributes(%s, %s, %s, %s, %s);"""
		quality_attr = pd.read_sql(query, conn, params=[opoid, disposition_type, subdisposition_type, fromdate, todate])
		quality_attr = quality_attr.to_dict('records')
		# qualityScore = pd.read_sql(f"SELECT ROUND(AVG(score),2) as qualityscore from sbitest_ai WHERE connid in(select connid from calltrans where disposition='{disposition_type}' and subdisposition='{subdisposition_type}' and  Date(calldate) BETWEEN '{fromdate}' and '{todate}');",conn)
		query = """SELECT ROUND(AVG(sa.score), 2) AS qualityscore FROM sbitest_ai sa JOIN calltrans ct ON sa.connid = ct.connid WHERE ct.disposition = %s AND ct.subdisposition = %s AND DATE(ct.calldate) BETWEEN %s AND %s"""
		qualityScore = pd.read_sql(query, conn, params=(disposition_type, subdisposition_type, fromdate, todate))

	#dispo_query = pd.read_sql(f'select disposition from calltrans group by disposition',conn) 
	# dispo_query = pd.read_sql(f"select disposition from calltrans where date(calldate) >= '2023-12-25' group by disposition ",conn)
	query = """SELECT disposition FROM calltrans WHERE DATE(calldate) >= %s GROUP BY disposition"""
	params = ('2023-12-25',)
	dispo_query = pd.read_sql(query, conn, params=params)
	# subdispo_query = pd.read_sql(f"select subdisposition from calltrans where date(calldate) >= '2023-12-25' group by subdisposition",conn)
	query = """SELECT subdisposition FROM calltrans  WHERE DATE(calldate) >= %s GROUP BY disposition"""
	params = ('2023-12-25',)
	subdispo_query = pd.read_sql(query, conn, params=params) 


	dispo_query = dispo_query.to_dict('records')
	subdispo_query = subdispo_query.to_dict('records')

	conn.close()
	context = {'data':dispo_query,'subdispo':subdispo_query,'sentiment_data':agent_senti_data,'opoid':opoid,'agent_call_7_days':agent_call_7_days,'attribut_val':quality_attr,'fromdate':fromdate,'todate':todate,'qualityScore':qualityScore.to_dict('records')[0]['qualityscore']}
	return render(request,'agent_search.html',context)

def disposition_analysis(request):
	conn = connection()
	dispo_query = pd.read_sql(f"select disposition from calltrans where date(calldate) >= '2023-12-25' group by disposition ",conn)
	subdispo_query = pd.read_sql(f"select subdisposition from calltrans where date(calldate) >= '2023-12-25' group by subdisposition",conn)
	
	conn.close()
	dispo_query = dispo_query.to_dict('records')
	subdispo_query = subdispo_query.to_dict('records')
	print(dispo_query)
	context = {'data':dispo_query,'subdispo':subdispo_query}
	return render(request,'disposition_analysis.html',context)


def get_disposition_data(request):
	dispoition_type = request.POST.get("disposition")
	dispoition_name = request.POST.get("disposition_name")
	subdispoition_type = request.POST.get("subdisposition")
	subdispoition_name = request.POST.get("subdisposition_name")
	
	start_date = request.POST.get("fromdate")
	end_date = request.POST.get("todate")	
	print(dispoition_type, start_date, end_date)
	conn = connection()
	print("=====")
	print(f"SELECT COUNT(id) AS call_evaluted, FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral, FORMAT(AVG(qualityscore),2) as quality_score FROM calltrans where disposition = '{dispoition_type}' and subdisposition = '{subdispoition_type}' and calldate BETWEEN '{start_date}' and '{end_date}'")
	print("=====")
	dispoition_senti_data = pd.read_sql(f"SELECT COUNT(id) AS call_evaluted, FORMAT(AVG(positivescore),2) AS positive, FORMAT(AVG(negativescore),2) AS negative, FORMAT(AVG(neutralscore),2) as neutral, FORMAT(AVG(qualityscore),2) as quality_score FROM calltrans where disposition = '{dispoition_type}' and subdisposition = '{subdispoition_type}' and calldate BETWEEN '{start_date}' and '{end_date}'", conn)
	# query = """SELECT  COUNT(id) AS call_evaluted, ROUND(AVG(positivescore), 2) AS positive,ROUND(AVG(negativescore), 2) AS negative, ROUND(AVG(neutralscore), 2) AS neutral, ROUND(AVG(qualityscore), 2) AS quality_score FROM  calltrans WHERE  disposition = %s  AND subdisposition = %s  AND calldate BETWEEN %s AND %s"""
	# query = """CALL GetDispositionSentiData(%s, %s, %s, %s)"""
	# dispoition_senti_data = pd.read_sql(query, conn, params=(dispoition_type, subdispoition_type, start_date, end_date))
	dispoition_senti_data = dispoition_senti_data.to_dict('records')[0]
	print(dispoition_senti_data)
	
	disp_7_day_chart = pd.read_sql(f"SELECT DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate, COUNT(calldate) AS total_call FROM calltrans WHERE disposition ='{dispoition_type}' and subdisposition ='{subdispoition_type}' and calldate BETWEEN '{start_date}' and '{end_date}' GROUP BY calldate",conn)
	# query = f"""SELECT DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate, COUNT(calldate) AS total_call FROM calltrans WHERE disposition = '{dispoition_type}' AND subdisposition = '{subdispoition_type}' AND calldate BETWEEN '{start_date}' AND '{end_date}' GROUP BY DATE_FORMAT(calldate, '%Y-%m-%d')"""
	# query = """CALL DispoGetCallCountsByDate(%s, %s, %s, %s)"""
	# params = (dispoition_type, subdispoition_type, start_date, end_date)
	# disp_7_day_chart = pd.read_sql(query, conn, params=params)
	# disp_7_day_chart = pd.read_sql(query, conn)
	# query = """SELECT  DATE_FORMAT(calldate, '%Y-%m-%d') AS lastdate, COUNT(*) AS total_call FROM  calltrans WHERE  disposition = %s AND subdisposition = %s  AND calldate BETWEEN %s AND %s GROUP BY  DATE_FORMAT(calldate, '%Y-%m-%d')"""
	# disp_7_day_chart = pd.read_sql(query, conn, params=(dispoition_type, subdispoition_type, start_date, end_date))
	disp_7_day_chart = disp_7_day_chart.to_dict('records')
	#print(disp_7_day_chart)

	qty_dt = """
	
			SELECT 
		FORMAT(((SUM(CASE WHEN t1.accountvalidation = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question1,


		FORMAT(((SUM(CASE WHEN t1.appropriatecallclosing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question4,
		FORMAT(((SUM(CASE WHEN t1.appropriateprobing  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question5,


		FORMAT(((SUM(CASE WHEN t1.datacapturing_remarks  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question8,
		FORMAT(((SUM(CASE WHEN t1.disposition  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question9,
		FORMAT(((SUM(CASE WHEN t1.empathy  = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question10,


		FORMAT(((SUM(CASE WHEN t1.grammarandsentenceformation = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question13,




		FORMAT(((SUM(CASE WHEN t1.purposeofcall = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question18,
		FORMAT(((SUM(CASE WHEN t1.rpc = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question19,
		FORMAT(((SUM(CASE WHEN t1.self_companyintroduction = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question20,

		FORMAT(((SUM(CASE WHEN t1.standardgreeting = 'MET' THEN 1 ELSE 0 END) / COUNT(*)) * 100),2) AS question22

		FROM sbitest_ai AS t1 join calltrans c on t1.connid = c.connid where
		"""
	
	quality_attr = pd.read_sql(f"{qty_dt} c.disposition ='{dispoition_type}' and c.subdisposition ='{subdispoition_type}' and DATE(c.calldate) BETWEEN '{start_date}' and '{end_date}' ",conn)

	# quality_attr = pd.read_sql(qty_dt, conn, params=(dispoition_type, subdispoition_type, start_date, end_date))
	# query = """CALL DispoGetQualityMetricsFormatted(%s, %s, %s, %s)"""
	# params = (dispoition_type, subdispoition_type, start_date, end_date)
	# quality_attr = pd.read_sql(query, conn, params=params)
	quality_attr = quality_attr.to_dict('records')
	print(quality_attr)

	qualityScore = pd.read_sql(f"SELECT ROUND(AVG(score),2) as qualityscore from sbitest_ai WHERE connid in(select connid from calltrans where disposition='{dispoition_type}' and subdisposition='{subdispoition_type}' and  Date(calldate) BETWEEN '{start_date}' and '{end_date}');",conn)
	# qualityScore_query = """SELECT ROUND(AVG(sa.score), 2) AS qualityscore FROM sbitest_ai sa JOIN calltrans ct ON sa.connid = ct.connid WHERE ct.disposition = %s AND ct.subdisposition = %s AND DATE(ct.calldate) BETWEEN %s AND %s"""
	# qualityScore = pd.read_sql(qualityScore_query, conn, params=(dispoition_type, subdispoition_type, start_date, end_date))


	#dispo_query = pd.read_sql(f'select disposition from calltrans group by disposition',conn) 
	dispo_query = pd.read_sql(f"select disposition from calltrans where date(calldate) >= '2023-12-25' group by disposition ",conn) 
	subdispo_query = pd.read_sql(f"select subdisposition from calltrans where date(calldate) >= '2023-12-25' group by subdisposition",conn) 
	
	#conn.close()
	dispo_query = dispo_query.to_dict('records')
	subdispo_query = subdispo_query.to_dict('records')

	conn.close()
	context = {'data':dispo_query,'subdispo':subdispo_query,'dispoition_senti_data':dispoition_senti_data,'disp_7_day_chart':disp_7_day_chart,'dispoition_name':dispoition_name,'subdispoition_name':subdispoition_name,'attribut_val':quality_attr,'qualityScore':qualityScore.to_dict('records'),'fromdate':start_date,'todate':end_date}
	return render(request,'disposition_analysis.html',context)






# ============= Added New Section User Junaid Ansari 1 July 2024 Block Start ===================

def users_view(request):

	conn = connection()
	users_list = pd.read_sql(f"""select id,name,opoid , role , created_by,created_at from users;""",conn)
	users_list = users_list.to_dict('records')
	my_opo= request.session.get('opoid')

	# print("users_list :",users_list)

	context = {"users_list" : users_list , "my_opo" : my_opo}
	return render(request , 'users.html' ,context = context )


def add_user_view(request):
	if request.method == "POST":
		username = request.POST.get('username' , None)
		opoid = str(request.POST.get('opoid' , None)).lower()
		role = request.POST.get('role' , None)
		password = request.POST.get('password1' , None)
		created_by = request.session.get('opoid')

		# print("username :",username)
		# print("opoid :",opoid)
		# print("role :" , role)
		# print("password :",password)
		# print("created_by :",created_by)

		conn = connection()
		cur = conn.cursor()

		query = """
            INSERT INTO users (name, opoid, role, password, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
		cur.execute(query, (username, opoid, role, password, created_by))
		conn.commit()
		cur.close()
		conn.close()
	
		# return render(request , 'users.html')
		messages.success(request, f'User {username} added successfully.')
		return redirect('users')

	return render(request , 'add_user.html')



def remove_user_view(request , id):
	try:
		# print("id :",id)
		conn = connection()
		cur = conn.cursor()
		cur.execute("DELETE FROM users WHERE id = %s", (id,))
		cur.execute("commit;")
		cur.close()
		messages.success(request, f'User has been deleted successfully.')

	except :
		messages.error(request, f'User with ID {id} does not exist.')

	return redirect("users")



def edit_user_view(request , id):
	# print()
	# print("id :",id)
	# print()

	conn = connection()
	cur = conn.cursor()

	if request.method == "POST":
		try:
			username = request.POST.get("username" , None)
			opoid = request.POST.get("opoid" , None)
			role = request.POST.get("role" , None)
			password = request.POST.get("password1" , None)
			# print(username)
			# print(opoid)
			# print(role)
			# print(password)

			query = "update users SET name = %s , opoid = %s, role = %s, password = %s WHERE id = %s;"
			data = (username , opoid , role , password , id)
			cur.execute(query ,data )

			cur.execute("commit;")
			cur.close()

			messages.success(request, f'User has been updated successfully.')	
			
		except :
			messages.error(request, f'User with ID {id} does not exist.')

		return redirect("users")

	else:

		try:

			query = "select * from users where id = %s"
			cur.execute(query, (id,))

			user = cur.fetchone()
			user_id , username , opoid , role , password , created_by , created_at = user

			context = {
				"user_id" : user_id,
				"username" : username ,
				"opoid" : opoid , 
				"role" : role ,
				"password" : password
			}
			# print('user :',user)
			return render(request , "edit_user.html" , context = context)

		except :
			messages.error(request, f'User with ID {id} does not exist.')

		return redirect("users")
		
# ============= Added New Section User Junaid Ansari 1 July 2024 Block end ===================


# Handling CSP Violations
# To handle CSP violations, you need to create a view to capture and log 
# these reports. Add a URL pattern and corresponding view in your Django 
# app.

@csrf_exempt
def csp_violation_report(request):
    if request.method == 'POST':
        report = json.loads(request.body.decode('utf-8'))
        print("CSP Violation Report:", report)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'invalid method'}, status=405)












