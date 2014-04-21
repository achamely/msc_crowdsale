#!/usr/bin/python
#Crowdsale Daemon.investor
import os, sys, signal, commands
import psycopg2, psycopg2.extras
import calendar, time
import requests, urlparse
import json

if len(sys.argv) > 1: 
    print "Reads from backend Database and performs crowd sale investments"
    exit()

#Figure out where we are running from 
#TOOLS='/home/ubuntu/mastercoin-tools'
TOOLS=os.path.dirname(os.path.realpath(__file__))

#Define the local DB name/user for tracking
DBNAME='maidsafe'
DBUSER='ubuntu'
#Prime SQL command
con = None

def handler(signum, frame):
    print('Stop Signal received')
    if con:
        con.close()
    exit(1)

def sql_connect():
    global con
    try:     
        con = psycopg2.connect(database=DBNAME, user=DBUSER)
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    	return cur
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)

def get_balance(address, csym, div):
    bal1=-3
    bal2=-4
    url =  'https://test.omniwallet.org/v1/address/addr/'
    PAYLOAD = {'addr': address }
    try:
        tx_data= requests.post(url, data=PAYLOAD, verify=False).json()
        for bal in tx_data['balance']:
	    if csym == bal['symbol']:
	    	if div == 1:
		    bal1=bal['value']
		else:
		    fbal=float(bal['value'])/100000000    
                    bal1=('%.8f' % fbal)
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
	print('Site 1 Unresponsive, Using 0 balance for now')
	bal1=-1

    url2 = 'http://uswest-dmzblue-base04alpha-devsnapred.masterchest.info/mastercoin_verify/adamtest.aspx?address='+address
    try:
	tx2_data=requests.get(url2, verify=False).json()
    	for bal in tx2_data['balance']:
            if csym == bal['symbol']:
            	bal2= ('%.8f' % float(bal['value']))
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
	print('Site 2 Unresponsive, Using 0 balance for now')
	bal2=-2

    if bal1 == bal2:
	print(' Confirmed Balance of '+str(bal1)+' '+str(csym)+' for '+str(address)+' from 2 data points')
	return bal1
    elif bal1 > 0 and bal2 < 0:
	print(' Balance mismatch, Site 1:['+str(bal1)+'] Site 2:['+str(bal2)+'] '+str(csym)+' for '+str(address)+' from 2 data points. Preffering Non Negative Balance Site 1: '+str(bal2))
        return bal1
    else:
	print(' Balance mismatch, Site 1:['+str(bal1)+'] Site 2:['+str(bal2)+'] '+str(csym)+' for '+str(address)+' from 2 data points. Preffering Site 2: '+str(bal2))
	return bal2


def send_tx(dstaddress, txamount, txcid, div):
    #write function to call msc_sxsendtx.py with the proper json files
    send_json=('{ \\"transaction_from\\": \\"'+str(MYADDRESS)+'\\", \\"transaction_to\\": \\"'+str(dstaddress)+'\\",'
               ' \\"currency_id\\": '+str(txcid)+', \\"msc_send_amt\\": \\"'+str(txamount)+'\\", \\"from_private_key\\": \\"'+str(MYPRIVKEY)+'\\",'
               '\\"property_type\\": '+str(div)+',\\"broadcast\\": '+str(BROADCAST)+',\\"clean\\": '+str(CLEAN)+' }')
    print('  ^--Creating\sending tx for '+str(txamount)+' of currency id '+str(txcid)+' and sending it to '+str(dstaddress))

    #print ('\n\n\n '+send_json)
    inter = commands.getoutput('echo '+send_json+' | python '+TOOLS+'/msc-sxsend.py').strip()
    print ('\n\n\n '+inter)
    #return commands.getoutput('echo '+send_json+' | python '+TOOLS+'/msc-sxsend.py')
    return inter

signal.signal(signal.SIGINT, handler)
#read json in with variables
JSON = sys.stdin.readlines()
listOptions = json.loads(str(''.join(JSON)))

#Define my local address used for sending/receiving MSC/SP
MYADDRESS=listOptions['my_address']
MYPRIVKEY=listOptions['my_private_key']
#Define the Investment address
IADDR=listOptions['investment_address']
#Define the Investment Sale end date (epoch) to calculated expected bonus
EDATE=listOptions['end_date']
#Define the Smart Property Bonus % /week
BRATE=listOptions['earlybird_bonus']
#Define the desired exchange rate. How many MSC in a BTC.  Ex; .2 BTC/MSC =>  1/.2 = 5 MSC/BTC
RATE=listOptions['x_rate']
#Define the expected MSC -> SP rate
SPRATE=listOptions['sp_rate']
#Define the Currency ID of the Smart property
SPCID=listOptions['sp_cid']
#Define Divisible
SPDIV=listOptions['property_type']
#Define the currency we send to make the investment ('1' MSC, '2' TMCS).
ICUR='2'
#Broadcast 1 or Test 0
BROADCAST=1
#1 to keep unsigned and signed, 2 to keep only signed
CLEAN=1



