import re
import sys
from inspect import getmembers
from types import ModuleType

from .base import aspectbase
from .meta import aspectclass
from .taste import Taste, TasteError

from .root import Root
from .Metadata import Metadata
from .Redundancy import Redundancy
from .Spelling import Spelling


__all__ = ['Root', 'Taste', 'TasteError', 'aspectclass', 'aspectbase']


class aspectsModule(ModuleType):
    """
    A special module wrapper for ``coalib.bearlib.aspects``, allowing
    case-insensitive aspect lookup by name via direct indexing :)

    >>> import coalib.bearlib.aspects

    >>> coalib.bearlib.aspects['Metadata']
    <aspectclass 'Root.Metadata'>

    >>> coalib.bearlib.aspects['commitmessage']
    <aspectclass 'Root.Metadata.CommitMessage'>

    >>> coalib.bearlib.aspects['shortlog.colonExistence']
    <aspectclass 'Root.Metadata.CommitMessage.Shortlog.ColonExistence'>
    """

    def __init__(self, module):
        """
        Take over all members from original `module` object.
        """
        super().__init__(module.__name__)
        self.__dict__.update(getmembers(module))

    def __getitem__(self, aspectname):
        regex = re.compile('(^|\.)%s$' % aspectname.lower())
        matches = []

        def search(aspects):
            """
            Recursively search in `aspects` for those matching
            case-insensitively the given ``aspectname``.
            """
            for aspect in aspects:
                if regex.search(aspect.__qualname__.lower()):
                    matches.append(aspect)
                if aspect.subaspects:
                    search(aspect.subaspects.values())

        search([Root])
        if not matches:
            raise LookupError('no aspect named %s' % repr(aspectname))

        if len(matches) > 1:
            raise LookupError('multiple aspects named %s. choose from %s' % (
                repr(aspectname),
                repr(sorted(matches, key=lambda a: a.__qualname__))))

        return matches[0]


# replace original module with wrapper
sys.modules[__name__] = aspectsModule(sys.modules[__name__])
