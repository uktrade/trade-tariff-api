#!/usr/bin/env python3

import uuid
import hashlib
import click


def print_keys(api_key, hashed_api_key) -> None:
    """Print `api_key` and `hashed_api_key` to the console with an informational
    message."""

    click.echo()
    click.echo("Provide the key to the client:")
    click.secho(api_key.decode("utf-8"), bold=True)
    click.echo()
    click.echo("Store the key's hash as an APIKEYS / APIKEYS_UPLOAD env var:")
    click.secho(hashed_api_key, bold=True)
    click.echo()


def generate_keys(api_key: str=None) -> tuple[str, str]:
    """Generate an API key and its hash, returning both in that order within a
    tuple. If `api_key` is provided (it must be a hex value in string format)
    then its value is used as the API key from which the hash is generated."""

    if api_key:
        try:
            int(api_key, 16)
        except ValueError:
            click.secho("Error: api_key must be a hexadecimal value.", fg="red")
            exit(1)
        api_key = api_key.encode("ascii")
    else:
        api_key = uuid.uuid4().hex.encode("ascii")

    hashed_api_key = hashlib.sha256(api_key).hexdigest()

    return api_key, hashed_api_key


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--api_key", required=False, help="Provide a key a hashing.")
def cli(ctx, api_key):
    """Generate and print an API key and its hash."""

    api_key, hashed_api_key = generate_keys(api_key)
    print_keys(api_key, hashed_api_key)


if __name__ == "__main__":
    cli()
