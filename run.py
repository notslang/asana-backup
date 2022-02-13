import argparse
import asana
from pathlib import Path
from json import dumps


def main():
    parser = argparse.ArgumentParser(description='Backup everything from Asana.')
    parser.add_argument('token', metavar='PERSONAL_ACCESS_TOKEN', type=str,
                        help='Token for connecting to Asana')
    parser.add_argument('output_dir', metavar='OUTPUT_DIRECTORY', type=str,
                        help='Where to write the backup.')
    args = parser.parse_args()

    client = asana.Client.access_token(args.token)

    me = client.users.me()
    print("Authenticated as: " + me['name'])

    for workspace in client.workspaces.find_all():
        backup_workspace(client, workspace, args.output_dir)


def backup_workspace(client, workspace, directory):
    print("Backing up workspace: " + workspace["name"])
    workspace_dir = Path(directory, workspace["name"])
    workspace_dir.mkdir(parents=True, exist_ok=True)
    for project in client.projects.find_all(workspace=workspace['gid']):
        backup_project(client, project, workspace_dir)


def backup_project(client, project, directory):
    print("Backing up project: " + project["name"])
    full_project = client.projects.find_by_id(project['gid'])
    project_dir = directory / project['name']
    project_dir.mkdir(parents=True, exist_ok=True)

    info_file = project_dir / 'info.json'
    with info_file.open('w') as f:
        f.write(dumps(full_project))

    tasks_file = project_dir / 'tasks.json'
    with tasks_file.open('w') as f:
        for task in client.tasks.find_by_project(project['gid']):
            full_task = get_task_object(client, task)
            f.write(dumps(full_task))


def get_task_object(client, task):
    full_task = client.tasks.find_by_id(task['gid'])
    stories = list(client.stories.find_by_task(task['gid']))
    full_task['stories'] = stories
    return full_task


main()
