class LogType:
    def __init__(self, config_json):
        self.is_log_to_file = config_json['log_to_file']
        self.log_path = config_json['log_path']
        self.verbose: bool = config_json['verbose']

