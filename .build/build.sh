(
    # NOTE: Runs this file like source .build/build.sh

    # MAKING ENVIRONMENT
    python3 -m venv .buildvenv
    source .buildvenv/bin/activate
    pip install --upgrade pip
    pip install build twine

    # BUILDING
    rm -rf dist
    python -m build .

    # REMOVING ENV
    deactivate
    rm -rf ./.buildvenv
)