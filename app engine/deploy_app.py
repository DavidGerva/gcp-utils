
import subprocess
import argparse
import logging
import os


__version__ = "1.3.0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROD_PROJECT = "patent-box"
TEST_PROJECT = "patent-box-staging"  # PROD_PROJECT
VERSION = None

CHECK_EXSISTANCE = ["es_utilities",
                    "elastic_rsa_private_key.p12"]


def set_project(project):

    logger.warning(f"Setting project to {project}")
    command = f'gcloud config set project {project}'
    subprocess.run(command.split(), stdout=subprocess.PIPE)

def _pre_deploy():

    for element in CHECK_EXSISTANCE:
        if not os.path.exists(element):
            raise RuntimeError(f"The given {element} does not exist")

    # check is datastore
    # if not settings.USE_DATASTORE:
    #     logger.error("USE_DATASTORE is False, deploy in datastore")
    #     raise RuntimeError("USE_DATASTORE is False, deploy in datastore")

    subprocess.run("npm run build".split(), cwd="vueapp")

    global VERSION
    VERSION = None
    # VERSION = settings.__version__
    # VERSION = VERSION.replace(".", "-")


def _post_deploy():
    ...


def deploy_ae(promote=False):

    _pre_deploy()

    command = f"gcloud app deploy"
    if VERSION is not None:
        command += f"  --version {VERSION}"

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
        logger.info("Deploying in test environment")
        set_project(TEST_PROJECT)
    elif args.production:
        logger.info("Deploying in production environment")
        set_project(PROD_PROJECT)
    else:
        parser.error('No environment specified! add -t or -p')

    promote = False
    if args.promote:
        logger.info("Deploying promote")
        promote = True
    elif args.no_promote:
        logger.info("Deploying no promote")
    else:
        parser.error('No promote/no promote specified! add --promote or --no-promote')

    deploy_ae(promote=promote)

    # TODO: restore previous project
    # set_project('PROJ_NAME')


if __name__ == "__main__":
    main()
