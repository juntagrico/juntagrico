import datetime

from django.urls import reverse

from . import JuntagricoTestCase
from ..view_decorators import using_change_date


@using_change_date
def get_change_date(request, change_date):
    return change_date


class ManageListTests(JuntagricoTestCase):

    def testSubscription(self):
        self.assertGet(reverse('manage-subscription'))
        # member2 has no access
        self.assertGet(reverse('manage-subscription'), member=self.member2, code=403)

    def testDepotSubscription(self):
        url = reverse('manage-depot-subs', args=[self.depot.pk])
        # anonymous has no access
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302, msg=f'url: {url}')
        # member2 has no access
        self.assertGet(url, member=self.member2, code=404)
        # coordinator has access
        self.assertGet(url, member=self.depot_coordinator)

    def testMember(self):
        response = self.assertGet(reverse('manage-member'))
        # check that member list is correct
        objects = list(response.context['object_list']().order_by('id'))
        self.assertListEqual(objects, [
            self.member, self.member2, self.member3, self.member4, self.member5, self.member6, self.member7,
            self.admin, self.area_admin, self.inactive_member, self.area_admin_modifier, self.area_admin_viewer,
            self.area_admin_contact, self.area_admin_remover, self.area_admin_job_modifier,
            self.area_admin_assignment_modifier, self.depot_coordinator
        ])
        member = objects[0]
        self.assertEqual(member.subscription_current, self.sub)
        # check if member is prefetched correctly
        self.assertEqual(member.subscription_current.depot_name, self.depot.name)
        # member2 has no access
        self.assertGet(reverse('manage-member'), member=self.member2, code=403)

    def testAreaMember(self):
        url = reverse('manage-area-member', args=[self.area.pk])
        # anonymous has no access
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302, msg=f'url: {url}')
        # member has no access
        self.assertGet(url, code=404)
        # member2 has no access
        self.assertGet(url, member=self.member2, code=404)
        # area admins have access
        self.assertGet(url, member=self.area_admin)
        self.assertGet(url, member=self.area_admin_viewer)

    def testAreaMemberRemove(self):
        # incomplete and unpriviledged requests should fail
        self.assertGet(reverse('manage-area-member-remove', args=[self.area.pk]), code=405)
        self.assertPost(reverse('manage-area-member-remove', args=[self.area.pk]), code=400)
        self.assertPost(reverse('manage-area-member-remove', args=[self.area.pk]), {
            'member_id': 1
        }, code=404)
        self.area.refresh_from_db()
        self.assertTrue(self.area.members.filter(id=1).exists())
        # area admin with removal rights can remove
        self.assertPost(reverse('manage-area-member-remove', args=[self.area.pk]), {
            'member_id': 1
        }, member=self.area_admin_remover, code=302)
        self.area.refresh_from_db()
        self.assertFalse(self.area.members.filter(id=1).exists())

    def testMemberCanceledList(self):
        self.assertGet(reverse('manage-member-canceled'))
        self.assertGet(reverse('manage-member-canceled'), member=self.member2, code=403)

    def testAssignmentList(self):
        self.assertGet(reverse('manage-assignments'))
        self.assertGet(reverse('manage-assignments'), member=self.member2, code=403)

    def testChangeDate(self):
        self.assertGet(reverse('changedate-set'), code=404)
        self.assertPost(reverse('changedate-set'), data={'date': '1999-01-01'}, code=302)
        self.assertEqual(get_change_date(self.client), datetime.date(1999, 1, 1))
        self.assertGet(reverse('changedate-unset'), code=302)
