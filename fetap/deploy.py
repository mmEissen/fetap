import os
import subprocess
from os import path
import tempfile


def release():
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


def install(remotehost: str, is_dev: bool) -> None:
    project = path.dirname(path.dirname(__file__))
    install_dir = "/opt/fetap"
    if is_dev:
        service_args = (
            f"--interval=1 --sigterm-timeout=5 {install_dir}/release.txt fetap run"
        )
    else:
        service_args = f"--interval={60 * 5} --sigterm-timeout={60 * 60 * 4} https://raw.githubusercontent.com/mmEissen/fetap/main/requirements.txt fetap run"
    service_user = os.environ.get("USER")
    service_template = path.join(project, "autoupdater.service.template")
    with open(service_template) as f:
        service_data = f.read().format(
            args=service_args, user=service_user, install_dir=install_dir
        )

    release_txt = path.join(project, "release.txt")
    bootstrap_sh = path.join(project, "rpi_bootstrap.sh")

    subprocess.run(
        ["ssh", remotehost, f"sudo mkdir -p {install_dir}"],
        check=True,
    )
    subprocess.run(
        ["ssh", remotehost, f"sudo chown $USER: {install_dir}"],
        check=True,
    )
    with tempfile.TemporaryDirectory() as tmp_dir, open(
        service_file := path.join(tmp_dir, "fetap.service"), "w"
    ) as file:
        file.write(service_data)
        file.close()
        subprocess.run(
            [
                "scp",
                bootstrap_sh,
                service_file,
            ]
            + [release_txt] * is_dev
            + [
                f"{remotehost}:{install_dir}",
            ],
            check=True,
        )
    subprocess.run(["ssh", remotehost, f"{install_dir}/rpi_bootstrap.sh"])


def uninstall(remotehost: str) -> None:
    install_dir = "/opt/fetap"

    subprocess.run(
        ["ssh", remotehost, f"sudo rm -rf {install_dir}"],
    )
    subprocess.run(
        ["ssh", remotehost, f"sudo systemctl stop fetap"],
    )
    subprocess.run(
        ["ssh", remotehost, f"sudo systemctl disable fetap"],
    )
    subprocess.run(
        ["ssh", remotehost, f"sudo rm /lib/systemd/system/fetap.service"],
    )


def logs(remotehost: str) -> None:
    subprocess.run(
        ["ssh", remotehost, f"sudo journalctl -f -u fetap.service"],
    )


def deploy_dev():
    pass
