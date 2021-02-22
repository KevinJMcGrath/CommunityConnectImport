import logging

from optparse import OptionParser
from pathlib import Path

import api.app as api
import config
import package_logger
import template_import
import user_import

from integration import salesforce, zendesk

from symphony.bot_client import BotClient

package_logger.initialize_logging()


def run_from_config():
    file_path = Path(config.import_path).absolute()
    import_users(file_path=file_path)


def import_users(file_path):
    logging.getLogger()


    logging.info('New user onboarding started.')
    sym_client = BotClient(config.bot_config)

    user_dict = template_import.import_user_data(file_path)
    salesforce.import_salesforce_users(user_dict)
    user_import.onboard_users(user_dict, bot_client=sym_client)
    salesforce.update_contact_symphony_ids(user_dict)

    # salesforce.search_users_no_import(user_dict)
    salesforce.send_welcome_email(user_dict)

    zendesk.add_zendesk_entries(user_dict)

    logging.info('New user onboarding complete.')


def run_api():
    api.start_app()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", help="Specify the input CSV for adding to Symphony", dest="file_path",
                      default=None, type='string', action="store")
    parser.add_option("-c", "--config", help="Input CSV is specified in the config.json", dest="is_config",
                      default=None, action="store_true")

    options, args = parser.parse_args()

    if not options:
        run_api()
    elif options.file_path:
        import_users(options.file_path)
    elif options.is_config:
        run_from_config()
