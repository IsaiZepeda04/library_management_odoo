from datetime import date

from odoo import api, fields, models
from odoo.exceptions import ValidationError

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

    # Producto relacionado para integracion con POS.
    # El POS trabaja con productos, no directamente con library.book.
    product_id = fields.Many2one(
        'product.product',
        string='Producto POS',
        required=True,
        help='Producto asociado al libro para poder operarlo desde Punto de Venta.'
    )

    _sql_constraints = [
        ('isbn_unique', 'unique(isbn)', 'El ISBN debe ser unico.'),
        ('product_unique', 'unique(product_id)', 'Cada producto solo puede estar asociado a un libro.')
    ]

    @api.depends('publi_date')
    def _compute_years_since_publication(self):
        today = date.today()
        for record in self:
            if record.publi_date:
                record.years_since_publication = today.year - record.publi_date.year
            else:
                record.years_since_publication = 0

    @api.constrains('product_id')
    def _check_product_id(self):
        for record in self:
            if not record.product_id:
                raise ValidationError('Debe seleccionar un producto asociado al libro.')

    def action_create_loan(self):
        #Boton desde el formulario del libro.
        #Abre el formulario de prestamos con el libro cargado
        self.ensure_one()

        if not self.is_available:
            raise ValidationError('El libro no esta disponible para prestamo.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nuevo Prestamo',
            'res_model': 'library.loan',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_book_id': self.id,
            }

        }