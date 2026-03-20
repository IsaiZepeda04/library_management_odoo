from odoo import http
from odoo.http import request, Response
import json

class LibraryApiController(http.Controller):
    
    @http.route('/api/book', type='http', auth='public', method=['GET'], csrf=False)
    def get_book_availability(self, **kwargs):
        isbn = kwargs.get('isbn')

        if not isbn:
            return Response(
                json.dumps({
                    'error': 'Debe proporcionar el parametro ISBN'
                }),
                status=400,
                content_type='application/json'
            )
        
        book = request.env['library.book'].sudo().search([
            ('isbn', '=', isbn)
        ], limit=1)

        if not book:
            return Response(
                json.dumps({
                    'error': f'No se encontro ningun libro con ISBN {isbn}.'
                }),
                status=404,
                content_type='application/json'
            )
        
        return Response(
            json.dumps({
                'id': book.id,
                'isbn': book.isbn,
                'titulo': book.name,
                'disponibilidad': 'Disponible' if book.is_available else 'No Disponible'
            }),
            status=200,
            content_type='application/json'
        )

