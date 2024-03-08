import subprocess
import click
from os import path


@click.group
def cli() -> None:
    pass


@cli.command
def run() -> None:
    pass


@cli.command
def release() -> None:
    project = path.dirname(path.dirname(__file__))
    release_txt = path.join(project, "release.txt")
    subprocess.run(
        ["poetry", "export", "--without-hashes", f"--output={release_txt}"],
        check=True,
        cwd=project,
    )
    current_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        check=True,
        cwd=project,
    ).stdout.decode()
    package_name = "fetap"
    github_url = "https://github.com/mmEissen/fetap"
    with open(release_txt, "a") as f:
        f.write(f"{package_name} @ git+{github_url}@{current_commit}\n")
    


cli()
