from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import DriverLicenseVerification
from .serializers import (
    UserSerializer, UserRegistrationSerializer, DriverLicenseVerificationSerializer,
    UserProfileUpdateSerializer, ChangePasswordSerializer
)

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """Register a new user"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileView(generics.RetrieveUpdateAPIView):
    """View and update user profile"""
    
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserProfileUpdateSerializer

class ChangePasswordView(generics.UpdateAPIView):
    """Change user password"""
    
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Incorrect password"]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password successfully changed"}, 
                            status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DriverLicenseVerificationViewSet(viewsets.ModelViewSet):
    """API for driver license verification"""
    
    queryset = DriverLicenseVerification.objects.all()
    serializer_class = DriverLicenseVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users see only their own requests, admins see all
        user = self.request.user
        if not user or not user.is_authenticated:
            return DriverLicenseVerification.objects.none()
        if user.is_staff:
            return DriverLicenseVerification.objects.all()
        return DriverLicenseVerification.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a verification request (admin only)"""
        verification = self.get_object()
        verification.status = 'approved'
        verification.save()
        
        # Update user status
        user = verification.user
        user.is_verified_driver = True
        user.save()
        
        return Response({"message": "Verification successfully approved"})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a verification request (admin only)"""
        verification = self.get_object()
        verification.status = 'rejected'
        verification.comment = request.data.get('comment', '')
        verification.save()
        
        return Response({"message": "Verification rejected"})