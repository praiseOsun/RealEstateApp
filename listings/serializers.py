from rest_framework import serializers
from .models import Listing

class ListingSerializer(serializers.ModelSerializer):
    category = serializers.ChoiceField(choices=Listing.CategoryChoices.choices)
    
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['realtor','slug']

    def create(self, validated_data):
        validated_data['realtor'] = self.context['request'].user
        validated_data['realtor_email'] = self.context['request'].user.email
        return super().create(validated_data)
