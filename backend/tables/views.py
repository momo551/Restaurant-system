from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Table, Reservation, QRCode, TableSession
from .serializers import TableSerializer, ReservationSerializer, QRCodeSerializer, TableSessionSerializer
from users.permissions import HasTablesAccess
from rest_framework import permissions


class TableViewSet(viewsets.ModelViewSet):
    """ViewSet for Table management."""
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [HasTablesAccess]
    filterset_fields = ['status', 'floor', 'is_active']

    def get_permissions(self):
        if self.action in ['list', 'layout', 'retrieve', 'from_qr']:
            return [permissions.AllowAny()]
        return [HasTablesAccess()]

    @action(detail=False, methods=['get'], url_path='from-qr/(?P<code>[^/.]+)')
    def from_qr(self, request, code=None):
        """Get table info from QR code UUID."""
        try:
            qr = QRCode.objects.get(code=code, is_active=True)
            return Response(TableSerializer(qr.table).data)
        except QRCode.DoesNotExist:
            return Response({'error': 'كود غير صحيح'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update table status."""
        table = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Table.Status.choices):
            table.status = new_status
            table.save()
            return Response(TableSerializer(table).data)
        return Response({'error': 'حالة غير صحيحة'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_position(self, request, pk=None):
        """Update table position for visual layout."""
        table = self.get_object()
        table.position_x = request.data.get('position_x', table.position_x)
        table.position_y = request.data.get('position_y', table.position_y)
        table.save()
        return Response(TableSerializer(table).data)

    @action(detail=False, methods=['get'])
    def layout(self, request):
        """Get tables layout for visual representation."""
        floor = request.query_params.get('floor', 1)
        tables = Table.objects.filter(floor=floor, is_active=True)
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)


class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet for Reservation management."""
    queryset = Reservation.objects.select_related('table')
    serializer_class = ReservationSerializer
    permission_classes = [HasTablesAccess]
    filterset_fields = ['table', 'is_confirmed', 'reservation_time']

    def get_permissions(self):
        return [HasTablesAccess()]

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a reservation."""
        reservation = self.get_object()
        reservation.is_confirmed = True
        reservation.table.status = Table.Status.RESERVED
        reservation.table.save()
        reservation.save()
        return Response(ReservationSerializer(reservation).data)


class TableSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for Table Session management."""
    queryset = TableSession.objects.all()
    serializer_class = TableSessionSerializer
    permission_classes = [permissions.AllowAny] # Publicly accessible for customers

    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """Create a new session for a table."""
        try:
            table_id = request.data.get('table_id')
            table = Table.objects.get(id=table_id, is_active=True)
            # Find or create an active session for this table
            session = TableSession.objects.filter(table=table, is_active=True).first()
            if not session:
                session = TableSession.objects.create(table=table)
            return Response(TableSessionSerializer(session).data)
        except Table.DoesNotExist:
            return Response({'error': 'الطاولة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

