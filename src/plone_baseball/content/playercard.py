from plone import schema
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope.interface import implementer


class IPlayerCard(model.Schema):
    """Dexterity-Schema for PlayerCards"""

    playerID = schema.TextLine(
        title="Player ID",
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
        required=False,
    )


@implementer(IPlayerCard)
class PlayerCard(Container):
    """PlayerCard instance class"""
