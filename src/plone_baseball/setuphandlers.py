# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from plone import api
import requests
import json
import transaction


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


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.
    portal = api.portal.get()
    post_content(portal)


def post_content(portal):
    if not portal.get("players", False):
        mainfolder = api.content.create(
            type="Document",
            container=portal,
            title="Players",
            id="players",
        )

    json_array = json.loads(
        requests.get(
            "https://statsapi.mlb.com/api/v1/sports/1/players?season=2023"
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


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
    catalog = api.portal.get_tool(name="portal_catalog")

    for brain in catalog(portal_type="playercard"):
        obj = brain.getObject()

        try:
            # Below line needs a transaction to actually delete the object 
            api.content.delete(obj, check_linkintegrity=False)
            print(f"deleting {obj.absolute_url()}")

        except Exception as e:
            print(f"Error deleting object {obj.absolute_url()}: {e}")

    transaction.commit()
    