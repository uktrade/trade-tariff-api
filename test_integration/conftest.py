
def pytest_addoption(parser):
    """
    Add a custom pytest option, `--env-file`, to allow different env files to be
    configured and used when running integration tests.
    
    This enables support for different environment files when integration
    testing against different service environments. For instance, by creating
    the file `.env.test` we can use the env vars configured in that file instead
    of those found in `.env` (the default):

        pytest --env-file=.env.test
    """

    parser.addoption("--env-file", action="store", default=".env")
