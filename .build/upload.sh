(
    # NOTE: Runs this file like source .build/upload.sh

    # MAKING ENVIRONMENT
    python3 -m venv .buildvenv
    source .buildvenv/bin/activate
    pip install --upgrade pip
    pip install twine

    # UPLOADING
    twine upload --repository pypi-rabbitmq-utils ./dist/*

    # REMOVING ENV
    deactivate
    rm -rf ./.buildvenv
)