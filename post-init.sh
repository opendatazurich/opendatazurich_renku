#!/bin/sh
SCRIPT_DIR=$(dirname "$(realpath "$0")")

pushd . > /dev/null
cd $SCRIPT_DIR

if [ -z "${DATASET_ID}" ]; then
    echo "DATASET_ID is not set. Using the default dataset."
    papermill templates/TemplateCsv.ipynb OpenData.ipynb
    exit 0
fi

dataset_type=$(python src/get_dataset_type.py "${DATASET_ID}")
if [ "${dataset_type}" = "csv" ]; then
    echo "Using CSV dataset."
    papermill templates/TemplateCsv.ipynb OpenData.ipynb -p dataset_id "${DATASET_ID}"
elif [ "${dataset_type}" = "geo" ]; then
    echo "Using Geo dataset."
    papermill templates/TemplateGeo.ipynb OpenData.ipynb -p dataset_id "${DATASET_ID}"
else
    echo "Unknown dataset type: ${dataset_type}. Defaulting to CSV."
    papermill templates/TemplateCsv.ipynb OpenData.ipynb -p dataset_id "${DATASET_ID}"
    exit 1
fi

popd > /dev/null
