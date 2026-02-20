#!/bin/bash
# PostgreSQL wrapper for Zo service - uses PORT env var

export PGDATA=/var/lib/postgresql/data
export PGPORT=${PORT:-5432}

# Update postgresql.conf with the correct port
su - postgres -c "sed -i 's/^port = .*/port = '$PGPORT'/' $PGDATA/postgresql.conf"
su - postgres -c "echo 'port = $PGPORT' >> $PGDATA/postgresql.conf" 2>/dev/null || true

# Start PostgreSQL in foreground
exec su - postgres -c "/usr/lib/postgresql/15/bin/postgres -D $PGDATA -c config_file=$PGDATA/postgresql.conf"
