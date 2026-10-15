from django.db import transaction
from rest_framework import serializers
from .models import Book, Loan


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'year', 'available', 'created_at']
        read_only_fields = ['id', 'created_at']

class AvailableBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'available']


class LoanSerializer(serializers.ModelSerializer):
    # Entrada: o cliente manda "book_id": 1
    book_id = serializers.PrimaryKeyRelatedField(
        source='book',
        queryset=Book.objects.all(),
    )
    # Saída: a resposta mostra os dados completos do livro
    book = BookSerializer(read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'book_id', 'book', 'person_name', 'loan_date', 'return_date']
        read_only_fields = ['id']

    def validate(self, data):
        instance = self.instance  # None no POST, o empréstimo existente no PUT

        book = data.get('book', instance.book if instance else None)
        loan_date = data.get('loan_date', instance.loan_date if instance else None)
        return_date = data.get('return_date', instance.return_date if instance else None)

        if return_date and loan_date and return_date < loan_date:
            raise serializers.ValidationError(
                {'return_date': 'A data de devolução não pode ser anterior à data do empréstimo.'}
            )

        if instance is None:
            # ---- Criação (POST) ----
            if return_date is not None:
                raise serializers.ValidationError(
                    {'return_date': 'Não informe return_date ao criar o empréstimo. '
                                    'Use PUT para registrar a devolução.'}
                )
            if not book.available:
                raise serializers.ValidationError(
                    {'book_id': 'Este livro não está disponível para empréstimo.'}
                )
        else:
            # ---- Atualização (PUT/PATCH) ----
            if book != instance.book:
                raise serializers.ValidationError(
                    {'book_id': 'Não é permitido trocar o livro de um empréstimo existente.'}
                )
            reabrindo = instance.return_date is not None and return_date is None
            if reabrindo and not book.available:
                raise serializers.ValidationError(
                    {'return_date': 'Não é possível reabrir este empréstimo: '
                                    'o livro já foi emprestado novamente.'}
                )

        return data

    @transaction.atomic
    def create(self, validated_data):
        loan = super().create(validated_data)
        loan.book.available = False          # emprestou → indisponível
        loan.book.save(update_fields=['available'])
        return loan

    @transaction.atomic
    def update(self, instance, validated_data):
        estava_aberto = instance.return_date is None
        loan = super().update(instance, validated_data)
        esta_aberto = loan.return_date is None

        if estava_aberto and not esta_aberto:     # devolução registrada
            loan.book.available = True
            loan.book.save(update_fields=['available'])
        elif not estava_aberto and esta_aberto:   # devolução desfeita
            loan.book.available = False
            loan.book.save(update_fields=['available'])

        return loan