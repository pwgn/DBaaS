# MariaDB-as-a-Service

## Requirements

- ansible
- python

## Setup

### Ansible

```
ansible-galaxy install -r requirements.yml
ansible-playbook install-mariadb.yml
```

### Python

Your typical venv thingy:

```
python -m venv env
source env/bin/activate
python create-database.py mydb
```

## Infra

Note that ip adresses and hostnames are hardcoded

- Docker containers act as vm-instances
- Ansible setup MariaDB on the vms
- Python script creates databases on the MariaDB instances

### Provision docker container:
Dockers are provisioned manually for now...

```
docker run --name vm-1 -t -d mmumshad/ubuntu-ssh-enabled
docker inspect vm-1 | grep "IPAddress"
# add vm to inventory like:
    vm-1:
      ansible_host: 172.17.0.2
```

### Create db:

Note that the python script only creates databases on the host `vm-1` for now.

```
python create-database.py mydb
```


