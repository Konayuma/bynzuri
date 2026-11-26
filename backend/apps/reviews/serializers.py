from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'user_name', 'rating', 'comment', 'staff_reply', 'is_approved', 'created_at']
        read_only_fields = ['id', 'user', 'product', 'staff_reply', 'is_approved', 'created_at']

    def validate_comment(self, value):
        value = value.strip()
        if len(value) < 5 or len(value) > 1000:
            raise serializers.ValidationError('Review must be between 5 and 1000 characters.')
        return value

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5')
        return value
