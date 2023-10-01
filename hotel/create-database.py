from pprint import pprint
import argparse
import subprocess
import yaml

ANSIBLE_HOME = '../ansible'
ANSIBLE_HOST_VARS_DIR = f'{ANSIBLE_HOME}/host_vars'
ANSIBLE_CREATE_DB_PLAYBOOK = f'create-database.yml'
ANSIBLE_MARIADB_HOST = 'vm-1'

YML_MYSQL_DATABASES_KEY = 'mysql_databases'
YML_MYSQL_USERS_KEY = 'mysql_users'

def generate_yml_db(database_name):
    new_entry = {
        'name': database_name,
        'collation': 'utf8_general_ci',
        'encoding': 'utf8',
        'replicate': 1
    }

    return new_entry

def generate_yml_user(database_name):
    new_entry = {
        'name': f'admin-{database_name}',
        'host': '172.17.0.1',
        'password': 'secret',
        'priv': f'{database_name}.*:ALL'
    }

    return new_entry

def update_server_databases(host, database_name, host_vars_file):

    with open(host_vars_file, 'r') as file:
        host_yml = yaml.safe_load(file)

    existings_dbs = [db['name'] for db in host_yml[YML_MYSQL_DATABASES_KEY]]
    if database_name in existings_dbs:
        raise ValueError(f'database_name: {database_name} already exists')

    mysql_db_entry = generate_yml_db(database_name)
    host_yml[YML_MYSQL_DATABASES_KEY].append(mysql_db_entry)

    mysql_user_entry = generate_yml_user(database_name)
    host_yml[YML_MYSQL_USERS_KEY].append(mysql_user_entry)


    with open(host_vars_file, 'w') as file:
        yaml.safe_dump(host_yml, file)

    account = {
        'database_host': host,
        'database_name': database_name,
        'admin_user': mysql_user_entry['name'],
        'admin_password': mysql_user_entry['password']
    }

    return account


def run_ansible_playbook(playbook_path, working_dir):
    try:
        # Run the ansible-playbook command as a subprocess
        subprocess.run(['ansible-playbook', playbook_path], check=True, cwd=working_dir)
        print("Ansible playbook executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Ansible playbook: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate YAML for MySQL database and user")
    parser.add_argument("database_name", help="Name of the database")

    args = parser.parse_args()

    host_vars_file = f'{ANSIBLE_HOST_VARS_DIR}/{ANSIBLE_MARIADB_HOST}.yml'
    account = update_server_databases(ANSIBLE_MARIADB_HOST, args.database_name, host_vars_file)

    run_ansible_playbook(ANSIBLE_CREATE_DB_PLAYBOOK, ANSIBLE_HOME)

    pprint(f'Database provisioned successfully!')

    pprint(account)
    pprint(f'Get started:')
    pprint(f'mysql -u {account["admin_user"]} -p{account["admin_password"]}')

