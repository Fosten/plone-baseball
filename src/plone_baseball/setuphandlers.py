# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import json
import requests
import transaction


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


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "plone_baseball:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["plone_baseball.upgrades"]


def post_content(portal):
    if not portal.get("players", False):
        mainfolder = api.content.create(
            type="Document",
            container=portal,
            title="Players",
            id="players",
        )
        api.content.transition(obj=mainfolder, transition="publish")

    json_array = json.loads(
        requests.get(
            "https://statsapi.mlb.com/api/v1/sports/1/players?season=2025"
        ).text
    )
    store_list = [
        {
            "nameFirstLast": item["nameFirstLast"],
            "nameSlug": item["nameSlug"],
            "id": item["id"],
            "fullFMLName": item["fullFMLName"],
        }
        for item in json_array["people"]
    ]

    for item in store_list:
        try:
            obj = api.content.create(
                type="playercard",
                title=item["nameFirstLast"],
                description="Player information and statistics for "
                + item["fullFMLName"]
                + " better known as Major League Baseball player "
                + item["nameFirstLast"],
                id=item["nameSlug"],
                playerID=item["id"],
                container=portal["players"],
            )
            api.content.transition(obj=obj, transition="publish")
            print(f"adding {obj.absolute_url()}")

        except Exception as e:
            print(f"Error adding object: {e}")


def patch_playercards(portal, DEFAULT_BLOCKS, DEFAULT_BLOCKS_LAYOUT):
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


def remove_playercards(portal):
    catalog = api.portal.get_tool(name="portal_catalog")

    for brain in catalog(portal_type="playercard"):
        obj = brain.getObject()

        try:
            # Below line needs a transaction to actually delete the object
            api.content.delete(obj, check_linkintegrity=False)
            transaction.commit()
            print(f"deleting {obj.absolute_url()}")

        except Exception as e:
            print(f"Error deleting object {obj.absolute_url()}: {e}")


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.
    portal = api.portal.get()
    post_content(portal)
    patch_playercards(portal, DEFAULT_BLOCKS, DEFAULT_BLOCKS_LAYOUT)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
    portal = api.portal.get()
    remove_playercards(portal)
