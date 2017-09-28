"""Tests for mappers/datacite.py."""

from nose.tools import eq_
from unittest import TestCase

from ckanext.etsin.mappers.datacite import datacite_mapper
from ckanext.harvest.model import HarvestObject

from .helpers import _get_file_as_lxml


class TestMappersDataCite(TestCase):

    @classmethod
    def setup_class(cls):
        cls.metax_dict = datacite_mapper(
            _get_file_as_lxml('datacite/datacite1.xml'))

    def testPreferredIdentifier(self):
        assert self.metax_dict['research_dataset'][
            'preferred_identifier'] == 'http://dx.doi.org/10.18150/9887707'

    # TODO: test creators with identifiers and affiliations
    def testCreator(self):
        assert {"name": "Drozdzal, Pawel"} in self.metax_dict[
            'research_dataset']['creator']
        assert {"name": "Kierzek, Ryszard"} in self.metax_dict[
            'research_dataset']['creator']
        assert {"name": "Gilski, Miroslaw"} in self.metax_dict[
            'research_dataset']['creator']
        assert {"name": "Jaskolski, Mariusz"} in self.metax_dict[
            'research_dataset']['creator']

    # TODO: current test file doesn't have language
    def testLanguage(self):
        pass

    def testTitle(self):
        assert self.metax_dict['research_dataset']['title'] == {"default": "Raw X-ray diffraction data for DNA-RNA chimera crystals in complex with barium cations"}

    def testPublisher(self):
        assert {"name": "RepOD"} in self.metax_dict[
            'research_dataset']['publisher']

    def testPublicationYear(self):
        assert self.metax_dict['research_dataset']['issued'] == '2015'

    # TODO: current test file doesn't have YSO subjects
    def testSubject(self):
        assert "DNA-RNA chimera" in self.metax_dict[
            'research_dataset']['keyword']
        assert "X-ray synchrotron diffraction images" in self.metax_dict[
            'research_dataset']['keyword']
        assert "left-handed Z-type duplex" in self.metax_dict[
            'research_dataset']['keyword']
        assert "multi-domain twinning" in self.metax_dict[
            'research_dataset']['keyword']
        assert "pseudosymmetry" in self.metax_dict[
            'research_dataset']['keyword']
        assert "twin detection" in self.metax_dict[
            'research_dataset']['keyword']
        assert "Natural and mathematical sciences" in self.metax_dict[
            'research_dataset']['keyword']
        assert not self.metax_dict['research_dataset']['theme']

    # TODO: current test file doesn't have contributors
    def testContributor(self):
        pass

    # TODO: Date mapping hasn't been compeleted
    def testDate(self):
        pass

    # TODO: current test file doesn't have alternate identifiers with type URL
    def testAlternateIdentifier(self):
        assert not self.metax_dict['research_dataset']['other_identifier']

    # TODO: current test file doesn't have related identifiers
    def testRelatedIdentifier(self):
        pass

    # TODO: current test file doesn't have version
    def testVersion(self):
        pass

    def testRights(self):
        assert {
            "description": "Open Access",
            "license": {
                "identifier": "info:eu-repo/semantics/openAccess"
            }
        } in self.metax_dict['research_dataset']['access_rights']

    # TODO: current test file only has one description
    def testDescription(self):
        assert {"default": u"Abstract: X-Ray synchrotron diffraction data for the self-complementary dCrGdCrGdCrG chimeric hexanucleotide, crystallized in the presence of barium cations in the form of a left-handed Z-type duplex. The diffraction images were collected to the resolution of 1.09 \xc5 at the BESSY beamline 14.2 in Berlin at 100K using a MAR225 detector. The data was recorded in two passes: subset 1 (low, 200 images to resolution of 1.36 \xc5) and subset 2 (high, 180 images to resolution of 1.09 \xc5) with crystal-to-detector distances: (low) 160mm; (high) 70mm. The direct beam position (x=1531px, y=1535px), oscillation angle (1\xb0) and X-ray wavelength (0.8266 \xc5) were the same for both passes. "} in self.metax_dict[
            'research_dataset']['description']

    # TODO: current test file doesn't have location
    def testLocation(self):
        pass
