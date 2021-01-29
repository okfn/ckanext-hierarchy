import nose.tools
from ckan.plugins import toolkit
from ckan import model
from ckan.tests import factories
from ckan.tests import helpers as test_helpers
from ckanext.hierarchy.helpers import get_allowable_parent_groups

eq = nose.tools.assert_equals


class TestHelpers(test_helpers.FunctionalTestBase):
    def setup(self):
        super(TestHelpers, self).setup()
        self.app = self._get_test_app()
        self.org1 = factories.Organization(name='org1')
        self.org2 = factories.Organization(name='org2')
        self.fancy_org1 = factories.Organization(name='fancy_org1', type='fancy-type')
        self.fancy_org2 = factories.Organization(name='fancy_org2', type='fancy-type')

    def test_get_allowable_parent_groups_default_group_type(self):
        eq(
            [org.name for org in get_allowable_parent_groups('org1')],
            [self.org2['name']]
        )
        eq(
            [org.name for org in get_allowable_parent_groups('fancy_org1')],
            [self.fancy_org2['name']]
        )
        eq(
            [org.name for org in get_allowable_parent_groups(None)],
            [self.org1['name'], self.org2['name']]
        )

    @test_helpers.change_config('hierarchy.default_parent_group_type', 'fancy-type')
    def test_get_allowable_parent_groups_custom_group_type(self):
        eq(
            [org.name for org in get_allowable_parent_groups('org1')],
            [self.org2['name']]
        )
        eq(
            [org.name for org in get_allowable_parent_groups('fancy_org1')],
            [self.fancy_org2['name']]
        )
        eq(
            [org.name for org in get_allowable_parent_groups(None)],
            [self.fancy_org1['name'], self.fancy_org2['name']]
        )

    @test_helpers.change_config('hierarchy.user_must_be_in_parent_group', True)
    def test_get_allowable_parent_groups_user_must_be_in_parent_group(self):
        user = factories.User()
        userobj = model.User.get(user['name'])

        with self.app.flask_app.test_request_context():
            toolkit.c.user = user['name']
            toolkit.c.userobj = userobj

            eq(get_allowable_parent_groups('org1'), [])

            member = model.Member(
                group=model.Group.get(self.org2['id']),
                table_id=user['id'], table_name='user', capacity='member')
            model.Session.add(member)
            model.Session.commit()

            eq(
                [org.name for org in get_allowable_parent_groups('org1')],
                [self.org2['name']]
            )
