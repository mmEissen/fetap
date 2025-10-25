

https://github.com/myoung34/docker-github-actions-runner/wiki/Usage#modifications


- Create file `ephemeral-github-actions-runner.service`
```
[Unit]
Description=Ephemeral GitHub Actions Runner Container
After=docker.service
Requires=docker.service
[Service]
TimeoutStartSec=0
Restart=always
ExecStartPre=-/usr/bin/docker stop %N
ExecStartPre=-/usr/bin/docker rm %N
ExecStartPre=-/usr/bin/docker pull myoung34/github-runner:latest
ExecStart=/usr/bin/docker run --rm \
                              --env-file /etc/ephemeral-github-actions-runner.env \
                              -e RUNNER_NAME=%H \
                              -v /var/run/docker.sock:/var/run/docker.sock \
                              --name %N \
                              myoung34/github-runner:latest
[Install]
WantedBy=multi-user.target
```
- `sudo install -m 644 ephemeral-github-actions-runner.service /etc/systemd/system/`

- Create file `ephemeral-github-actions-runner.env`:
```
RUNNER_SCOPE=repo
REPO_URL=https://github.com/mmEissen/fetap
LABELS=rpi-zero-2w
ACCESS_TOKEN=<access-token>
RUNNER_WORKDIR=/tmp/runner/work
DISABLE_AUTO_UPDATE=1
EPHEMERAL=1
```
- `sudo install -m 600 ephemeral-github-actions-runner.env /etc/`
- `sudo systemctl daemon-reload`
- `sudo systemctl enable ephemeral-github-actions-runner`
- `sudo systemctl start ephemeral-github-actions-runner`