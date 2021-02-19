from integration import salesforce

from zenpy import Zenpy
from zenpy.lib.api_objects import Organization, User

import config

z_client = Zenpy(**config.zendesk)

def add_zendesk_entries(user_dict):

    for company_name, user_list in user_dict.items():
        first_user = user_list[0]
        sponsor_id = first_user.sponsor_sfdc_id
        domain = first_user.email.split('@')[1]
        sponsor_name = salesforce.get_account_name_by_id(sponsor_id)

        org = get_or_add_org(company_name, domain, sponsor_name)
        org_id = org.id

        for u in user_list:
            name = u.first_name + ' ' + u.last_name

            get_or_add_user(name, u.email, org_id)

def get_or_add_org(company_name: str, domain: str, sponsor_name: str):
    org_notes = 'CP2 pod; Sponsor: ' + sponsor_name

    e_org = search_orgs(company_name=company_name)
    if e_org:
        notes = e_org.notes + '\n\n' if e_org.notes else ''

        do_update = False
        if org_notes not in notes:
            e_org.notes = notes + org_notes
            do_update = True

        if domain not in e_org.domain_names:
            e_org.domain_names.append(domain)
            do_update = True

        if 'business' not in [t.lower() for t in e_org.tags]:
            e_org.tags.append('Business')
            do_update = True

        if 'community_connect' not in [t.lower() for t in e_org.tags]:
            e_org.tags.append('Community_Connect')
            do_update = True

        if do_update:
            # the api returns the updated version of the record, for what that's worth
            e_org = z_client.organizations.update(e_org)

        return e_org
    else:
        n_org = Organization(name=company_name, domain_names=[domain], notes=org_notes,
                             tags=['Community_Connect', 'Business'], shared_tickets=True, shared_comments=True)

        return z_client.organizations.create(n_org)


def get_or_add_user(fullname: str, email: str, org_id: str):
    user_notes = 'Community Connect Pod User'

    e_user = search_users(email)
    if e_user:
        notes = e_user.notes + '\n\n' if e_user.notes else ''

        do_update = False
        if user_notes not in notes:
            e_user.notes = notes + user_notes
            do_update = True

        if e_user.organization_id != org_id:
            e_user.organization_id = org_id
            do_update = True

        if not e_user.verified:
            e_user.verified = True
            do_update = True

        if 'community_connect' not in [t.lower() for t in e_user.tags]:
            e_user.tags.append('Community_Connect')
            do_update = True

        if do_update:
            e_user = z_client.users.update(e_user)
    else:
        n_user = User(name=fullname, email=email, organization_id=org_id, role='end-user', verified=True,
                      notes=user_notes, tags=['Community_Connect'], ticket_restriction='requested',
                      only_private_comments=False)

        z_client.users.create(n_user)

def search_orgs(company_name):
    orgs = z_client.search(name=company_name, type='organization')

    for org in orgs:
        if org.name == company_name:
            return org


def search_users(email: str):
    users = z_client.search(email=email, type='user')

    for u in users:
        if u.email == email:
            return u