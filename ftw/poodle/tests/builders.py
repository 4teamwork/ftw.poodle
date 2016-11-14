from ftw.builder import builder_registry
from ftw.builder.archetypes import ArchetypesBuilder


class PoodleBuilder(ArchetypesBuilder):
    portal_type = 'Poodle'

builder_registry.register('poodle', PoodleBuilder)
