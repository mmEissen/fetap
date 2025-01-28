# Server deployment

- Most things are automated via github actions
- When starting on a fresh server, one thing to note is that nginx won't run correctly out of the box
    - Why? Because the ssl certificates don't exist yet
    - how to fix
        - in nginx disable the 443 configs in `server/fetap-nginx/http.conf`
        - deploy via github actions
        - ssh into the server
        - run `docker compose run certbot` manually
        - complete the prompts and make sure certbot succeeded
        - if all went well, you should now be able to run certbot again, but this time it will not prompt you and instead try to renew the existing cert
        - quit ssh session
        - re-add the configs into `server/fetap-nginx/http.conf`
        - deploy again


... I am sure I could make this more automatic, but I hope this is a rare case :/
