from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Prestamo de Libro'
    _order = 'loan_date desc'

    book_id = fields.Many2one('library.book', string='Libro', required=True)
    member_id = fields.Many2one(
        'res.partner',
        string='Miembro',
        required=True,
        domain=[('is_library_member', '=', True)]
    )
    loan_date = fields.Date(string='Fecha de prestamo', default=fields.Date.today, required=True)
    return_date = fields.Date(string='Fecha de devolucion')
    state = fields.Selection([
        ('active', 'Activo'),
        ('overdue', 'Vencido'),
        ('returned', 'Devuelto'),
    ], string='Estado', default='active', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        loans = super().create(vals_list)

        for loan in loans:
            if not loan.book_id.is_available:
                raise ValidationError('El libro no esta disponible para prestamo.')
            
            active_loans = self.search_count([
                ('member_id', '=', loan.member_id.id),
                ('state', 'in', ['active', 'overdue'])
            ])

            if active_loans > 5:
                raise ValidationError('El socio ya tiene 5 prestamos activos.')
            
            loan.book_id.is_available = False

        return loans

    def action_return_book(self):
        for record in self:
            if record.state == 'returned':
                continue
            record.state = 'returned'
            record.return_date = fields.Date.today()
            record.book_id.is_available = True

    @api.model
    def cron_mark_overdue_loans(self):
        today = fields.Date.today()
        limit_date = today - timedelta(days=30)

        overdue_loans = self.search([
            ('state', '=', 'active'),
            ('loan_date', '<=', limit_date),
        ])

        for loan in overdue_loans:
            loan.state = 'overdue'

            if not loan.member_id.email:
                continue

        self.env['mail.mail'].create({
            'subject': f'Prestamo vencido: {loan.book_id.name}',
            'body_html': f"""
                <p>Hola {loan.member_id.name},</p>
                <p>Tu prestamo del libro <strong>{loan.book_id.name}</strong> se encuentra vencido.</p>
                <p>Fecha de prestamo: {loan.loan_date}</p>
                <p>Por favor, realiza la devolucion lo antes posible.</p>
            """,
            'email_to': loan.member_id.email,
            'email_from': self.env.user.email or 'noreply@example.com',
        }).send()