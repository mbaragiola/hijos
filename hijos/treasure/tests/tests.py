from datetime import date
from decimal import Decimal

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from hijos.treasure import models
from hijos.users import models as users


class LodgeAccountTestCase(TestCase):
    """
    """
    fixtures = [
        'hijos/treasure/tests/fixtures/users.json',
        'hijos/treasure/tests/fixtures/treasure.json'
    ]

    def setUp(self):
        self.user1 = users.User.objects.get(username='user1')
        self.user2 = users.User.objects.get(username='user2')
        self.lodge = users.Lodge.objects.get(name='Example')
        self.affiliation = users.Affiliation.objects.get(
            lodge=self.lodge,
            user=self.user1
        )
        self.lodge_account = models.LodgeAccount.objects.get(
            handler=self.affiliation
        )
        self.url_login = reverse('account_login')

    def test_str(self):
        self.assertEqual(
            str(self.lodge_account),
            "One, User (3) @ Example"
        )

    def test_create(self):
        url_create = reverse('treasure:lodgeaccount-create')
        data = {
            'handler': 2,
            'description': 'Sup',
            'balance': Decimal('100.00'),
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        lodge_account = models.LodgeAccount.objects.get(
            handler__lodge=self.lodge,
            handler__user=self.user2
        )
        url_detail = reverse(
            'treasure:lodgeaccount-detail', args=[lodge_account.pk]
        )
        self.assertRedirects(response, url_detail)
        self.assertEqual(lodge_account.description, 'Sup')
        self.assertEqual(lodge_account.balance, Decimal('0.00'))
        self.assertTrue(lodge_account.is_active)

    def test_read(self):
        url_list = reverse('treasure:lodgeaccount-list', args=[self.lodge.pk])
        url_detail = reverse(
            'treasure:lodgeaccount-detail', args=[self.lodge_account.pk]
        )

        self.client.logout()
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_list
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_detail
        )

        self.client.force_login(user=self.user1)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccount_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccount_detail.html'
        )

        self.client.force_login(user=self.user2)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccount_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccount_detail.html'
        )


