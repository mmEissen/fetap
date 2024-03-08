import click


@click.group
def cli() -> None:
    pass


@cli.command
def run() -> None:
    pass


@cli.command
def release() -> None:
    import deploy

    deploy.release()


@cli.command
@click.argument("remotehost", type=str)
@click.option("--dev", is_flag=True, default=False)
def install(remotehost: str, dev: bool) -> None:
    import deploy

    deploy.install(remotehost, dev)


@cli.command
@click.argument("remotehost", type=str)
def uninstall(remotehost: str) -> None:
    import deploy

    deploy.uninstall(remotehost)


@cli.command
@click.argument("remotehost", type=str)
def logs(remotehost: str) -> None:
    import deploy

    deploy.logs(remotehost)


cli()
