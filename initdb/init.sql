######################################################################;

SHOW DATABASES;
CREATE DATABASE IF NOT EXISTS crypto_db;

######################################################################;

CREATE USER IF NOT EXISTS 'walid'@'%' IDENTIFIED BY 'walid';
GRANT ALL PRIVILEGES ON crypto_db.* TO 'walid'@'%' WITH GRANT OPTION;

CREATE USER IF NOT EXISTS 'sam'@'%' IDENTIFIED BY 'sam';
GRANT ALL PRIVILEGES ON crypto_db.* TO 'root'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;
SELECT host
  , user
FROM mysql.user;

######################################################################;

USE crypto_db

######################################################################;

DROP TABLE IF EXISTS T_SYMBOL ;
/*DROP TABLE IF EXISTS T_CRYPTO_HIST ;*/

######################################################################;

CREATE TABLE IF NOT EXISTS T_SYMBOL (
    symbol VARCHAR(10) NOT NULL,
    PRIMARY KEY (symbol)
);

######################################################################;

CREATE TABLE IF NOT EXISTS T_CRYPTO_HIST (
    symbol VARCHAR(10) NOT NULL,
    time TIMESTAMP NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume FLOAT NOT NULL,
    closetime TIMESTAMP NOT NULL,
    quote_asset_volume FLOAT NOT NULL,
    number_of_trades FLOAT NOT NULL,
    base_asset_volume FLOAT NOT NULL,
    base_quote_volume FLOAT NOT NULL,
    PRIMARY KEY (symbol, time)
);
