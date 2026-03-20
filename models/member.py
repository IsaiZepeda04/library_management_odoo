from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_library_member = fields.Boolean(string='Library Member')
    member_date = fields.Date(string='Member Date', default =fields.Date.today)
    member_code = fields.Char(string='Member Code', readonly=True, copy=False, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_library_member') and not vals.get('member_code'):
                vals['member_code'] = self.env['ir.sequence'].next_by_code('library.member') or 'NEW'
        return super().create(vals_list)
    
    def write(self, vals):
        if 'member_code' in vals:
            vals.pop('member_code')
        return super().write(vals)