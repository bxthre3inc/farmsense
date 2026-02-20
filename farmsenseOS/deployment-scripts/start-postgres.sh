#!/bin/bash
# PostgreSQL with PostGIS startup script for Zo service

export PGDATA=/var/lib/postgresql/data
export POSTGRES_USER=${POSTGRES_USER:-farmsense_user}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-changeme}
export POSTGRES_DB=${POSTGRES_DB:-farmsense}
export PGPORT=${PORT:-5432}

# Initialize database if not exists
if [ ! -s "$PGDATA/PG_VERSION" ]; then
    echo "Initializing PostgreSQL database..."
    initdb -D $PGDATA --auth-local=trust --auth-host=md5
    
    # Configure postgresql.conf
    echo "listen_addresses = '*'" >> $PGDATA/postgresql.conf
    echo "port = $PGPORT" >> $PGDATA/postgresql.conf
    
    # Configure pg_hba.conf for external connections
    echo "host all all 0.0.0.0/0 md5" >> $PGDATA/pg_hba.conf
    
    # Start PostgreSQL temporarily to create user and database
    pg_ctl -D $PGDATA -l /dev/shm/postgres.log start -w
    
    # Create user and database
    psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
        CREATE USER $POSTGRES_USER WITH SUPERUSER PASSWORD '$POSTGRES_PASSWORD';
        CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;
        \connect $POSTGRES_DB
        CREATE EXTENSION IF NOT EXISTS postgis;
        CREATE EXTENSION IF NOT EXISTS timescaledb;
EOSQL
    
    pg_ctl -D $PGDATA stop -w
fi

# Start PostgreSQL in foreground
exec postgres -D $PGDATA -c config_file=$PGDATA/postgresql.conf
