
import subprocess
import argparse
import logging
logging.getLogger().setLevel(logging.INFO)


PROD_PROJECT = "patent-box"
TEST_PROJECT = "patent-box-staging"  # PROD_PROJECT


def set_project(project):

    logging.warning(f"Setting project to {project}")
    command = f'gcloud config set project {project}'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process.wait()


def _modify_secrets(remove_credentials):

    # remove gcloud credentials from secrets
    lines = []
    with open("secrets.env", 'r') as ofile:
        lines = ofile.readlines()

    for idx, line in enumerate(lines):
        if remove_credentials:
            if line.startswith("GOOGLE_APPLICATION_CREDENTIALS="):
                lines[idx] = "#" + line
                break
        else:
            if line.startswith("#GOOGLE_APPLICATION_CREDENTIALS="):
                lines[idx] = line[1:]
                break

    with open("secrets.env", 'w') as ofile:
        ofile.writelines(lines)


def deploy_ae(promote=False):

    # _modify_secrets(True)

    command = "gcloud app deploy"

    if not promote:
        command += " --no-promote"

    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process.wait()

    # remove gcloud credentials from secrets
    # _modify_secrets(False)


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
