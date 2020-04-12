from optparse import OptionParser
from pathlib import Path

import config
import package_logger
import salesforce
import template_import
import user_import

package_logger.initialize_logging()

def run_main(file_path: str):
    if not file_path:
        if config.import_path:
            file_path = config.import_path
        else:
            file_path = input("Please specify the user import file path:  \n")

    if file_path:
        import_users(Path(file_path))
    else:
        print('Invalid file path.')
        exit(1)

def import_users(file_path):
    user_dict = template_import.import_user_data(file_path)
    sfdc_imported_users = salesforce.import_salesforce_users(user_dict)
    user_import.onboard_users(sfdc_imported_users)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", help="Specify the input CSV for adding to Symphony", dest="file_path",
                      default=None, action="store_true")

    options, args = parser.parse_args()

    run_main(options.file_path)