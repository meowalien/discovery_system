pg_dump -h postgres.default -p 5432 -U postgres -d discovery_system -F c -f backup/mydb.dump
pg_restore -h postgres.default -p 5432 -U postgres -d discovery_system -c backup/mydb.dump