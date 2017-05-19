"""Coredata Module

Core is a rather ambigious term - includes upfront questions such
as DOB and patient / staff role.  Basic diagnosis and procedure
questions.

Interventions will sometimes require their own set of data, for which the
`/api/coredata/*` endpoints exist.

"""
from abc import ABCMeta, abstractmethod
from flask import current_app
import sys

from .audit import Audit
from .intervention import UserIntervention, INTERVENTION
from .fhir import CC
from .organization import Organization, OrgTree
from .role import ROLE
from .tou import ToU


class Coredata(object):
    """Singleton managing coredata **model** logic, mostly shortcuts"""

    class __singleton(object):
        """Hidden inner class defines all the public methods

        Outer class accessors wrap, so any calls hit the single
        instance and appear at outer class scope.
        """
        def __init__(self):
            self._registered = []

        def register_class(self, cls):
            if cls not in self._registered:
                self._registered.append(cls)

        def required(self, user):
            # Returns list of datapoints required for user
            items = []
            for cls in self._registered:
                instance = cls()
                if instance.required(user):
                    items.append(instance.id)
            return items

        def initial_obtained(self, user):
            # Check if all registered methods have data
            for cls in self._registered:
                instance = cls()
                if not instance.required(user):
                    continue
                if instance.hasdata(user):
                    continue
                current_app.logger.debug(
                    'intial NOT obtained for at least {}'.format(cls.__name__))
                return False
            return True

        def still_needed(self, user):
            # Returns list of registered still needing data
            needed = []
            for cls in self._registered:
                instance = cls()
                if not instance.required(user):
                    continue
                if not instance.hasdata(user):
                    needed.append(instance.id)
            if needed:
                current_app.logger.debug(
                    'intial still needed for {}'.format(needed))
            return needed

    instance = None
    def __new__(cls):
        if not Coredata.instance:
            Coredata.instance = Coredata.__singleton()
        return Coredata.instance

    def __getattr__(self, name):
        """Delegate to hidden inner class"""
        return getattr(self.instance, name)

    def __setattr__(self, name):
        """Delegate to hidden inner class"""
        return setattr(self.instance, name)


class CoredataPoint(object):
    """Abstract base class - defining methods each datapoint needs"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def required(self, user):
        """Returns true if required for user, false otherwise

        Applications are configured to request a set of core data points.
        This method returns True if the active configuration includes the
        datapoint for the user, regardless of whether or not a value has
        been acquired.  i.e., should the user ever be asked for this point,
        or should the control be hidden regardless of the presence of data.

        NB - the user's state is frequently considered.  For example,
        belonging to an intervention or organization may imply the datapoint
        should never be an available option for the user to set.

        """
        raise NotImplemented

    @abstractmethod
    def hasdata(self, user):
        """Returns true if the data has been obtained, false otherwise"""
        raise NotImplemented

    @property
    def id(self):
        """Returns identifier for class - namely lowercase w/o Data suffix"""
        name = self.__class__.__name__
        return name[:-4].lower()


def CP_user(user):
    """helper to determine if the user has Care Plan access"""
    return UserIntervention.user_access_granted(
        user_id=user.id,
        intervention_id=INTERVENTION.CARE_PLAN.id)


def SR_user(user):
    """helper to determine if the user has Sexual Recovery access"""
    return UserIntervention.user_access_granted(
        user_id=user.id,
        intervention_id=INTERVENTION.SEXUAL_RECOVERY.id)


def IRONMAN_user(user):
    """helper to determine if user is associated with the IRONMAN org"""
    # NB - not all systems have this organization!
    iron_org = Organization.query.filter_by(name='IRONMAN').first()
    if iron_org:
        OT = OrgTree()
        for org_id in (o.id for o in user.organizations if o.id):
            top_of_org = OT.find(org_id).top_level()
            if top_of_org == iron_org.id:
                return True
    return False


###
## Series of "datapoint" collection classes follow
###

class DobData(CoredataPoint):

    def required(self, user):
        # DOB is only required for patient
        if user.has_role(ROLE.PATIENT):
            return True
        return False

    def hasdata(self, user):
        return user.birthdate is not None


class RaceData(CoredataPoint):

    def required(self, user):
        if SR_user(user):
            return False
        if IRONMAN_user(user):
            return False
        if user.hasrole(ROLE.PATIENT):
            return True
        return False

    def hasdata(self, user):
        return len(user.races) > 0


class EthnicityData(CoredataPoint):

    def required(self, user):
        if SR_user(user):
            return False
        if IRONMAN_user(user):
            return False
        if user.hasrole(ROLE.PATIENT):
            return True
        return False

    def hasdata(self, user):
        return len(user.ethnicities) > 0


class IndigenousData(CoredataPoint):

    def required(self, user):
        if SR_user(user):
            return False
        if IRONMAN_user(user):
            return False
        if user.hasrole(ROLE.PATIENT):
            return True
        return False

    def hasdata(self, user):
        return len(user.indigenous) > 0


class RoleData(CoredataPoint):

    def required(self, user):
        return not SR_user(user)

    def hasdata(self, user):
        if len(user.roles) > 0:
            return True


class OrgData(CoredataPoint):

    def required(self, user):
        if SR_user(user) or CP_user(user):
            return False
        if any(map(
            user.has_role, (ROLE.PATIENT, ROLE.STAFF, ROLE.STAFF_ADMIN))):
            return True
        return False

    def hasdata(self, user):
        return user.organizations.count() > 0


class ClinicalData(CoredataPoint):

    def required(self, user):
        if SR_user(user):
            return False
        return user.has_role(ROLE.PATIENT)

    def hasdata(self, user):
        required = {item: False for item in (
            CC.BIOPSY, CC.PCaDIAG)}

        for obs in user.observations:
            if obs.codeable_concept in required:
                required[obs.codeable_concept] = True
        return all(required.values())


class LocalizedData(CoredataPoint):

    def required(self, user):
        if SR_user(user):
            return False
        if current_app.config.get('LOCALIZED_AFFILIATE_ORG'):
            # Some systems use organization affiliation to denote localized
            # on these systems, we don't ask about localized - let
            # the org check worry about that
            return False
        return user.has_role(ROLE.PATIENT)

    def hasdata(self, user):
        for obs in user.observations:
            if obs.codeable_concept == CC.PCaLocalized:
                return True
        return False


class NameData(CoredataPoint):

    def required(self, user):
        return not SR_user(user)

    def hasdata(self, user):
        return user.first_name and user.last_name


class TouData(CoredataPoint):

    def required(self, user):
        return not SR_user(user)

    def hasdata(self, user):
        return ToU.query.join(Audit).filter(
            Audit.user_id==user.id).count() > 0


def configure_coredata(app):
    """Configure app for coredata checks"""
    coredata = Coredata()

    # Add static list of "configured" datapoints
    config_datapoints = app.config.get(
        'REQUIRED_CORE_DATA',
        ['name', 'dob', 'role', 'org', 'clinical', 'localized', 'tou',
         'race', 'ethnicity', 'indigenous'])

    for name in config_datapoints:
        # Camel case with 'Data' suffix - expect to find class in local
        # scope or raise exception
        cls_name = name.title() + 'Data'
        try:
            # limit class loading to this module - die if not found
            cls = getattr(sys.modules[__name__], cls_name)
        except AttributeError as e:
            app.logger.error("Configuration for REQUIRED_CORE_DATA includes "
                             "unknown element '{}' - can't continue".format(
                                 name))
            raise e
        coredata.register_class(cls)
