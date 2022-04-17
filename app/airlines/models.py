import math
from decimal import Decimal

from airlines.exceptions import TooMuchAirplanes

from django.db import models


CAPACITY_CONSTANT = Decimal('200')
FUEL_CONSUMPTION_BASE = Decimal('0.8')
FUEL_CONSUMPTION_PASSENGER_INCREASE = Decimal('0.002')
TOTAL_AVAILABLE_AIRPLANES = 10


class Airplane(models.Model):

    airplane_id = models.IntegerField('AirplaneID', unique=True, null=True)
    passengers_count = models.IntegerField('Current passenger load', null=True)

    @property
    def tank_capacity(self) -> Decimal:
        """
        :return: Full fuel tank capacity
        """
        tank_capacity = self.airplane_id * CAPACITY_CONSTANT
        return tank_capacity

    @property
    def fuel_consumption(self) -> Decimal:
        """
        :return: Value of fuel consumption per minute.
                 Depends on Airplain.ID and Airplane.passengers_count
        """
        fuel_consumption = FUEL_CONSUMPTION_BASE * Decimal(
            math.log(self.airplane_id)
        )
        fuel_consumption += FUEL_CONSUMPTION_PASSENGER_INCREASE * self.passengers_count
        return fuel_consumption

    def save(self, **kwargs):
        if self.pk:
            # Check if we EDIT! instance
            return super().save(**kwargs)
        if self.__class__.objects.count() < TOTAL_AVAILABLE_AIRPLANES:
            # Check if total count lower than available
            return super().save(**kwargs)

        raise TooMuchAirplanes('Max %s planes allowed.' % TOTAL_AVAILABLE_AIRPLANES)
