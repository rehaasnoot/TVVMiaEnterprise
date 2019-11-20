#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from tvvmiaecology.settings import TVVConfigApi

SECTION = "TVVMia API GraphQL"
cfg = TVVConfigApi()
ENGINE_CONNECT_STRING = cfg.get(SECTION, 'db_uri')

db_engine = create_engine(ENGINE_CONNECT_STRING, convert_unicode=True)

db_session_scoped = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db_engine, expire_on_commit=True))
# We will need this for querying
declarative_base().metadata.bind = db_engine
db_query_prop = db_session_scoped.query_property()

