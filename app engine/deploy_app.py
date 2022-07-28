
import subprocess
import argparse
import logging


__version__ = "2.0.0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppEngineDeployer():

    def __init__(self, test_env=True, promote=False) -> None:
        self.PROD_PROJECT = None
        self.TEST_PROJECT = None
        self.VERSION = None

        self.test_env = test_env
        self.promote = promote

        self._set_variables()
        if self.PROD_PROJECT is None:
            raise RuntimeError("Vars not defined")

        if self.PROD_PROJECT == self.TEST_PROJECT:
            logger.warning("PROD_PROJECT and TEST_PROJECT are the same!")

        logger.info(f"Deploying in {'test' if self.test_env else 'prod'} environment")
        logger.info(f"Deploying in {'promote' if self.promote else 'NO promote'} environment")

    def _set_variables(self):

        if self.VERSION is not None and not self.promote:
            self.VERSION += "-np"

    def set_project(self):

        project = self.TEST_PROJECT if self.test_env else self.PROD_PROJECT

        logging.warning(f"Setting project to {project}")
        command = f'gcloud config set project {project}'
        subprocess.run(command.split(), stdout=subprocess.PIPE)

    def _pre_deploy(self):
        pass

    def deploy_ae(self):

        self._pre_deploy()

        command = f"gcloud app deploy"
        if self.VERSION is not None:
            command += f"  --version {self.VERSION}"

        if not self.promote:
            command += " --no-promote"

        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        process.wait()

        # _post_deploy()

# =================================
# PARTE SPECIFICA
# =================================

# from patent_box import settings


class ActualDeployer(AppEngineDeployer):

    # TODO: edit here
    def _set_variables(self):
        self.PROD_PROJECT = "PROJECT_NAME"
        self.TEST_PROJECT = self.PROD_PROJECT

        # self.VERSION = settings.__version__
        # self.VERSION = self.VERSION.replace(".", "-")

        return super()._set_variables()

    def _pre_deploy(self):

        # check is datastore
        # if not settings.USE_DATASTORE:
        #     logging.error("USE_DATASTORE is False, deploy in datastore")
        #     raise RuntimeError("USE_DATASTORE is False, deploy in datastore")

        return super()._pre_deploy()

# =================================
# FINE PARTE SPECIFICA
# =================================


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

    test = True
    if args.test:
        test = True
    elif args.production:
        test = False
    else:
        parser.error('No environment specified! add -t or -p')

    promote = False
    if args.promote:
        promote = True
    elif args.no_promote:
        promote = False
    else:
        parser.error('No promote/no promote specified! add --promote or --no-promote')

    deployer = ActualDeployer(test_env=test, promote=promote)
    deployer.deploy_ae()


if __name__ == "__main__":
    main()