class PeriodTestCase(TestCase):
    """
    """
    fixtures = [
        'hijos/treasure/tests/fixtures/users.json',
        'hijos/treasure/tests/fixtures/treasure.json'
    ]

    def setUp(self):
        self.user1 = users.User.objects.get(username='user1')
        self.user2 = users.User.objects.get(username='user2')
        self.user3 = users.User.objects.get(username='user3')
        self.user4 = users.User.objects.get(username='user4')
        self.lodge = users.Lodge.objects.get(name='Example')
        self.period = models.Period.objects.get(lodge=self.lodge)
        self.url_login = reverse('account_login')
        self.today = date.today()

    def test_str(self):
        self.assertEqual(
            str(self.period),
            "2018-01-01:2018-03-31"
        )

    def test_create_with_email(self):
        url_create = reverse('treasure:period-create')
        data = {
            'lodge': self.lodge.pk,
            'begin': '2018-04-01',
            'end': '2018-04-30',
            'price_multiplier': 1,
            'send_email': True,
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.Invoice.objects.filter(
                period__begin=date(year=2018, month=4, day=1),
                period__end=date(year=2018, month=4, day=30),
                affiliation__user=self.user1,
                amount=Decimal('100.00'),
                send_email=True,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user1,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

        self.assertFalse(
            models.Invoice.objects.filter(
                period__begin=date(year=2018, month=4, day=1),
                period__end=date(year=2018, month=4, day=30),
                affiliation__user=self.user2,
                amount=Decimal('100.00'),
                send_email=True,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user2,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

        self.assertFalse(
            models.Invoice.objects.filter(
                period__begin=date(year=2018, month=4, day=1),
                period__end=date(year=2018, month=4, day=30),
                affiliation__user=self.user3,
                amount=Decimal('100.00'),
                send_email=True,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user3,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-50.00'),
                balance=Decimal('-200.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        period = models.Period.objects.get(
            lodge=self.lodge,
            begin=date(year=2018, month=4, day=1),
            end=date(year=2018, month=4, day=30)
        )
        url_detail = reverse('treasure:period-detail', args=[period.pk])
        self.assertRedirects(response, url_detail)
        self.assertEqual(period.price_multiplier, 1)
        self.assertTrue(period.send_email)
        self.assertTrue(period.is_active)

        self.assertTrue(
            models.Invoice.objects.filter(
                period=period,
                affiliation__user=self.user1,
                amount=Decimal('100.00'),
                send_email=True,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user1,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )
        msg = mail.outbox[0]
        self.assertEqual(
            msg.recipients(),
            ['user1@user.com']
        )
        self.assertEqual(
            msg.subject,
            'New invoice'
        )
        self.assertEqual(
            msg.body,
            "Dear M.·.W.·.B.·. User One:"
            "\n\t"
            "A new invoice has been issued to you for the period "
            "2018-04-01:2018-04-30 of an amount $ 100.00."
            "\n\t"
            "Your current account balance with Example is of $ -400.00"
            "\n\n"
            "Your last 10 movements are:"
            "\n\nDate\tType\t\tAmount\t\tBalance\n\n" +
            str(self.today) + "\tInvoice\t\t-100.00\t\t-400.00\n"
            "2018-05-18\tInvoice\t\t-300.00\t\t-300.00\n"
        )

        self.assertTrue(
            models.Invoice.objects.filter(
                period=period,
                affiliation__user=self.user2,
                amount=Decimal('100.00'),
                send_email=True,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user2,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )
        msg = mail.outbox[2]
        self.assertEqual(
            msg.recipients(),
            ['user2@user.com']
        )
        self.assertEqual(
            msg.subject,
            'New invoice'
        )
        self.assertEqual(
            msg.body,
            "Dear W.·.B.·. User Two:"
            "\n\t"
            "A new invoice has been issued to you for the period "
            "2018-04-01:2018-04-30 of an amount $ 100.00."
            "\n\t"
            "Your current account balance with Example is of $ -400.00"
            "\n\n"
            "Your last 10 movements are:"
            "\n\nDate\tType\t\tAmount\t\tBalance\n\n" +
            str(self.today) + "\tInvoice\t\t-100.00\t\t-400.00\n"
            "2018-05-18\tInvoice\t\t-300.00\t\t-300.00\n"
            "2018-05-18\tDeposit\t\t200.00\t\t0.00\n"
            "2018-05-17\tCharge\t\t-200.00\t\t-200.00\n"
        )

        self.assertTrue(
            models.Invoice.objects.filter(
                period=period,
                affiliation__user=self.user3,
                amount=Decimal('50.00'),
                send_email=True,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user3,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-50.00'),
                balance=Decimal('-200.00')
            ).exists()
        )
        msg = mail.outbox[1]
        self.assertEqual(
            msg.recipients(),
            ['user3@user.com']
        )
        self.assertEqual(
            msg.subject,
            'New invoice'
        )
        self.assertEqual(
            msg.body,
            "Dear P.·.M.·. User Three:"
            "\n\t"
            "A new invoice has been issued to you for the period "
            "2018-04-01:2018-04-30 of an amount $ 50.00."
            "\n\t"
            "Your current account balance with Example is of $ -200.00"
            "\n\n"
            "Your last 10 movements are:"
            "\n\nDate\tType\t\tAmount\t\tBalance\n\n" +
            str(self.today) + "\tInvoice\t\t-50.00\t\t-200.00\n"
            "2018-05-18\tInvoice\t\t-150.00\t\t-150.00\n"
        )

    def test_create_without_email(self):
        url_create = reverse('treasure:period-create')
        data = {
            'lodge': self.lodge.pk,
            'begin': '2018-04-01',
            'end': '2018-04-30',
            'price_multiplier': 1,
            'send_email': False,
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.Invoice.objects.filter(
                period__begin=date(year=2018, month=4, day=1),
                period__end=date(year=2018, month=4, day=30),
                affiliation__user=self.user1,
                amount=Decimal('100.00'),
                send_email=True,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user1,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

        self.assertFalse(
            models.Invoice.objects.filter(
                period__begin=date(year=2018, month=4, day=1),
                period__end=date(year=2018, month=4, day=30),
                affiliation__user=self.user2,
                amount=Decimal('100.00'),
                send_email=True,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user2,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

        self.assertFalse(
            models.Invoice.objects.filter(
                period__begin=date(year=2018, month=4, day=1),
                period__end=date(year=2018, month=4, day=30),
                affiliation__user=self.user3,
                amount=Decimal('100.00'),
                send_email=True,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user3,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-50.00'),
                balance=Decimal('-200.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        period = models.Period.objects.get(
            lodge=self.lodge,
            begin=date(year=2018, month=4, day=1),
            end=date(year=2018, month=4, day=30)
        )
        url_detail = reverse('treasure:period-detail', args=[period.pk])
        self.assertRedirects(response, url_detail)
        self.assertEqual(period.price_multiplier, 1)
        self.assertFalse(period.send_email)
        self.assertTrue(period.is_active)
        self.assertFalse(mail.outbox)

        self.assertTrue(
            models.Invoice.objects.filter(
                period=period,
                affiliation__user=self.user1,
                amount=Decimal('100.00'),
                send_email=False,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user1,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

        self.assertTrue(
            models.Invoice.objects.filter(
                period=period,
                affiliation__user=self.user2,
                amount=Decimal('100.00'),
                send_email=False,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user2,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

        self.assertTrue(
            models.Invoice.objects.filter(
                period=period,
                affiliation__user=self.user3,
                amount=Decimal('50.00'),
                send_email=False,
                created_by=self.user1,
                last_modified_by=self.user1
            ).exists()
        )
        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation__lodge=self.lodge,
                account__affiliation__user=self.user3,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-50.00'),
                balance=Decimal('-200.00')
            ).exists()
        )

    def test_read(self):
        url_list = reverse('treasure:period-list', args=[self.lodge.pk])
        url_detail = reverse('treasure:period-detail', args=[self.period.pk])

        self.client.logout()
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_list
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_detail
        )

        self.client.force_login(user=self.user1)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/period_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/period_detail.html'
        )

        self.client.force_login(user=self.user2)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/period_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/period_detail.html'
        )


class InvoiceTestCase(TestCase):
    """
    """
    fixtures = [
        'hijos/treasure/tests/fixtures/users.json',
        'hijos/treasure/tests/fixtures/treasure.json'
    ]

    def setUp(self):
        self.user1 = users.User.objects.get(username='user1')
        self.user2 = users.User.objects.get(username='user2')
        self.lodge = users.Lodge.objects.get(name='Example')
        self.affiliation = users.Affiliation.objects.get(
            lodge=self.lodge,
            user=self.user1
        )
        self.period = models.Period.objects.get(lodge=self.lodge)
        self.invoice = models.Invoice.objects.get(
            period=self.period,
            affiliation=self.affiliation
        )
        self.url_login = reverse('account_login')
        self.today = date.today()

    def test_str(self):
        self.assertEqual(
            str(self.invoice),
            "2018-01-01:2018-03-31 $ 300.00 (#1)"
        )

    def test_create_with_email(self):
        url_create = reverse('treasure:invoice-create')
        data = {
            'period': self.period.pk,
            'affiliation': self.affiliation.pk,
            'amount': Decimal('100.00'),
            'send_email': True,
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        invoice = models.Invoice.objects.get(
            period=self.period,
            affiliation=self.affiliation,
            amount=Decimal('100.00')
        )
        url_detail = reverse('treasure:invoice-detail', args=[invoice.pk])
        self.assertRedirects(response, url_detail)
        self.assertTrue(invoice.send_email)
        self.assertTrue(invoice.is_active)

        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )
        msg = mail.outbox[0]
        self.assertEqual(
            msg.recipients(),
            ['user1@user.com']
        )
        self.assertEqual(
            msg.subject,
            'New invoice'
        )
        self.assertEqual(
            msg.body,
            "Dear M.·.W.·.B.·. User One:"
            "\n\t"
            "A new invoice has been issued to you for the period "
            "2018-01-01:2018-03-31 of an amount $ 100.00."
            "\n\t"
            "Your current account balance with Example is of $ -400.00"
            "\n\n"
            "Your last 10 movements are:"
            "\n\nDate\tType\t\tAmount\t\tBalance\n\n" +
            str(self.today) + "\tInvoice\t\t-100.00\t\t-400.00\n"
            "2018-05-18\tInvoice\t\t-300.00\t\t-300.00\n"
        )

    def test_create_without_email(self):
        url_create = reverse('treasure:invoice-create')
        data = {
            'period': self.period.pk,
            'affiliation': self.affiliation.pk,
            'amount': Decimal('100.00'),
            'send_email': False,
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        invoice = models.Invoice.objects.get(
            period=self.period,
            affiliation=self.affiliation,
            amount=Decimal('100.00')
        )
        url_detail = reverse('treasure:invoice-detail', args=[invoice.pk])
        self.assertRedirects(response, url_detail)
        self.assertFalse(invoice.send_email)
        self.assertTrue(invoice.is_active)
        self.assertFalse(mail.outbox)

        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_INVOICE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

    def test_read(self):
        url_list = reverse('treasure:invoice-list', args=[self.lodge.pk])
        url_detail = reverse('treasure:invoice-detail', args=[self.invoice.pk])

        self.client.logout()
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_list
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_detail
        )

        self.client.force_login(user=self.user1)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/invoice_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/invoice_detail.html'
        )

        self.client.force_login(user=self.user2)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/invoice_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/invoice_detail.html'
        )


class ChargeTestCase(TestCase):
    """
    """
    fixtures = [
        'hijos/treasure/tests/fixtures/users.json',
        'hijos/treasure/tests/fixtures/treasure.json'
    ]

    def setUp(self):
        self.user1 = users.User.objects.get(username='user1')
        self.user2 = users.User.objects.get(username='user2')
        self.lodge = users.Lodge.objects.get(name='Example')
        self.affiliation = users.Affiliation.objects.get(
            lodge=self.lodge,
            user=self.user1
        )
        self.charge = models.Charge.objects.get(
            debtor__lodge=self.lodge,
            debtor__user=self.user2,
            amount=Decimal('200.00')
        )
        self.url_login = reverse('account_login')
        self.today = date.today()

    def test_str(self):
        self.assertEqual(
            str(self.charge),
            "Two, User (3) @ Example - $ 200.00 (#1)"
        )

    def test_create_with_email(self):
        url_create = reverse('treasure:charge-create')
        data = {
            'debtor': self.affiliation.pk,
            'amount': Decimal('100.00'),
            'description': 'Sup',
            'charge_type': models.CHARGE_RAISE,
            'send_email': True,
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_CHARGE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        charge = models.Charge.objects.get(
            debtor=self.affiliation,
            amount=Decimal('100.00'),
            charge_type=models.CHARGE_RAISE
        )
        url_detail = reverse('treasure:charge-detail', args=[charge.pk])
        self.assertRedirects(response, url_detail)
        self.assertEqual(charge.description, 'Sup')
        self.assertTrue(charge.send_email)
        self.assertTrue(charge.is_active)

        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_CHARGE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )
        msg = mail.outbox[0]
        self.assertEqual(
            msg.recipients(),
            ['user1@user.com']
        )
        self.assertEqual(
            msg.subject,
            'New charge'
        )
        self.assertEqual(
            msg.body,
            "Dear M.·.W.·.B.·. User One:"
            "\n\t"
            "A new charge has been issued to you of an amount $ 100.00."
            "\n\t"
            "Your current account balance with Example is of $ -400.00"
            "\n\n"
            "Your last 10 movements are:"
            "\n\nDate\tType\t\tAmount\t\tBalance\n\n" +
            str(self.today) + "\tCharge\t\t-100.00\t\t-400.00\n"
            "2018-05-18\tInvoice\t\t-300.00\t\t-300.00\n"
        )

    def test_create_without_email(self):
        url_create = reverse('treasure:charge-create')
        data = {
            'debtor': self.affiliation.pk,
            'amount': Decimal('100.00'),
            'charge_type': models.CHARGE_PASS,
            'send_email': False,
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_CHARGE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        charge = models.Charge.objects.get(
            debtor=self.affiliation,
            amount=Decimal('100.00'),
            charge_type=models.CHARGE_PASS
        )
        url_detail = reverse('treasure:charge-detail', args=[charge.pk])
        self.assertRedirects(response, url_detail)
        self.assertEqual(charge.description, "")
        self.assertFalse(charge.send_email)
        self.assertTrue(charge.is_active)
        self.assertFalse(mail.outbox)

        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_CHARGE,
                amount=Decimal('-100.00'),
                balance=Decimal('-400.00')
            ).exists()
        )

    def test_read(self):
        url_list = reverse('treasure:charge-list', args=[self.lodge.pk])
        url_detail = reverse('treasure:charge-detail', args=[self.charge.pk])

        self.client.logout()
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_list
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_detail
        )

        self.client.force_login(user=self.user1)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/charge_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/charge_detail.html'
        )

        self.client.force_login(user=self.user2)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/charge_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/charge_detail.html'
        )


class DepositTestCase(TestCase):
    """
    """
    fixtures = [
        'hijos/treasure/tests/fixtures/users.json',
        'hijos/treasure/tests/fixtures/treasure.json'
    ]

    def setUp(self):
        self.user1 = users.User.objects.get(username='user1')
        self.user2 = users.User.objects.get(username='user2')
        self.lodge = users.Lodge.objects.get(name='Example')
        self.affiliation = users.Affiliation.objects.get(
            lodge=self.lodge,
            user=self.user1
        )
        self.lodge_account = models.LodgeAccount.objects.get(
            handler=self.affiliation
        )
        self.deposit = models.Deposit.objects.get(
            payer__lodge=self.lodge,
            payer__user=self.user2,
            amount=Decimal('200.00')
        )
        self.url_login = reverse('account_login')
        self.today = date.today()

    def test_str(self):
        self.assertEqual(
            str(self.deposit),
            "Two, User (3) @ Example->One, User (3) @ Example + $ 200.00 (#1)"
        )

    def test_create_with_email(self):
        url_create = reverse('treasure:deposit-create')
        data = {
            'payer': self.affiliation.pk,
            'lodge_account': self.lodge_account.pk,
            'amount': Decimal('100.00'),
            'description': 'Sup',
            'send_email': True,
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_DEPOSIT,
                amount=Decimal('100.00'),
                balance=Decimal('-200.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        deposit = models.Deposit.objects.get(
            payer=self.affiliation,
            amount=Decimal('100.00')
        )
        url_detail = reverse('treasure:deposit-detail', args=[deposit.pk])
        self.assertRedirects(response, url_detail)
        self.assertEqual(deposit.description, 'Sup')
        self.assertTrue(deposit.send_email)
        self.assertTrue(deposit.is_active)

        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_DEPOSIT,
                amount=Decimal('100.00'),
                balance=Decimal('-200.00')
            ).exists()
        )
        msg = mail.outbox[0]
        self.assertEqual(
            msg.recipients(),
            ['user1@user.com']
        )
        self.assertEqual(
            msg.subject,
            'New deposit'
        )
        self.assertEqual(
            msg.body,
            "Dear M.·.W.·.B.·. User One:"
            "\n\t"
            "A new deposit on your behalf has been made of an amount $ 100.00."
            "\n\t"
            "Your current account balance with Example is of $ -200.00"
            "\n\n"
            "Your last 10 movements are:"
            "\n\nDate\tType\t\tAmount\t\tBalance\n\n" +
            str(self.today) + "\tDeposit\t\t100.00\t\t-200.00\n"
            "2018-05-18\tInvoice\t\t-300.00\t\t-300.00\n"
        )

    def test_create_without_email(self):
        url_create = reverse('treasure:deposit-create')
        data = {
            'payer': self.affiliation.pk,
            'lodge_account': self.lodge_account.pk,
            'amount': Decimal('100.00'),
            'send_email': False,
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_DEPOSIT,
                amount=Decimal('100.00'),
                balance=Decimal('-200.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        deposit = models.Deposit.objects.get(
            payer=self.affiliation,
            amount=Decimal('100.00')
        )
        url_detail = reverse('treasure:deposit-detail', args=[deposit.pk])
        self.assertRedirects(response, url_detail)
        self.assertEqual(deposit.description, "")
        self.assertFalse(deposit.send_email)
        self.assertTrue(deposit.is_active)
        self.assertFalse(mail.outbox)

        self.assertTrue(
            models.AccountMovement.objects.filter(
                account__affiliation=self.affiliation,
                account_movement_type=models.ACCOUNTMOVEMENT_DEPOSIT,
                amount=Decimal('100.00'),
                balance=Decimal('-200.00')
            ).exists()
        )

    def test_read(self):
        url_list = reverse('treasure:deposit-list', args=[self.lodge.pk])
        url_detail = reverse('treasure:deposit-detail', args=[self.deposit.pk])

        self.client.logout()
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_list
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_detail
        )

        self.client.force_login(user=self.user1)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/deposit_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/deposit_detail.html'
        )

        self.client.force_login(user=self.user2)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/deposit_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/deposit_detail.html'
        )


class LodgeAccountIngressTestCase(TestCase):
    """
    """
    fixtures = [
        'hijos/treasure/tests/fixtures/users.json',
        'hijos/treasure/tests/fixtures/treasure.json'
    ]

    def setUp(self):
        self.user1 = users.User.objects.get(username='user1')
        self.user2 = users.User.objects.get(username='user2')
        self.user3 = users.User.objects.get(username='user3')
        self.lodge = users.Lodge.objects.get(name='Example')
        self.lodge_account = models.LodgeAccount.objects.get(
            handler__lodge=self.lodge,
            handler__user=self.user1
        )
        self.ingress = models.LodgeAccountIngress.objects.get(
            lodge_account__handler__lodge=self.lodge,
            lodge_account__handler__user=self.user3,
            amount=Decimal('400.00')
        )
        self.url_login = reverse('account_login')
        self.today = date.today()

    def test_str(self):
        self.assertEqual(
            str(self.ingress),
            "Three, User (3) @ Example + $ 400.00 (#1)"
        )

    def test_create(self):
        url_create = reverse('treasure:lodgeaccountingress-create')
        data = {
            'lodge_account': self.lodge_account.pk,
            'amount': Decimal('100.00'),
            'description': 'Sup',
            'ingress_type': models.INGRESS_TYPE_DONATION,
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.LodgeAccountMovement.objects.filter(
                lodge_account=self.lodge_account,
                lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_INGRESS,
                amount=Decimal('100.00'),
                balance=Decimal('300.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        ingress = models.LodgeAccountIngress.objects.get(
            lodge_account=self.lodge_account,
            ingress_type=models.INGRESS_TYPE_DONATION,
            amount=Decimal('100.00')
        )
        url_detail = reverse(
            'treasure:lodgeaccountingress-detail', args=[ingress.pk]
        )
        self.assertRedirects(response, url_detail)
        self.assertEqual(ingress.description, "Sup")
        self.assertTrue(ingress.is_active)

        self.assertTrue(
            models.LodgeAccountMovement.objects.filter(
                lodge_account=self.lodge_account,
                lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_INGRESS,
                amount=Decimal('100.00'),
                balance=Decimal('300.00')
            ).exists()
        )

    def test_read(self):
        url_list = reverse(
            'treasure:lodgeaccountingress-list', args=[self.lodge.pk]
        )
        url_detail = reverse(
            'treasure:lodgeaccountingress-detail', args=[self.ingress.pk]
        )

        self.client.logout()
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_list
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_detail
        )

        self.client.force_login(user=self.user1)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccountingress_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccountingress_detail.html'
        )

        self.client.force_login(user=self.user2)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccountingress_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccountingress_detail.html'
        )


class LodgeAccountEgressTestCase(TestCase):
    """
    """
    fixtures = [
        'hijos/treasure/tests/fixtures/users.json',
        'hijos/treasure/tests/fixtures/treasure.json'
    ]

    def setUp(self):
        self.user1 = users.User.objects.get(username='user1')
        self.user2 = users.User.objects.get(username='user2')
        self.user3 = users.User.objects.get(username='user3')
        self.lodge = users.Lodge.objects.get(name='Example')
        self.lodge_account = models.LodgeAccount.objects.get(
            handler__lodge=self.lodge,
            handler__user=self.user1
        )
        self.egress = models.LodgeAccountEgress.objects.get(
            lodge_account__handler__lodge=self.lodge,
            lodge_account__handler__user=self.user3,
            amount=Decimal('200.00')
        )
        self.url_login = reverse('account_login')
        self.today = date.today()

    def test_str(self):
        self.assertEqual(
            str(self.egress),
            "Three, User (3) @ Example - $ 200.00 (#1)"
        )

    def test_create(self):
        url_create = reverse('treasure:lodgeaccountegress-create')
        data = {
            'lodge_account': self.lodge_account.pk,
            'amount': Decimal('200.00'),
            'description': 'Sup',
            'egress_type': models.EGRESS_TYPE_DONATION,
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.LodgeAccountMovement.objects.filter(
                lodge_account=self.lodge_account,
                lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_EGRESS,
                amount=Decimal('-200.00'),
                balance=Decimal('0.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        egress = models.LodgeAccountEgress.objects.get(
            lodge_account=self.lodge_account,
            egress_type=models.EGRESS_TYPE_DONATION,
            amount=Decimal('200.00')
        )
        url_detail = reverse(
            'treasure:lodgeaccountegress-detail', args=[egress.pk]
        )
        self.assertRedirects(response, url_detail)
        self.assertEqual(egress.description, "Sup")
        self.assertTrue(egress.is_active)

        self.assertTrue(
            models.LodgeAccountMovement.objects.filter(
                lodge_account=self.lodge_account,
                lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_EGRESS,
                amount=Decimal('-200.00'),
                balance=Decimal('0.00')
            ).exists()
        )

    def test_read(self):
        url_list = reverse(
            'treasure:lodgeaccountegress-list', args=[self.lodge.pk]
        )
        url_detail = reverse(
            'treasure:lodgeaccountegress-detail', args=[self.egress.pk]
        )

        self.client.logout()
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_list
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_detail
        )

        self.client.force_login(user=self.user1)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccountegress_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccountegress_detail.html'
        )

        self.client.force_login(user=self.user2)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccountegress_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccountegress_detail.html'
        )


class LodgeAccountTransferTestCase(TestCase):
    """
    """
    fixtures = [
        'hijos/treasure/tests/fixtures/users.json',
        'hijos/treasure/tests/fixtures/treasure.json'
    ]

    def setUp(self):
        self.user1 = users.User.objects.get(username='user1')
        self.user2 = users.User.objects.get(username='user2')
        self.user3 = users.User.objects.get(username='user3')
        self.lodge = users.Lodge.objects.get(name='Example')
        self.lodge_account_user1 = models.LodgeAccount.objects.get(
            handler__lodge=self.lodge,
            handler__user=self.user1,
        )
        self.lodge_account_user3 = models.LodgeAccount.objects.get(
            handler__lodge=self.lodge,
            handler__user=self.user3,
        )
        self.transfer = models.LodgeAccountTransfer.objects.get(
            lodge_account_from=self.lodge_account_user3,
            lodge_account_to=self.lodge_account_user1,
            amount=Decimal('200.00')
        )
        self.url_login = reverse('account_login')
        self.today = date.today()

    def test_str(self):
        self.assertEqual(
            str(self.transfer),
            "(#1) Three, User (3) @ Example -> $ 200.00 -> "
            "One, User (3) @ Example"
        )

    def test_create(self):
        url_create = reverse('treasure:lodgeaccounttransfer-create')
        data = {
            'lodge_account_from': self.lodge_account_user1.pk,
            'lodge_account_to': self.lodge_account_user3.pk,
            'amount': Decimal('100.00'),
            'description': 'Sup',
            'is_active': False
        }

        self.client.logout()
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_create
        )

        self.assertFalse(
            models.LodgeAccountMovement.objects.filter(
                lodge_account=self.lodge_account_user1,
                lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_TRANSFER,
                amount=Decimal('-100.00'),
                balance=Decimal('100.00')
            ).exists()
        )
        self.assertFalse(
            models.LodgeAccountMovement.objects.filter(
                lodge_account=self.lodge_account_user3,
                lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_TRANSFER,
                amount=Decimal('100.00'),
                balance=Decimal('100.00')
            ).exists()
        )

        self.client.force_login(user=self.user1)
        response = self.client.post(url_create, data, follow=True)
        self.assertEqual(response.status_code, 200)
        transfer = models.LodgeAccountTransfer.objects.get(
            lodge_account_from=self.lodge_account_user1,
            lodge_account_to=self.lodge_account_user3,
            amount=Decimal('100.00')
        )
        url_detail = reverse(
            'treasure:lodgeaccounttransfer-detail', args=[transfer.pk]
        )
        self.assertRedirects(response, url_detail)
        self.assertEqual(transfer.description, "Sup")
        self.assertTrue(transfer.is_active)

        self.assertTrue(
            models.LodgeAccountMovement.objects.filter(
                lodge_account=self.lodge_account_user1,
                lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_TRANSFER,
                amount=Decimal('-100.00'),
                balance=Decimal('100.00')
            ).exists()
        )
        self.assertTrue(
            models.LodgeAccountMovement.objects.filter(
                lodge_account=self.lodge_account_user3,
                lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_TRANSFER,
                amount=Decimal('100.00'),
                balance=Decimal('100.00')
            ).exists()
        )

    def test_read(self):
        url_list = reverse(
            'treasure:lodgeaccounttransfer-list', args=[self.lodge.pk]
        )
        url_detail = reverse(
            'treasure:lodgeaccounttransfer-detail', args=[self.transfer.pk]
        )

        self.client.logout()
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_list
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            self.url_login + '?next=' + url_detail
        )

        self.client.force_login(user=self.user1)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccounttransfer_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccounttransfer_detail.html'
        )

        self.client.force_login(user=self.user2)
        response = self.client.get(url_list, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccounttransfer_list.html'
        )
        response = self.client.get(url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'treasure/lodgeaccounttransfer_detail.html'
        )
