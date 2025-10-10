import click

@click.group()
def cli():
    pass

@cli.group()
def server():
    pass

@server.command(
    context_settings={
        "ignore_unknown_options":True
    }
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def docker(args: list[str]):
    import subprocess
    import shlex

    command = f"COMPOSE_FILE=/home/momo/usb2/server/docker-compose-prod.yml docker {' '.join(shlex.quote(arg) for arg in args)}"
    subprocess.run(["ssh", "momo@fetap-build", "-t", command])

cli()
