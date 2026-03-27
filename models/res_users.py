from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        users._sync_library_partner_member()
        return users

    def write(self, vals):
        res = super().write(vals)
        self._sync_library_partner_member()
        return res

    def _sync_library_partner_member(self):
        librarian_group = self.env.ref('library_management.group_library_librarian', raise_if_not_found=False)
        public_group = self.env.ref('library_management.group_library_public_user', raise_if_not_found=False)
        portal_group = self.env.ref('base.group_portal', raise_if_not_found=False)

        for user in self:
            partner = user.partner_id
            if not partner:
                continue

            has_library_role = False

            if librarian_group and librarian_group in user.group_ids:
                has_library_role = True
            if public_group and public_group in user.group_ids:
                has_library_role = True
            if portal_group and portal_group in user.group_ids:
                has_library_role = True

            if has_library_role and not partner.is_library_member:
                partner.write({
                    'is_library_member': True,
                })