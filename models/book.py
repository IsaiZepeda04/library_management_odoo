from datetime import date

from odoo import api, fields, models

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Libros de la biblioteca'
    _order = 'name'

    name = fields.Char(string='Titulo', required=True)
    author = fields.Char(string='Autor', required=True)
    isbn = fields.Char(string='ISBN', required=True)
    publi_date = fields.Date(string='Fecha de Publicacion')
    years_since_publication = fields.Integer(
        string='Años desde su publicacion',
        compute='_compute_years_since_publication',
        store=True
    )
    is_available = fields.Boolean(string='Disponible', default=True)

    product_id = fields.Many2one(
        'product.product',
        string='Producto POS',
        help='Producto asociado para operar este libro desde Punto de Venta'
    )

    _sql_constraints = [
        ('isbn_unique', 'unique(isbn)', 'El ISBN debe ser unico.'),
    ]

    @api.depends('publi_date')
    def _compute_years_since_publication(self):
        today = date.today()
        for record in self:
            if record.publi_date:
                record.years_since_publication = today.year - record.publi_date.year
            else:
                record.years_since_publication = 0

    def action_create_loan(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nuevo Prestamo',
            'res_model': 'library.loan',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_book_id': self.id,
                'default_loan_date': fields.Date.today(),
                'default_state': 'active',
            }

        }