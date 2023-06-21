(
    # MAKING ENVIRONMENT
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install build

    # COPYING DATA
    mkdir rabbitmq_utils
    cp -r ../__init__.py ../consumer.py ../producer.py ../requirements.txt ../rpc ./rabbitmq_utils
    cp ../README.md ./

    # BUILDING
    rm -rf dist
    python -m build .

    # REMOVINF UNWANTED
    rm -rf ./rabbitmq_utils.egg-info
    rm -rf ./rabbitmq_utils
    rm README.md

    # REMOVING ENV
    deactivate
    rm -rf ./venv
)