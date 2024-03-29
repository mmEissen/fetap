import click



@click.group
def cli() -> None:
    pass


@cli.command
def run() -> None:
    print("Started")
    from fetap import dial
    dial.get_number()


@cli.command
def release() -> None:
    from fetap import deploy

    deploy.release()


@cli.command
@click.argument("remotehost", type=str, envvar="FETAP_REMOTEHOST")
@click.option("--dev", is_flag=True, default=False)
def install(remotehost: str, dev: bool) -> None:
    from fetap import deploy

    deploy.install(remotehost, dev)


@cli.command
@click.argument("remotehost", type=str, envvar="FETAP_REMOTEHOST")
def uninstall(remotehost: str) -> None:
    from fetap import deploy

    deploy.uninstall(remotehost)


@cli.command
@click.argument("remotehost", type=str, envvar="FETAP_REMOTEHOST")
def logs(remotehost: str) -> None:
    from fetap import deploy

    deploy.logs(remotehost)


@cli.command
@click.argument("remotehost", type=str, envvar="FETAP_REMOTEHOST")
def deploy_dev(remotehost: str) -> None:
    from fetap import deploy

    deploy.deploy_dev(remotehost, show_logs=True)


cli()
