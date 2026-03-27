from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class LibraryPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        loan_count = request.env['library.loan'].sudo().search_count([
            ('member_id', '=', partner.id),
            ('state', 'in', ['active', 'overdue', 'returned'])
        ])

        values['loan_count'] = loan_count
        return values

    @http.route(['/my/loans'], type='http', auth='user', website=True)
    def portal_my_loans(self, **kw):
        partner = request.env.user.partner_id

        loans = request.env['library.loan'].sudo().search([
            ('member_id', '=', partner.id)
        ], order='loan_date desc')

        values = self._prepare_portal_layout_values()
        values.update({
            'loans': loans,
            'page_name': 'my_loans',
        })
        return request.render('library_management.portal_my_loans', values)

    @http.route(['/my/loans/<int:loan_id>/renew'], type='http', auth='user', website=True)
    def portal_renew_loan(self, loan_id, **kw):
        partner = request.env.user.partner_id
        loan = request.env['library.loan'].sudo().browse(loan_id)

        if not loan.exists():
            return request.redirect('/my/loans')

        if loan.member_id.id != partner.id:
            return request.redirect('/my/loans')

        if loan.state in ['overdue', 'returned']:
            return request.redirect('/my/loans')

        loan.action_renew_loan()
        return request.redirect('/my/loans')