# Plant-Sensor-Team

## SETUP

Please run the following to setup your database locally:  \
`psql -d postgres -f create_tables.sql`

Please run the following to setup database remotely:  \
`psql --host [rds-address] --port 5439 -U [user] dev -f create_tables.sql`

### Questions about data

- Some plants do not have sunlight recorded; raise issue with LMNH to adjust their raspberry pi.