from rest_framework import serializers
from django.contrib.auth import get_user_model
from userauths.models import Profile, ContactUs, User
from django.contrib.auth import authenticate


User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'role', 'bio']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'default': 'guest'}  
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            bio=validated_data.get('bio', ''),
            role=validated_data.get('role', 'guest')
        )
        # Hash the password
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # def validate(self, attrs):
    #     user = authenticate(email=attrs['email'], password=attrs['password'])
    #     if user is None:
    #         raise serializers.ValidationError("Invalid email or password.")
    #     return user  
    
    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        # Authenticate  with email 
        user = authenticate(username=email, password=password)
        
        if user is None:
            raise serializers.ValidationError("Invalid credentials, please try again")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is inactive")
        
        data["user"] = user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'full_name', 'bio', 'phone', 'address', 'country', 'verified', 'image']
        read_only_fields = ['user']  

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)
        instance.country = validated_data.get('country', instance.country)
        instance.verified = validated_data.get('verified', instance.verified)

        if 'image' in validated_data:
            instance.image = validated_data['image']

        instance.save()
        return instance


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['full_name', 'email', 'phone', 'subject', 'message']

    def create(self, validated_data):
        return super().create(validated_data)