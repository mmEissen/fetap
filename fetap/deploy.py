import os
import subprocess
from os import path
import tempfile


PROJECT_DIR = path.dirname(path.dirname(__file__))
RELEASE_TXT = path.join(PROJECT_DIR, "release.txt")
INSTALL_DIR = "/opt/fetap"
PACKAGE_NAME = "fetap"
GITHUB_URL = "https://github.com/mmEissen/fetap"


def release(output: str=RELEASE_TXT, is_dev: bool = False):
    subprocess.run(
        ["poetry", "export", "--without-hashes", f"--output={output}"],
        check=True,
        cwd=PROJECT_DIR,
    )
    current_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        check=True,
        cwd=PROJECT_DIR,
    ).stdout.decode()
    with open(output, "a") as f:
        if is_dev:
            f.write(f"-e {INSTALL_DIR}/src/fetap\n")
        else:
            f.write(f"{PACKAGE_NAME} @ git+{GITHUB_URL}@{current_commit}\n")


def install(remotehost: str, is_dev: bool) -> None:
    if is_dev:
        service_args = (
            f"--interval=1 --sigterm-timeout=5 {INSTALL_DIR}/release.txt {PACKAGE_NAME} run"
        )
    else:
        service_args = f"--interval={60 * 5} --sigterm-timeout={60 * 60 * 4} https://raw.githubusercontent.com/mmEissen/fetap/main/requirements.txt {PACKAGE_NAME} run"
    service_user = os.environ.get("USER")
    service_template = path.join(PROJECT_DIR, "autoupdater.service.template")
    with open(service_template) as f:
        service_data = f.read().format(
            args=service_args, user=service_user, install_dir=INSTALL_DIR
        )

    bootstrap_sh = path.join(PROJECT_DIR, "rpi_bootstrap.sh")

    subprocess.run(
        ["ssh", remotehost, f"sudo mkdir -p {INSTALL_DIR}"],
        check=True,
    )
    subprocess.run(
        ["ssh", remotehost, f"sudo chown $USER: {INSTALL_DIR}"],
        check=True,
    )

    if is_dev:
        deploy_dev(remotehost)

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
            + [
                f"{remotehost}:{INSTALL_DIR}",
            ],
            check=True,
        )
    subprocess.run(["ssh", remotehost, f"{INSTALL_DIR}/rpi_bootstrap.sh"])


def uninstall(remotehost: str) -> None:
    subprocess.run(
        ["ssh", remotehost, f"sudo rm -rf {INSTALL_DIR}"],
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
        ["ssh", remotehost, f"sudo journalctl -f -u fetap.service -n 100"],
    )


def deploy_dev(remotehost: str, show_logs: bool=False) -> None:
    subprocess.run(
        [
            "rsync",
            "-P",
            "-r",
            PROJECT_DIR,
            f"{remotehost}:{INSTALL_DIR}/src",
        ],
        check=True,
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        dev_release_txt = path.join(tmp_dir, "release.txt")
        release(dev_release_txt, is_dev=True)
        subprocess.run(
            [
                "scp",
                dev_release_txt,
                f"{remotehost}:{INSTALL_DIR}",
            ],
            check=True,
        )
    if show_logs:
        logs(remotehost)
