from rest_framework import serializers
from .models import Department, User
from django.contrib.auth.hashers import make_password


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "department_id", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    # Use department_id instead of numeric id
    department = serializers.SlugRelatedField(
        slug_field="department_id", 
        queryset=Department.objects.all()
    )

    class Meta:
        model = User
        fields = [
            "id",
            "employee_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
            "department",
        ]
        read_only_fields = ["employee_id"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)
