from plone import schema
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope.interface import implementer


class IPlayerCard(model.Schema):
    """Dexterity-Schema for PlayerCards"""

    firstname = schema.TextLine(
        title="First Name",
        description="First Name (or names) of the player",
        required=True,
    )

    lastname = schema.TextLine(
        title="Last Name",
        description="Last Name (or names) of the player",
        required=True,
    )

    birthdate = schema.Date(
        title="Birthdate",
        description="Birthdate of the player",
        required=True,
    )

    positions = schema.TextLine(
        title="Fielding positions",
        required=True,
    )

    currentteam = schema.TextLine(
        title="Current Team",
        required=True,
    )

    image = NamedBlobImage(
        title="Image",
        description="Portrait of the player",
        required=False,
    )

    blurb = RichText(
        title="Blurb",
        description="Player blurb (max. 2000 characters)",
        max_length=2000,
        required=True,
    )


@implementer(IPlayerCard)
class PlayerCard(Container):
    """PlayerCard instance class"""
