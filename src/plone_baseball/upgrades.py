from plone import api
from plone.app.upgrade.utils import loadMigrationProfile

import logging

default_profile = 'profile-plone_baseball:default'
logger = logging.getLogger(__name__)


DEFAULT_BLOCKS = {
    "d3f1c443-583f-4e8e-a682-3bf25752a300": {"@type": "playerinfo"},
    "8624cf51-15d1-3051-3f51-3fd6597d84b1": {"@type": "seasonstats"},
    "7624cf59-05d0-4055-8f55-5fd6597d84b0": {"@type": "careerstats"},
}
DEFAULT_BLOCKS_LAYOUT = {
    "items": [
        "d3f1c443-583f-4e8e-a682-3bf25752a300",
        "8624cf51-15d1-3051-3f51-3fd6597d84b1",
        "7624cf59-05d0-4055-8f55-5fd6597d84b0",
    ]
}

def reload_gs_profile(context):
    loadMigrationProfile(
        context,
        'profile-plone_baseball:default',
    )

def reload_types(context=None):
    # reload type info
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(default_profile, 'typeinfo')

def upgrade_content(portal):
    if not portal.get("players", False):
        mainfolder = api.content.create(
            type="Document",
            container=portal,
            title="Players",
            id="players",
        )

    json_array = json.loads(
        requests.get(
            "https://statsapi.mlb.com/api/v1/sports/1/players?season=2024"
        ).text
    )
    store_list = [
        {
            "nameFirstLast": item["nameFirstLast"],
            "nameSlug": item["nameSlug"],
            "id": item["id"],
        }
        for item in json_array["people"]
    ]

    for item in store_list:
        try:
            obj = api.content.create(
                type="playercard",
                title=item["nameFirstLast"],
                id=item["nameSlug"],
                playerID=item["id"],
                container=portal["players"],
            )
            print(f"adding {obj.absolute_url()}")

        except Exception as e:
            print(f"Error adding object {obj.absolute_url()}: {e}")


def patch_upgraded_playercards(portal, DEFAULT_BLOCKS, DEFAULT_BLOCKS_LAYOUT):
    catalog = api.portal.get_tool(name="portal_catalog")

    for brain in catalog(portal_type="playercard"):
        obj = brain.getObject()
        try:
            obj.blocks = DEFAULT_BLOCKS
            print(f"updating blocks for {obj.absolute_url()}")
            obj.blocks_layout = DEFAULT_BLOCKS_LAYOUT
            print(f"updating blocks_layout for {obj.absolute_url()}")

        except Exception as e:
            print(f"Error updating object {obj.absolute_url()}: {e}")

def post_upgrade(context):
    """Post upgrade script"""
    # Do something at the end of the installation of this package.
    portal = api.portal.get()
    reload_gs_profile(context)
    reload_types(context=None)
    upgrade_content(portal)
    patch_upgraded_playercards(portal, DEFAULT_BLOCKS, DEFAULT_BLOCKS_LAYOUT)
