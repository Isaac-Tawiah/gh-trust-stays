import os
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction

from apps.properties.models import Booking
from apps.properties.choices import BookingStatus as BookingStatusChoices
from .models import Payment, Payout
from .serializers import PaymentSerializer

# Initialize Paystack with your secret key
# In production, use environment variable: os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY', 'sk_test_6f4bce34f464e95b7affac6ca461ac916b7f1bd7')
paystack = Paystack(secret_key=PAYSTACK_SECRET_KEY)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_payment(request):
    """
    Initialize a payment for a booking.
    
    Request body:
    {
        "booking_id": "uuid-of-booking",
        "method": "MOMO"  # MOMO, CARD, or BANK
    }
    """
    booking_id = request.data.get('booking_id')
    method = request.data.get('method', 'MOMO')

    if not booking_id:
        return Response({'error': 'booking_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)

    # Prevent duplicate payments
    if hasattr(booking, 'payment') and booking.payment.status == 'SUCCESS':
        return Response({'error': 'This booking has already been paid for.'}, status=status.HTTP_400_BAD_REQUEST)

    # Determine the channel based on method
    channel_map = {
        'MOMO': 'mobile_money',
        'CARD': 'card',
        'BANK': 'bank',
    }
    channel = channel_map.get(method, 'mobile_money')

    reference = f"GTS-{booking.id.hex[:8].upper()}"

    try:
        # Initialize transaction with Paystack
        response = Transaction.initialize(
            reference=reference,
            amount=int(booking.total_price * 100),  # Paystack uses kobo/pesewas
            email=request.user.email or f"{request.user.phone_number}@ghtruststays.com",
            channels=[channel],
            metadata={
                'booking_id': str(booking.id),
                'user_id': str(request.user.id),
                'method': method,
            }
        )

        if response.get('status'):
            data = response.get('data', {})

            # Create payment record
            payment, created = Payment.objects.update_or_create(
                booking=booking,
                defaults={
                    'user': request.user,
                    'amount': booking.total_price,
                    'method': method,
                    'paystack_reference': reference,
                    'paystack_access_code': data.get('access_code', ''),
                    'status': 'PENDING',
                }
            )

            booking.status = BookingStatusChoices.PENDING
            booking.save(update_fields=['status'])

            return Response({
                'message': 'Payment initialized. Complete payment using the authorization URL.',
                'authorization_url': data.get('authorization_url'),
                'access_code': data.get('access_code'),
                'reference': reference,
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Failed to initialize payment with Paystack.',
            'details': response.get('message', 'Unknown error')
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_payment(request, reference):
    """
    Verify a payment by its Paystack reference.
    """
    try:
        response = Transaction.verify(reference=reference)

        if response.get('status'):
            data = response.get('data', {})
            paystack_status = data.get('status')

            payment = get_object_or_404(Payment, paystack_reference=reference)

            if paystack_status == 'success':
                payment.status = 'SUCCESS'
                payment.paid_at = data.get('paid_at')
                payment.save(update_fields=['status', 'paid_at'])

                booking = payment.booking
                booking.status = BookingStatusChoices.CONFIRMED
                booking.save(update_fields=['status'])

                # Create pending payout for host
                Payout.objects.create(
                    host=booking.listing.host,
                    booking=booking,
                    amount=payment.amount,
                    status='PENDING',
                )

                return Response({'message': 'Payment verified. Booking confirmed.', 'status': 'SUCCESS'})

            elif paystack_status == 'failed':
                payment.status = 'FAILED'
                payment.save(update_fields=['status'])
                return Response({'message': 'Payment failed.', 'status': 'FAILED'})

            return Response({'message': f'Payment status: {paystack_status}', 'status': paystack_status})

        return Response({'error': 'Verification failed.'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
def paystack_webhook(request):
    """
    Webhook endpoint for Paystack to call when payment status changes.
    Paystack sends events like charge.success, transfer.success, etc.
    """
    import json
    import hashlib

    # Verify webhook signature
    paystack_signature = request.headers.get('x-paystack-signature', '')
    body = request.body.decode('utf-8')

    # In production, verify the signature with your secret key
    # secret_key = os.environ.get('PAYSTACK_SECRET_KEY')
    # computed_signature = hashlib.sha512((body + secret_key).encode()).hexdigest()
    # if computed_signature != paystack_signature:
    #     return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)

    event = json.loads(body)
    event_type = event.get('event')
    data = event.get('data', {})

    if event_type == 'charge.success':
        reference = data.get('reference')
        try:
            payment = Payment.objects.get(paystack_reference=reference)
            payment.status = 'SUCCESS'
            payment.paid_at = data.get('paid_at')
            payment.save(update_fields=['status', 'paid_at'])

            booking = payment.booking
            booking.status = BookingStatusChoices.CONFIRMED
            booking.save(update_fields=['status'])

            Payout.objects.get_or_create(
                booking=booking,
                defaults={
                    'host': booking.listing.host,
                    'amount': payment.amount,
                    'status': 'PENDING',
                }
            )

            return Response({'message': 'Webhook processed.'}, status=status.HTTP_200_OK)

        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'message': 'Event received.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    """Get all payments for the authenticated user."""
    payments = Payment.objects.filter(user=request.user)
    serializer = PaymentSerializer(payments, many=True)
    return Response({'count': payments.count(), 'results': serializer.data})