#!/bin/bash

if [ -z "${DATASET_ID}" ]; then
    echo "DATASET_ID is not set. Using the default dataset."
    papermill TemplateCsv.ipynb OpenData.ipynb
    exit 0
fi

echo "Running papermill with DATASET_ID=${DATASET_ID}"
papermill TemplateCsv.ipynb OpenData.ipynb -p dataset_id "${DATASET_ID}"
