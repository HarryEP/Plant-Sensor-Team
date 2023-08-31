# Plant-Sensor-Team


## SETUP

Please run the following to setup your database locally:  \
`psql -d postgres -f create_tables.sql`

### Questions about data

- Some plants do not have sunlight recorded; raise issue with LMNH to adjust their raspberry pi.

### Extraction findings

Plant ids start from 0, if you put negatives, crashes

Possible outcomes:

Plant not found
`{'error': 'plant not found', 'plant_id': 54}`

Normal:
`{'botanist': {'email': 'gertrude.jekyll@lnhm.co.uk', 'name': 'Gertrude Jekyll', 'phone': '965-251-6468'}, 'cycle': 'Herbaceous Perennial', 'images': ..... `

Plant on Loan:
`{'error': 'plant on loan to another museum', 'plant_id': 43}`

### git

to initialise the new branch, commit + push anything
`git merge main` to pull from main to branch
switch to main to fetch + pull
