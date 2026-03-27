from odoo import fields, models
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _create_library_loans_from_order(self):
        """
        Recorre las lineas de la orden POS.
        Si encuentra productos marcados como items de biblioteca,
        busca el libro relacionado y crea automaticamente el prestamo.
        """
        Loan = self.env['library.loan']
        Book = self.env['library.book']

        for order in self:
            # Es obligatorio seleccionar cliente/socio en la orden POS
            if not order.partner_id:
                raise ValidationError('Debe seleccionar un cliente/socio en la orden POS.')

            # El cliente debe estar marcado como miembro de biblioteca
            if not order.partner_id.is_library_member:
                raise ValidationError('El cliente seleccionado no esta registrado como socio de biblioteca.')

            for line in order.lines:
                product = line.product_id

                # Solo procesar productos marcados como libros de biblioteca
                if not product.is_library_item:
                    continue

                # Buscar el libro que esta vinculado al producto del POS
                book = Book.search([('product_id', '=', product.id)], limit=1)

                if not book:
                    raise ValidationError(
                        f'No existe un libro asociado al producto "{product.display_name}".'
                    )

                # Validar si el libro esta disponible
                if not book.is_available:
                    raise ValidationError(
                        f'El libro "{book.name}" no esta disponible para prestamo.'
                    )

                # Validar cantidad de prestamos activos o vencidos del socio
                active_loans = Loan.search_count([
                    ('member_id', '=', order.partner_id.id),
                    ('state', 'in', ['active', 'overdue'])
                ])

                if active_loans >= 5:
                    raise ValidationError(
                        f'El socio "{order.partner_id.name}" ya tiene 5 prestamos activos.'
                    )

                # Crear el prestamo en el sistema
                Loan.create({
                    'book_id': book.id,
                    'member_id': order.partner_id.id,
                    'loan_date': fields.Date.today(),
                    'state': 'active',
                })

    def action_pos_order_paid(self):
        """
        Se ejecuta cuando la orden POS se marca como pagada.
        Luego de la logica normal de Odoo, se crean los prestamos asociados.
        """
        res = super().action_pos_order_paid()
        self._create_library_loans_from_order()
        return res      