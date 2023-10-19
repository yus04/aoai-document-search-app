#!/bin/sh

python ./app/prepdocs/create_and_upload_blob.py
python ./app/prepdocs/create_datasource.py
python ./app/prepdocs/create_skillset.py
python ./app/prepdocs/create_index.py
python ./app/prepdocs/create_indexer.py