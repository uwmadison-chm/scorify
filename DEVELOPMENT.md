# How to work on Scorify

    virtualenv .venv
    source .venv/bin/activate
    pip3 install -r requirements-dev.txt

## Pytest

To run tests:

    pytest

To run a specific test and drop into a debugger, put this for breakpoints:

    import pdb; pdb.set_trace()

    pytest -k <TEST_NAME> --pdb

