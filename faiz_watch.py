#get fix
import sys,json, operator, os.path, time, calendar, requests, subprocess,os, signal

JSON = str(''.join(sys.stdin.readlines()))
listOptions = json.loads(JSON)

def handler(signum, frame):
    sx_mon.terminate()
    sx_mon.kill()
    exit(1)
    print 'kill procs'

signal.signal(signal.SIGINT, handler)

sx_mon = subprocess.Popen(['/usr/local/bin/sx','monitor', listOptions['address']], stdout=subprocess.PIPE )

count=0
for line in iter(sx_mon.stdout.readline, ''):
   splitted=line.split(' ')
   if len(splitted) > 0 and splitted[0] != 'Worker:':
        transaction_hash = splitted[0]
        bitcoin_amt =  '%.8f' % (float(splitted[1])/100000000)
        msc_needed = bitcoin_amt*5
        address=''
        url =  'http://btc.blockr.io/api/v1/tx/info/' + transaction_hash
        tx_data= requests.get(url).json()
        #print tx_data.keys()
	largestamt=0
        for vin in tx_data['data']['trade']['vins']:
            if vin['is_nonstandard'] == False:
		if abs(vin['amount']) > largestamt:
		    largestamt=abs(vin['amount'])
		    address=vin['address']
		print vin

        #retval_q = subprocess.Popen('/usr/bin/psql','maidsafe', '-q', '-c', "insert into tx (address, btc, tx_in) values ('$address','#btc', '$tx_in');")
        print address, bitcoin_amt, transaction_hash

	import psycopg2
	try:       
	    con = psycopg2.connect(database='maidsafe', user='ubuntu')        
	    cur = con.cursor()  
	    cur.execute("INSERT into tx (address, btc, tx_in) values (%s, %s, %s)", (address, bitcoin_amt, transaction_hash ))         
	    con.commit()      
	except psycopg2.DatabaseError, e:      
	    if con: 
		con.rollback()      
	    print 'Error %s' % e     
	    sys.exit(1)      
	finally:      
	    if con: 
		con.close()

   if(count > 1):
        handler('','')
   count+=1

#trigger send from address for X MSC to fundraiser_addr
#then MSC*3400 MaidSafe to from_addr, bonus calcs

