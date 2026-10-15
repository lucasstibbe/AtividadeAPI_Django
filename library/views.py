from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book, Loan
from .serializers import AvailableBookSerializer, BookSerializer, LoanSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('id')
    serializer_class = BookSerializer

    def destroy(self, request, *args, **kwargs):
        book = self.get_object()  # já retorna 404 se não existir
        if book.loans.exists():
            return Response(
                {'detail': 'Não é possível remover um livro que possui empréstimos registrados.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='available')
    def available(self, request):
        books = Book.objects.filter(available=True).order_by('id')
        serializer = AvailableBookSerializer(books, many=True)
        return Response(serializer.data)


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.select_related('book').order_by('id')
    serializer_class = LoanSerializer

    @transaction.atomic
    def perform_destroy(self, instance):
        # Apagar um empréstimo em aberto libera o livro
        if instance.return_date is None:
            instance.book.available = True
            instance.book.save(update_fields=['available'])
        instance.delete()
