# How to work on Scorify

Currently, this module is being converted to Python 3.

    virtualenv env/scorify
    pip3 install -r requirements-dev.txt

## Pytest

To run tests, install the module locally and run pytest:

    pip3 install --user . && pytest

To run a specific test and drop into a debugger, put this for breakpoints:

    import pdb; pdb.set_trace()

and then run:

    pip3 install --user . && pytest -k <TEST_NAME> --pdb

