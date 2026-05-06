(
    set -e

    # MAKING ENVIRONMENT
    python3 -m venv .buildvenv
    source .buildvenv/bin/activate
    pip install --upgrade pip
    pip install twine

    # UPLOADING
    twine upload --verbose --repository testpypi ./dist/*

    # REMOVING ENV
    deactivate
    rm -rf ./.buildvenv
)
