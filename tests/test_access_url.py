"""Unit test module for access URLs"""
from __future__ import unicode_literals  # isort:skip

from flask import url_for

from portal.extensions import db, user_manager
from portal.models.role import ROLE
from tests import TestCase


class TestAccessUrl(TestCase):

    def test_create_access_url(self):
        onetime = self.add_user('one@time.com')
        self.promote_user(user=onetime, role_name=ROLE.WRITE_ONLY.value)

        self.promote_user(role_name=ROLE.ADMIN.value)
        self.login()
        onetime = db.session.merge(onetime)
        response = self.client.get('/api/user/{}/access_url'.format(
            onetime.id))
        assert response.status_code == 200

        # confirm we obtained a valid token
        access_url = response.json['access_url']
        token = access_url.split('/')[-1]
        is_valid, has_expired, id = user_manager.token_manager.verify_token(
            token, 10)
        assert is_valid
        assert not has_expired
        assert id == onetime.id

    def test_use_access_url(self):
        """The current flow forces access to the challenge page"""
        onetime = self.add_user(
            'one@time.com', first_name='first', last_name='last')
        onetime.birthdate = '01-31-1969'  # verify requires DOB
        self.promote_user(user=onetime, role_name=ROLE.WRITE_ONLY.value)
        onetime = db.session.merge(onetime)

        token = user_manager.token_manager.generate_token(onetime.id)
        access_url = url_for(
            'portal.access_via_token', token=token, _external=True)

        response = self.client.get(access_url)
        self.assert_redirects(
            response,
            url_for('portal.challenge_identity', request_path=access_url))

    def test_bad_token(self):
        token = 'TBKSYw7iHndUT3DfaED9tw.DHZMrQ.Wwr8SPM7ylABWf0mQHhGHHwttYk'
        access_url = url_for('portal.access_via_token', token=token)

        response = self.client.get(access_url)
        assert response.status_code == 404
