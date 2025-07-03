# from django.contrib.auth import get_user_model
# from rest_framework import status, generics
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.views import TokenObtainPairView
#
# from .serializers import UserSerializer, UserProfileSerializer, SignupSerializer
#
# User = get_user_model()
#
# # 회원가입 뷰
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def signup(request):
#     """회원가입"""
#     serializer = SignupSerializer(data=request.data)
#     if serializer.is_valid():
#         user = serializer.save()
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             'message': '회원가입이 완료되었습니다.',
#             'user': UserSerializer(user).data,
#             'refresh': str(refresh),
#             'access': str(refresh.access_token)
#         })
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# # 로그인은 JWT TokenObtainPairView 사용 (URL에 연결만 해주면 됨)
#
#
# # 로그아웃 (Refresh Token 무효화)
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout(request):
#     """로그아웃"""
#     try:
#         refresh_token = request.data.get('refresh_token')
#         if refresh_token:
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#         return Response({'message': '로그아웃 되었습니다.'})
#     except Exception as e:
#         return Response({'error': f'로그아웃 오류: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
#
#
# # 사용자 정보 조회
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def user_info(request):
#     """내 정보 조회"""
#     serializer = UserSerializer(request.user)
#     return Response(serializer.data)
#
#
# # 프로필 조회 및 수정
# class UserProfileView(generics.RetrieveUpdateAPIView):
#     serializer_class = UserProfileSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self):
#         return self.request.user
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#
#         # ManyToMany 필드 처리
#         many_to_many_fields = ['position', 'language', 'tech', 'coop_tool',
#                                'interest_field', 'interest_trend', 'career']
#         for field in many_to_many_fields:
#             if field in request.data and isinstance(request.data[field], list):
#                 getattr(instance, field).set(request.data[field])
#
#         self.perform_update(serializer)
#         return Response(serializer.data)
