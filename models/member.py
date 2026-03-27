from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_library_member = fields.Boolean(string='Library Member')
    member_date = fields.Date(string='Member Date', default=fields.Date.today)
    member_code = fields.Char(string='Member Code', readonly=True, copy=False, index=True)

    _sql_constraints = [
        ('member_code_unique', 'unique(member_code)', 'El codigo de miembro debe ser unico.')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_library_member') and not vals.get('member_code'):
                vals['member_code'] = self.env['ir.sequence'].next_by_code('library.member') or 'NEW'
        return super().create(vals_list)

    def write(self, vals):
        # bloquear edición manual del código
        if 'member_code' in vals:
            vals.pop('member_code')

        # detectar si se está marcando como socio
        generate_code_for = self.env['res.partner']
        if vals.get('is_library_member'):
            generate_code_for = self.filtered(lambda r: not r.member_code and not r.is_library_member)

        res = super().write(vals)

        # generar código SIN volver a caer en nuestro write personalizado
        for record in generate_code_for:
            code = self.env['ir.sequence'].next_by_code('library.member') or 'NEW'
            super(ResPartner, record.sudo()).write({'member_code': code})

        return res