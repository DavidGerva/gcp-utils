
import subprocess
import argparse
import logging
import os


__version__ = "1.2.0"

logging.getLogger().setLevel(logging.INFO)

PROD_PROJECT = "patent-box"
TEST_PROJECT = "patent-box-staging"  # PROD_PROJECT

CHECK_EXSISTANCE = ["es_utilities",
                    "elastic_rsa_private_key.p12"]


def set_project(project):

    logging.warning(f"Setting project to {project}")
    command = f'gcloud config set project {project}'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process.wait()


def _pre_deploy():

    for element in CHECK_EXSISTANCE:
        if not os.path.exists(element):
            raise RuntimeError(f"The given {element} does not exist")

    # check is datastore
    # if not settings.USE_DATASTORE:
    #     logging.error("USE_DATASTORE is False, deploy in datastore")
    #     raise RuntimeError("USE_DATASTORE is False, deploy in datastore")

    subprocess.run("npm run build".split(), cwd="vueapp")


def _post_deploy():
    ...


def deploy_ae(promote=False):

    _pre_deploy()

    command = "gcloud app deploy"

    if not promote:
        command += " --no-promote"

    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process.wait()

    _post_deploy()


def main():

    # Define the program description
    text = 'GCP app engine utility program'

    # Initiate the parser with a description
    parser = argparse.ArgumentParser(description=text)
    # Add long and short argument
    parser.add_argument(
        "-t", "--test", help="Deploy in test environment", action="store_true")
    parser.add_argument(
        "-p", "--production", help="Deploy in production environment", action="store_true")

    # Add long and short argument
    parser.add_argument(
        "--promote", help="Deploy app promote", action="store_true")
    parser.add_argument(
        "--no-promote", help="Deploy app NO promote", action="store_true")

    # Read arguments from the command line
    args = parser.parse_args()

    if args.test:
        logging.info("Deploying in test environment")
        set_project(TEST_PROJECT)
    elif args.production:
        logging.info("Deploying in production environment")
        set_project(PROD_PROJECT)
    else:
        parser.error('No environment specified! add -t or -p')

    promote = False
    if args.promote:
        logging.info("Deploying promote")
        promote = True
    elif args.no_promote:
        logging.info("Deploying no promote")
    else:
        parser.error('No promote/no promote specified! add --promote or --no-promote')

    deploy_ae(promote=promote)

    # TODO: restore previous project
    # set_project('PROJ_NAME')


if __name__ == "__main__":
    main()
