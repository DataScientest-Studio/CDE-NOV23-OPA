show databases;
#Création de la Bdd
create database if not exists opa;

########################################;
#Création des users
create user if not exists 'datascientest'@'%' identified by 'admin';
grant all privileges on opa.* to 'datascientest'@'%' with grant option;
grant all privileges on opa.* to 'root'@'%' with grant option;
flush privileges;
select host
  , user
from mysql.user;
######################################## ;
use opa;

########################################;
#Réinitilisation des tables
drop table if exists T_CRYPTO_HIST;
drop table if exists T_CRYPTO_STREAM;
drop table if exists T_SYMBOL;

create table if not exists T_SYMBOL
    (
        id_symbol       int not null
      , symbol          varchar(10) not null
      , interval_symbol varchar(4) not null
      , date_insert timestamp not null
      , date_update timestamp not null
      , starttime bigint not null
      , endtime   bigint not null
      , primary key(id_symbol)
    ) ;	
--
insert
into T_SYMBOL values
    (
        1
      , 'BTCUSDT'
      , '1h'
      , now()
      , now()
      , 0
      , 0
    ) ;
	
	
######################################## ;
#Création de la table T_CRYPTO_HIST
drop table if exists T_CRYPTO_HIST ;
create table if not exists T_CRYPTO_HIST
    (
        id_symbol int not null
      , opentime  bigint not null
      , open float not null
      , high float not null
      , low float not null
      , close float not null
      , volume float not null
      , closetime        bigint not null
      , quote_asset_volume float not null
      , number_of_trades float not null
      , taker_buy_base_asset_volume float not null
      , taker_buy_quote_asset_volume float not null
      , primary key(id_symbol, opentime)
      , foreign key(id_symbol) references T_SYMBOL(id_symbol)
    ) ;

	
######################################## ;
#Création de la table T_CRYPTO_STREAM
drop table if exists T_CRYPTO_STREAM ;
create table if not exists T_CRYPTO_STREAM
    (
        id_symbol int not null
      , event_type varchar(16) not null
      , event_time float not null
      , symbol varchar(16) not null
	  , kline_starttime float not null
	  , kline_closetime float not null
      , symbol_2 varchar(16) not null	  
      , interval_symbol varchar(16) not null
      , first_trade_id int not null
      , last_trade_id int not null	  
      , open_price  float not null
      , close_price  float not null	  
      , high_price float not null
      , low_price float not null
      , base_asset_volume float not null
      , number_of_trades int not null
	  , is_this_kline_closed int not null
      , quote_asset_volume float not null
      , taker_buy_base_asset_volume float not null
      , taker_buy_quote_asset_volume float not null
      , primary key(id_symbol, opentime)
    )
    engine = memory;
		