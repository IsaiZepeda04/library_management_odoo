from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _create_library_loans_from_order(self):
        LibraryBook = self.env['library.book']
        LibraryLoan = self.env['library.loan']

        for order in self:
            partner = order.partner_id
            if not partner:
                continue

            active_loans_count = LibraryLoan.search_count([
                ('member_id', '=', partner.id),
                ('state', '=', 'active'),
            ])

            for line in order.lines:
                book = LibraryBook.search([
                    ('product_id', '=', line.product_id.id)
                ], limit=1)

                if not book:
                    continue

                if not book.is_available:
                    raise ValidationError(
                        f'El libro "{book.name}" no está disponible para préstamo.'
                    )

                if active_loans_count >= 5:
                    raise ValidationError(
                        f'El socio "{partner.name}" ya tiene 5 préstamos activos.'
                    )

                LibraryLoan.create({
                    'member_id': partner.id,
                    'book_id': book.id,
                    'loan_date': fields.Date.today(),
                    'state': 'active',
                })

                book.is_available = False
                active_loans_count += 1

    @api.model
    def create_from_ui(self, orders, draft=False):
        result = super().create_from_ui(orders, draft=draft)

        order_ids = []
        for item in result:
            if isinstance(item, dict) and item.get('id'):
                order_ids.append(item['id'])
            elif isinstance(item, int):
                order_ids.append(item)

        if order_ids:
            pos_orders = self.browse(order_ids)
            pos_orders._create_library_loans_from_order()

        return result        