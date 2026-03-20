from odoo import http, fields
from odoo.http import request


class LibraryPortal(http.Controller):

    @http.route(['/my/loans'], type='http', auth='user', website=True)
    def portal_my_loans(self, **kw):
        partner = request.env.user.partner_id

        loans = request.env['library.loan'].sudo().search([
            ('member_id', '=', partner.id)
        ], order='loan_date desc')

        values = {
            'loans': loans,
            'page_name': 'my_loans',
        }
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

        loan.loan_date = fields.Date.today()
        return request.redirect('/my/loans')