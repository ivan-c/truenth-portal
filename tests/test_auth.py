"""Unit test module for auth"""
from tests import TestCase, TEST_USER_ID

from portal.extensions import db
from portal.models.auth import Client
from portal.models.role import ROLE 
from portal.models.user import add_authomatic_user, User

class AuthomaticMock(object):
    """Simple container for mocking Authomatic response"""
    pass


class TestAuth(TestCase):
    """Auth API tests"""

    def add_test_client(self):
        """Prep db with a test client for test user"""
        client_id = 'test_client'
        client = Client(client_id=client_id,
                _redirect_uris='http://localhost',
                client_secret='tc_secret', user_id=TEST_USER_ID)
        db.session.add(client)
        db.session.commit()
        self.promote_user(role_name=ROLE.APPLICATION_DEVELOPER)
        return client

    def test_nouser_logout(self):
        """Confirm logout works without a valid user"""
        rv = self.app.get('/logout')
        self.assertEquals(302, rv.status_code)

    def test_local_user_add(self):
        """Add a local user via flask_user forms"""
        data = {'username': 'OneTestUser',
                'password': 'one2Three',
                'retype_password': 'one2Three',
                'email': 'otu@example.com',
               }
        rv = self.app.post('/user/register', data=data)
        self.assertEquals(rv.status_code, 302)
        new_user = User.query.filter_by(username=data['username']).first()
        self.assertTrue(new_user.roles[0].name, ROLE.PATIENT)

    def test_client_add(self):
        """Test adding a client application"""
        origins = "https://test.com https://two.com"
        self.promote_user(role_name=ROLE.APPLICATION_DEVELOPER)
        self.login()
        rv = self.app.post('/client', data=dict(
            application_origins=origins))
        self.assertEquals(302, rv.status_code)

        client = Client.query.filter_by(user_id=TEST_USER_ID).first()
        self.assertEquals(client.application_origins, origins)

    def test_client_bad_add(self):
        """Test adding a bad client application"""
        self.promote_user(role_name=ROLE.APPLICATION_DEVELOPER)
        self.login()
        rv = self.app.post('/client',
                data=dict(application_origins="bad data in"))
        self.assertTrue("Invalid URL" in rv.data)

    def test_client_edit(self):
        """Test editing a client application"""
        client = self.add_test_client()
        self.login()
        rv = self.app.post('/client/{0}'.format(client.client_id),
                data=dict(callback_url='http://tryme.com',
                    application_origins=client.application_origins))
        self.assertEquals(302, rv.status_code)

        client = Client.query.get('test_client')
        self.assertEquals(client.callback_url, 'http://tryme.com')

    def test_unicode_name(self):
        """Test insertion of unicode name via add_authomatic_user"""
        # Bug with unicode characters in a google user's name
        # mock an authomatic class:

        authomatic_user = AuthomaticMock()
        authomatic_user.name = 'Test User'
        authomatic_user.first_name = 'Test'
        authomatic_user.last_name = u'Bugn\xed'
        authomatic_user.birth_date = None
        authomatic_user.gender = u'male'
        authomatic_user.email = 'test@test.org'

        add_authomatic_user(authomatic_user, None)

        user = User.query.filter_by(email='test@test.org').first()
        self.assertEquals(user.last_name, u'Bugn\xed')

    def test_callback_validation(self):
        """Confirm only valid urls can be set"""
        client = self.add_test_client()
        self.login()
        rv = self.app.post('/client/{0}'.format(client.client_id),
                data=dict(callback_url='badprotocol.com',
                    application_origins=client.application_origins))
        self.assertEquals(200, rv.status_code)

        client = Client.query.get('test_client')
        self.assertEquals(client.callback_url, None)
