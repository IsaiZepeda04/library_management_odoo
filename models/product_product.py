from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_library_item = fields.Boolean(
        string='Es item de biblioteca',
        help='Indica si este producto representa un libro para prestamos.'
    )