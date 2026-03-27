{
    'name': 'Library Management',
    'version': '1.0',
    'summary': 'Módulo de gestión de bibliotecas para libros, usuarios, autores y préstamos',
    'description': 'Módulo personalizado para gestionar una biblioteca en Odoo 19.',
    'category': 'Services',
    'author': 'Leonardo Zepeda',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'website', 'portal', 'point_of_sale', 'product'],
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'security/library_record_rules.xml',
        
        'data/member_sequence.xml',
        'data/loan_email_template.xml',
        'data/loan_cron.xml',

        'views/member_views.xml',
        'views/book_views.xml',
        'views/loan_views.xml',
        'views/menu_views.xml',
        'views/portal_templates.xml',
        'views/product_views.xml'
    ],
    'installable': True,
    'application': True,
}