from plone import api
from plone.app.upgrade.utils import loadMigrationProfile

import json
import requests
import transaction


def reload_gs_profile(context):
    loadMigrationProfile(
        context,
        "profile-plone_baseball:default",
    )


def move_inactive_playercards(portal):
    if not portal.get("inactive-players", False):
        mainfolder = api.content.create(
            type="Document",
            container=portal,
            title="Inactive Players",
            id="inactive-players",
        )

    json_array = json.loads(
        requests.get(
            "https://statsapi.mlb.com/api/v1/sports/1/players?season=2024"
        ).text
    )
    store_list = []
    for item in json_array["people"]:
        store_list.append(item["nameSlug"])

    catalog = api.portal.get_tool(name="portal_catalog")

    for brain in catalog(portal_type="playercard"):
        obj = brain.getObject()

        # Below line needs a transaction to actually delete the object
        if obj.id not in store_list:
            api.content.move(source=obj, target=portal["inactive-players"])
            print(f"moving {obj.absolute_url()}")

        transaction.commit()


def post_upgrade(context):
    """Post upgrade script"""
    # Do something at the end of the installation of this package.
    portal = api.portal.get()
    move_inactive_playercards(portal)
    reload_gs_profile(context)
