from decimal import Decimal

from airlines.exceptions import TooMuchAirplanes
from airlines.models import Airplane

from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class AirplaneSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(
        source='airplane_id',
        validators=[
            UniqueValidator(queryset=Airplane.objects.all())
        ]
    )
    passengers_count = serializers.IntegerField()
    tank_capacity = serializers.DecimalField(max_digits=10, decimal_places=3, read_only=True)
    fuel_consumption = serializers.DecimalField(max_digits=10, decimal_places=3, read_only=True)
    available_fly_minutes = serializers.SerializerMethodField()

    def get_available_fly_minutes(self, obj: Airplane) -> str:
        return str(Decimal(
            obj.tank_capacity / obj.fuel_consumption
        ).quantize(Decimal('1.000')))

    class Meta:
        model = Airplane
        fields = ['id', 'passengers_count', 'tank_capacity', 'fuel_consumption', 'available_fly_minutes']

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except TooMuchAirplanes as e:
            raise serializers.ValidationError(f'{e}')