print('\n\n-----------------------------------------------------------------------------------------')
if ICUR=='1':
    ISYM='MSC'
    print('Investment Currency has been set to Mastercoins. All Tx to the fundraiser address will send MSC')
elif ICUR=='2':
    ISYM='TMSC'
    print('Investment Currency has been set to Test Mastercoins. All Tx to the fundraiser address will send TMSC')
else:
    print('Investment Currency is invalid, please check and configuration and try again')
    exit(1)

if BROADCAST==0:
    print('Test Mode Enabled: Tx files will be created but not transmitted')
elif BROADCAST==1:
    print('Live Mode Enabled: Tx Files will be created AND Transmitted!')
else:
    print('Broadcast flag is invalid, Please change it and try again')
    exit(1)
print('-----------------------------------------------------------------------------------------')

while 1:

	print('\nChecking DB for tx to calculate expected smart property return')
	#Calculate the expected bonus for anyone we haven't yet.
	try:
          dbc
        except NameError:
          dbc=sql_connect()

	#Find transaction where we have Sent the MSC investment and we have not calculated expected Smart Properties
        dbc.execute("SELECT * FROM tx where f_msc_sent='1' and sp_exp='-1' order by id")
        ROWS = dbc.fetchall()
	print('^----Found '+str(len(ROWS))+' new TX to process')

        for row in ROWS:
            url =  'http://btc.blockr.io/api/v1/tx/info/' + row['tx_invest']
	    try:
                tx_data= requests.get(url).json()
	    except ValueError:  # includes simplejson.decoder.JSONDecodeError
	        print('Remote TX info not available yet for tx: '+str(row['tx_invest']))

	    #wait for at least 3 confirmations before moving onto data validation
	    if "success" in tx_data['status'] and tx_data['data']['confirmations'] >= 3:
		TXDATEUTC=calendar.timegm(time.strptime(tx_data['data']['time_utc'], '%Y-%m-%dT%H:%M:%SZ'))
		#Calculate and record expected number of Smart Property Tokens we should receive based on bonus calculation
                SPBASE=row['msc_sent']*SPRATE           #Base Num Tokens expected: Investment amount * return multiplier
                SBD=EDATE-TXDATEUTC                 	#Seconds before deadline
                BONUS=int((BRATE*SBD*SPBASE)/604800/100)   #calculate the Total Bonus amount =  Seconds before deadline/seconds in a week * Bonus% week * Token Base amount
		SPEXP=BONUS+SPBASE                  	#calculate the final token expected
		#print ('SPBASE:'+str(SPBASE)+'  SBD:'+str(SBD)+'  BONUS:'+str(BONUS)+'  SPEXP:'+str(SPEXP)+'  SPRATE:'+str(SPRATE)+'  BRATE:'+str(BRATE)+'  EDATE:'+str(EDATE)+'  TXDATEUTC:'+str(TXDATEUTC))
                try:
                    dbc.execute("UPDATE tx set sp_exp=%s where address=%s", (SPEXP, row['address']))
                    con.commit()
		    print('Calculated '+str(SPEXP)+' should be generated for investor '+str(row['address']))
                except psycopg2.DatabaseError, e:
                    if dbc:
                        con.rollback()
                        print 'Error updating db: %s' % e
                        sys.exit(1)
	    elif "success" in tx_data['status'] and tx_data['data']['confirmations'] < 3:
		print ('Tx '+str(row['tx_invest'])+' appears valid but has '+str(tx_data['data']['confirmations'])+' confirmations. Waiting for 3 confirmations')
	    else:
		print ('Tx '+str(row['tx_invest'])+' has not been seen yet as valid yet')

	print('\nChecking DB for entries to finish and send Smart Property Tokens back to investor')
	#Go through the Db of people we have not yet sent Smart Property Tokens to and if we have enough (Smart Property Token) balance send them the expected/calculated Expect number of tokens. 
	try:
	  dbc
	except NameError:
	  dbc=sql_connect()
	
	#Get TX's where user has verified its ready, we have not yet sent smart property, we have sent MSC investment and we have calculated the Expected Smart properties
	dbc.execute("SELECT * FROM tx where v_sp_send='1' and f_sp_sent='0' and f_msc_sent='1' and sp_exp>'0' order by id")
	ROWS = dbc.fetchall()

	print('^----Found '+str(len(ROWS))+' new DB entries to process')

        #Only attempt to get balance if we have data to process
        SPBALANCE=0
        if len(ROWS) > 0:
	    SPBALANCE=get_balance(MYADDRESS, 'SP'+str(SPCID), SPDIV)
	
	for row in ROWS:
	    if row['sp_exp'] <= SPBALANCE:
		BCAST=json.loads(send_tx(row['address'],row['sp_exp'],SPCID, SPDIV))
		if "Success" in BCAST['status']:
		    SPBALANCE = SPBALANCE-row['sp_exp']
		    FNAME=BCAST['st_file'].rpartition('/')[2]
		    #Update Database on who we sent SP tokens too and how many
		    try:
		        dbc.execute("UPDATE tx set f_sp_sent='1',sp_sent=%s,tx_out=%s,sp_tx_file=%s where address=%s", (row['sp_exp'], BCAST['hash'], FNAME, row['address']))
	                con.commit()
		    except psycopg2.DatabaseError, e:
			if dbc:
			    con.rollback()
	    		    print 'Error updating db: %s' % e    
			    sys.exit(1)
		elif BROADCAST == 0:
		    FNAME=BCAST['st_file'].rpartition('/')[2]
		    try:
			print('Test Mode Enabled: File Created but not broadcast')
                        dbc.execute("UPDATE tx set f_sp_sent='2',sp_sent=%s,tx_out=%s,sp_tx_file=%s where address=%s", (row['sp_exp'], BCAST['hash'], FNAME, row['address']))
                        con.commit()
                    except psycopg2.DatabaseError, e:
                        if dbc:
                            con.rollback()
                            print 'Error updating db: %s' % e
                            sys.exit(1)
		else:
		    print('\n\n****************************************************************************************************************************')
		    print('Sending SP TX failed for '+str(row['address'])+' with error: '+json.dumps(BCAST))
		    print('****************************************************************************************************************************')
	    else:
		print('\n\n****************************************************************************************************************************')
		print('Local Smart Property Balance ('+str(SPBALANCE)+') is too low to credit '+str(row['sp_exp'])+' tokens for investor: '+str(row['address']))
		print('****************************************************************************************************************************')
		break

	print('\nChecking DB for entries to send MSC investment to Fundraiser')		
	#Scan the Database for any new transactions we haven't yet invested
	try:
	  dbc
	except NameError:
	  dbc=sql_connect()
	
	#Select tx's where the MSC amount to invest is verified and we have not yet sent MSC or Smart Property Tokens
	dbc.execute("SELECT * FROM tx where v_msc_send='1' and f_sp_sent='0' and f_msc_sent='0' order by id")
	ROWS = dbc.fetchall()

	print('^----Found '+str(len(ROWS))+' new DB entries to send investing payment')

	#only attempt to get balance if we have data to process
	ICURBALANCE=0
	if len(ROWS) > 0:
            ICURBALANCE=get_balance(MYADDRESS,ISYM,2)
	
	for row in ROWS:
	    #For each tx calculate MSC to send and send it to the investment address using msc_sxsend.py
	    IAMOUNT=row['btc']*RATE
	    #Make sure we have enough MSC to actually do the investment
	    if IAMOUNT <= ICURBALANCE:
	        BCAST=json.loads(send_tx(IADDR,IAMOUNT,ICUR,'2'))
	        NOW=calendar.timegm(time.gmtime())
	        if "Success" in BCAST['status']:
		    FNAME=BCAST['st_file'].rpartition('/')[2]
	            #Record the #MSC sent in the db
	            try:
		        dbc.execute("UPDATE tx set f_msc_sent='1', msc_sent=%s, tx_invest=%s, time_msc_sent=%s,msc_tx_file=%s where address=%s", (IAMOUNT, BCAST['hash'], NOW, FNAME, row['address']))
		        con.commit()
		    except psycopg2.DatabaseError, e:
	                if dbc:
			    con.rollback()
			    print 'Error updating db: %s' % e
			    sys.exit(1)
		elif BROADCAST == 0:
		    FNAME=BCAST['st_file'].rpartition('/')[2]
		    try:
			print('Test Mode Enabled: File Created but not broadcast')
                        dbc.execute("UPDATE tx set f_msc_sent='2', msc_sent=%s, tx_invest=%s, time_msc_sent=%s,msc_tx_file=%s where address=%s", (IAMOUNT, BCAST['hash'], NOW, FNAME, row['address']))
                        con.commit()
                    except psycopg2.DatabaseError, e:
                        if dbc:
                            con.rollback()
                            print 'Error updating db: %s' % e
                            sys.exit(1)
		else:		
		    print('\n\n****************************************************************************************************************************')
		    print('Sending Investment TX failed for '+str(row['address'])+' with error: '+json.dumps(BCAST))
 		    print('****************************************************************************************************************************')
	    else:
		print('\n\n*****************************************************************************************************************************************************')
		print('Local Source Address Currency Balance is too low ('+str(ICURBALANCE)+' '+ISYM+') to send investment payment: '+str(IAMOUNT)+' for investor: '+str(row['address']))
		print('*****************************************************************************************************************************************************')
		break


	#sleep for 5 minutes and repeat
	print('\n\n------------------------------------------------------------')
	print('      Sleeping for 5 minutes before next check')
	print('------------------------------------------------------------')
	time.sleep(300)
