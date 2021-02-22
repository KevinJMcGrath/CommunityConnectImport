import integration.clients


from integration.decorators import sfdc_connection_check


def load_zendesk_client():
    return None

sfdc_client = integration.clients.SFDCClient()
zendesk_client = load_zendesk_client()