
import subprocess
import argparse
import logging
import os
import json

logging.getLogger().setLevel(logging.INFO)


# deploy_cf script version
__version__ = "2.1.0"


# =============================================================================
# TODO: change things here
TEST_PROJECT = "patent-box-staging"
PROD_PROJECT = "patent-box"  # TEST_PROJECT
REGION = "europe-west3"

ALSO_INCLUDE_ENV = False
METHOD_NAME = 'generate_report'
TIMEOUT = "540"  # "60" .. "540"
MEMORY = "256MB"  # "512MB"  "1GB" .. "8GB"

CHECK_EXSISTANCE = ["es_utilities",
                    "elastic_rsa_private_key.p12"]

# =============================================================================


def deploy_cf():

    command = f"""
        gcloud functions deploy {METHOD_NAME}
        --runtime python37
        --region {REGION}
        --trigger-http
        --timeout {TIMEOUT}
        --memory {MEMORY}
        """

    if ALSO_INCLUDE_ENV:
        command += " --env-vars-file env.yaml"

    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process.wait()


def prepare_deploy():
    """
    This function is called before the deployment.
    """
    for element in CHECK_EXSISTANCE:
        if not os.path.exists(element):
            raise RuntimeError(f"The given {element} does not exist")


def post_deploy():
    """
    This function is called after the deployment is done.
    It restores some lines in .gitignore file.
    """
    # lines_to_comment = [
    #     "# secrets.env\n",
    #     "# es_utilities*\n",
    #     "# trix_corpus_utils*\n"
    #     ]

    # lines = []
    # with open(".gitignore", "r") as f:
    #     lines = f.readlines()

    # for idx, line in enumerate(lines):
    #     if line in lines_to_comment:
    #         lines[idx] = line.replace("# ", "")

    # with open(".gitignore", "w") as f:
    #     f.writelines(lines)
    ...


def create_task(test=False):

    from google.cloud import tasks_v2

    payload = {"years": [2000], "months": [3, 4, 5]}  # TODO: change

    # TODO: change
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "PATH TO JSON CREDENTIALS"

    project_id = TEST_PROJECT if test else PROD_PROJECT
    os.environ['GCP_PROJECT'] = project_id

    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(
        project_id, "europe-west3", "QUEUE NAME")  # TODO: change
    service_account_email = "SERVICE ACCOUNT EMAIL"  # TODO: change

    task = {
        "http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            # The full url path that the task will be sent to.
            "url": "CF URL",  # TODO: change
            "oidc_token": {"service_account_email": service_account_email},
        }
    }

    if payload is None:
        raise RuntimeError('create_task function failed: empty payload')

    ## TODO: change
    to_pass = json.dumps(payload)
    converted_payload = to_pass.encode()
    task["http_request"]["body"] = converted_payload
    task["http_request"]["headers"] = {
        "Content-type": "application/json"
    }

    try:
        response = client.create_task(request={"parent": parent, "task": task})
        logging.info(f"Task created")
    except Exception as ex:
        logging.error(f"Create_task function failed")
        raise RuntimeError(
            'create_task function failed: %s' % repr(ex))


def set_project(project):

    logging.warning("Setting project to: %s" % project)
    command = f'gcloud config set project {project}'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process.wait()


def main():

    # Define the program description
    text = 'GCP cloud functions utility program'

    # Initiate the parser with a description
    parser = argparse.ArgumentParser(description=text)
    # Add long and short argument
    parser.add_argument(
        "-t", "--test", help="Deploy in test environment", action="store_true")
    parser.add_argument(
        "-p", "--production", help="Deploy in production environment", action="store_true")
    parser.add_argument(
        "--task", help="Create a task for this cf", action="store_true")

    # Read arguments from the command line
    args = parser.parse_args()

    if args.test:
        logging.info("Deploying in test environment")
        set_project(TEST_PROJECT)
        prepare_deploy()
        deploy_cf()
        post_deploy()

    elif args.production:
        logging.info("Deploying in production environment")
        set_project(PROD_PROJECT)
        prepare_deploy()
        deploy_cf()
        post_deploy()

    elif args.task:
        logging.info("Creating task for this cf")
        set_project(PROD_PROJECT)
        create_task(test=False)

    else:
        parser.error('No option specified! add -t or -p')

    # TODO: restore previous project
    # set_project('PROJ_NAME')


if __name__ == "__main__":
    main()
