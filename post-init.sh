#!/bin/bash
SCRIPT_DIR=$(dirname "$(realpath "$0")")

pushd . > /dev/null
cd $SCRIPT_DIR

if [ -z "${PACKAGE_ID}" ]; then
    echo "PACKAGE_ID is not set. Using the default dataset."
    PACKAGE_ID="bau_hae_lima_zuordnung_adr_quartier_bzo16_bzo99_od5143"
fi

if [ -z "${RESOURCE_ID}" ]; then
    echo "RESOURCE_ID is not set. Using the first resource."
    RESOURCE_ID="NONE"
fi

dataset_type=$(python src/get_dataset_type.py "${PACKAGE_ID}")
if [ "${dataset_type}" = "geo" ]; then
    echo "Using Geo dataset."
    template="templates/TemplateGeo.ipynb"
else
    if [ "${dataset_type}" = "csv" ]; then
        echo "Using CSV dataset."
    else
        echo "Unknown dataset type: ${dataset_type}. Defaulting to CSV."
    fi
    template="templates/TemplateCsv.ipynb"
fi

python src/run_template.py "${template}" OpenData.ipynb "${PACKAGE_ID}" "${RESOURCE_ID}"

popd > /dev/null
