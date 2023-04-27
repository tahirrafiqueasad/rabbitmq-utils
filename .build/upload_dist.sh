(
    set -e

    # MAKING ENVIRONMENT
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install twine

    # UPLOADING
    twine upload ./dist/* --repository pypi

    # REMOVING ENV
    deactivate
    rm -rf ./venv
)