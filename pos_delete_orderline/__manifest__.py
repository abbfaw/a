# -*- coding: utf-8 -*-
{
    'name': "pos_delete_orderline",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'category': 'Point of Sale',
    'depends': ['base','point_of_sale','pos_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/pos_order_form.xml',
          'security/security.xml',
          'views/pos_order_form.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_delete_orderline/static/src/js/Chrome.js',
            'pos_delete_orderline/static/src/js/hide_refund.js',
            'pos_delete_orderline/static/src/js/delete_orderline.js',
            'pos_delete_orderline/static/src/js/ticket_screen.js',
            ('replace', 'point_of_sale/static/src/js/Misc/NumberBuffer.js', 'pos_delete_orderline/static/src/js/Misc/NumberBuffer.js'),
            ('remove', 'point_of_sale/static/src/xml/Screens/ProductScreen/ControlButtons/RefundButton.xml'),
            'pos_delete_orderline/static/src/xml/RefundButton.xml',
            ('remove','pos_sale/static/src/xml/SetSaleOrderButton.xml'),
            'pos_delete_orderline/static/src/xml/SetSaleOrderButton.xml',
            'pos_delete_orderline/static/src/xml/CashMoveButton.xml',
            'pos_delete_orderline/static/src/xml/HeaderButton.xml',
            
        ],
        'web.assets_common': [
            'pos_delete_orderline/static/src/js/pos_quantity.js',
        ],
        
    },
}
