msc_crowdsale
=============

Crowdsale daemon

You'll need mastercoin tools installer and postgresql


## Setup:

1. Clone and install the One click installer

   ```
git clone https://github.com/mastercoin-MSC/install-msc.git
cd install-msc
sudo bash install-msc,sh
   ```

2. Install and setup postgres and psycopg2

   ```
sudo apt-get install postgresql python-psycopg2
   ```

3. Download and clone this repo

   ```
git clone https://github.com/achamely/msc_crowdsale.git
   ```

4. Create a db and user for the db that the script will be able to use.

   ```
  sudo -u postgres psql postgres    (starts the admin connection to postgres)
     CREATE USER ubuntu;               (this should be the same name as the user that will be running the script)
     CREATE DATABASE mycrowdsale;    (you can change this to whatever you prefer)
     GRANT ALL PRIVILEGES ON DATABASE mycrowdsale to ubuntu;     (update these to match above)
     \q       (quit the psql console)
   ```

5. Login as your local user and create the table structures for the Database.
*Note: you need the tx_utxo statement and 1 of the 2 tx statements from references/database.schema

   ```
  psql mycrowdsale
  #toInvestor schema 
     create TABLE tx(id BIGSERIAL primary key, address char(34) not null, sp_exp integer DEFAULT -1, tx_out char(64), sp_sent integer, f_sp_sent char(1) DEFAULT 0, v_sp_send char(1) DEFAULT 0, sp_tx_file char(100));
  #db for utxo transactions
     create TABLE tx_utxo(id BIGSERIAL primary key, address char(34) not null, tx_hash char(64) not null, hash_index integer not null, satoshi bigint not null, block integer not null, lock char(1) DEFAULT 0 not null, constraint u_constraint unique (address, tx_hash, hash_index));
   ```

## Usage:

toInvestor: Used to automate the distribution of a Masterprotocol currency from an sql database
 NOTE: This was written for nondivisible tokens. An update to process divisible tokens is coming soon. 

1. Update/fill in to_example.json with your relevant information
   
   ```
 my_address: The address that holds your tokens/currency
 my_private_key: The associated private key
 property_type: 1 for indivisible , 2 for divisible (MSC,TMSC)
 sp_cid: The currency ID you wish to send
   ```

2. Update toInvestor.py to reflect your database name and username

3. Import your data into the database tx table. The relevant fields you need are:

   ```
 address: The address to send the Masterprotocol currency to
 sp_exp: The quantity of the Masterprotocol currency to send
   ```
   
4. Review your data and update / set the v_sp_send='1' for all db entries you wish to process

5. Pipe your json input into the program

   ```
    cat myconfig.json | python toInvestor.py
   ```

6. The program will automatically process db entries where v_sp_send='1' and will run until it finishes or it can't create any new transactions.
   It will then sleep for 5 minutes and repeat the process. 

7. All processed sends get flagged in the db (f_sp_sent='1') so they will not be processed again. We also record the txhash and the filename of signed tx. 
