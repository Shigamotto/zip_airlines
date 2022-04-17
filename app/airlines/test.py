from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase

from .exceptions import TooMuchAirplanes
from .models import Airplane


class TestCreateApi(APITestCase):

    def test_create(self):
        response = self.client.post(
            reverse('airlines:create'), {
                'id': 1,
                'passengers_count': 1
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                'available_fly_minutes': '100000.000',
                'fuel_consumption': '0.002',
                'id': 1,
                'passengers_count': 1,
                'tank_capacity': '200.000'
            }
        )

    def test_create_with_validation_error_unique(self):
        Airplane.objects.create(airplane_id=1, passengers_count=0)
        response = self.client.post(
            reverse('airlines:create'), {
                'id': 1,
                'passengers_count': 1
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {'id': ['This field must be unique.']}
        )

    @mock.patch('airlines.models.TOTAL_AVAILABLE_AIRPLANES', 0)
    def test_create_with_validation_error_max_planes_allowed(self):
        response = self.client.post(
            reverse('airlines:create'), {
                'id': 1,
                'passengers_count': 1
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            ['Max 0 planes allowed.']
        )


class TestListApi(APITestCase):

    @classmethod
    def setUpTestData(cls):
        Airplane.objects.bulk_create([
            Airplane(airplane_id=1, passengers_count=1),
            Airplane(airplane_id=2, passengers_count=100),
            Airplane(airplane_id=3, passengers_count=0),
        ])

    def test_get(self):
        response = self.client.get(reverse('airlines:list'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 3)
        self.assertEqual(
            data, [{
                'available_fly_minutes': '100000.000',
                'fuel_consumption': '0.002',
                'id': 1,
                'passengers_count': 1,
                'tank_capacity': '200.000'
            }, {
                'available_fly_minutes': '530.140',
                'fuel_consumption': '0.755',
                'id': 2,
                'passengers_count': 100,
                'tank_capacity': '400.000'
            }, {
                'available_fly_minutes': '682.679',
                'fuel_consumption': '0.879',
                'id': 3,
                'passengers_count': 0,
                'tank_capacity': '600.000'
            }]
        )


class TestDetailApi(APITestCase):

    @classmethod
    def setUpTestData(cls):
        Airplane.objects.bulk_create([
            Airplane(airplane_id=10, passengers_count=1),
        ])

    def test_get(self):
        response = self.client.get(reverse('airlines:detail', args=['10']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'available_fly_minutes': '1084.559',
                'fuel_consumption': '1.844',
                'id': 10,
                'passengers_count': 1,
                'tank_capacity': '2000.000'
            }
        )

    def test_get_not_exists(self):
        response = self.client.get(reverse('airlines:detail', args=['1']))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'Not found.'})

    def test_put(self):
        airplane = Airplane.objects.get(airplane_id='10')
        response = self.client.put(
            reverse('airlines:detail', args=['10']), {
                'id': 20,
                'passengers_count': '100'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'available_fly_minutes': '1540.484',
                'fuel_consumption': '2.597',
                'id': 20,
                'passengers_count': 100,
                'tank_capacity': '4000.000'
            }
        )
        self.assertEqual(Airplane.objects.count(), 1)

        airplane.refresh_from_db()
        self.assertEqual(airplane.airplane_id, 20)
        self.assertEqual(airplane.passengers_count, 100)

    def test_patch(self):
        response = self.client.patch(
            reverse('airlines:detail', args=['10']), {
                'passengers_count': '100'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'available_fly_minutes': '979.399',
                'fuel_consumption': '2.042',
                'id': 10,
                'passengers_count': 100,
                'tank_capacity': '2000.000'
            }
        )
        self.assertEqual(Airplane.objects.get(airplane_id='10').passengers_count, 100)


class TestModel(TestCase):

    def test(self):
        Airplane.objects.create(airplane_id=1, passengers_count=1)
        self.assertEqual(Airplane.objects.count(), 1)

        obj = Airplane.objects.get(airplane_id=1)
        self.assertEqual(obj.airplane_id, 1)
        self.assertEqual(obj.passengers_count, 1)
        self.assertEqual(obj.tank_capacity, Decimal('200'))
        self.assertEqual(obj.fuel_consumption, Decimal('0.002'))

    @mock.patch('airlines.models.TOTAL_AVAILABLE_AIRPLANES', 0)
    def test_create_limit(self):
        with self.assertRaisesMessage(
            TooMuchAirplanes, 'Max 0 planes allowed.'
        ):
            Airplane.objects.create(airplane_id=1, passengers_count=1)
        self.assertEqual(Airplane.objects.count(), 0)

    @mock.patch('airlines.models.TOTAL_AVAILABLE_AIRPLANES', 0)
    def test_update_limit_pass(self):
        Airplane.objects.bulk_create([
            Airplane(airplane_id=1, passengers_count=1)
        ])
        airplane = Airplane.objects.get(airplane_id=1)
        self.assertEqual(airplane.passengers_count, 1)
        airplane.passengers_count = 100
        airplane.save()

        airplane.refresh_from_db()
        self.assertEqual(airplane.passengers_count, 100)
