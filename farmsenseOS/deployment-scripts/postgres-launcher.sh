#!/bin/bash
# PostgreSQL launcher using setpriv to fully drop privileges

export PGDATA=/var/lib/postgresql/data
export PGPORT=${PORT:-5432}
export HOME=/var/lib/postgresql

# Ensure postgres owns the data directory
chown -R postgres:postgres $PGDATA
chmod 700 $PGDATA

# Update postgresql.conf with the correct port
sed -i "s/^port = .*/port = $PGPORT/" $PGDATA/postgresql.conf 2>/dev/null || echo "port = $PGPORT" >> $PGDATA/postgresql.conf
sed -i "s/^#port = .*/port = $PGPORT/" $PGDATA/postgresql.conf 2>/dev/null || true

# Ensure postgres user can write to the socket directory
mkdir -p /var/run/postgresql
chown postgres:postgres /var/run/postgresql

# Start PostgreSQL with fully dropped privileges
exec setpriv --reuid=postgres --regid=postgres --clear-groups --inh-caps=-all \
    /usr/lib/postgresql/15/bin/postgres -D $PGDATA -c config_file=$PGDATA/postgresql.conf
