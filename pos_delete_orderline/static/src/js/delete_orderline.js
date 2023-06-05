odoo.define('pos_delete_orderline.NumpadWidget', function(require) {
    'use strict';

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');
    const session = require('web.session');
    var core = require('web.core');
    var _t = core._t;

    const PosDeleteOrderLineNumpadWidget = NumpadWidget => class extends NumpadWidget {
        sendInput(key) {
            console.log("**********************************************", key)
            console.log("##############################################", key);
            if (key === 'Backspace'){
                let line = this.env.pos.get_order().get_selected_orderline();
                if (line) {
                    session.user_has_group('point_of_sale.group_pos_manager').then(manager => {
                        session.user_has_group('pos_delete_orderline.group_pos_reponsable_user').then(responsable => {
                            session.user_has_group('point_of_sale.group_pos_user').then(utilisateur => {
                                console.log('=====manager======', manager, '=================');
                                console.log('======repos=====', responsable, '=================');
                                console.log('======uti=====', utilisateur, '=================');
                                console.log("UN autre", utilisateur, !responsable, !manager);

                                if (line.quantity.toString().length === 1) {
                                    if (manager) {
                                        this.trigger('numpad-click-input', { key });
                                    } else if (utilisateur && responsable && !manager) {
                                        this.trigger('numpad-click-input', { key });
                                    } else if (utilisateur && !responsable && !manager) {
                                        this.env.pos.get_order().set_orderline_options(line, { 'quantity': 1 });
                                        const { confirmed, payload } = Gui.showPopup('ErrorPopup', {
                                            title: _t('Autorisation'),
                                            body: _t("Vous ne pouvez pas supprimer un article dans le panier, attribuer une quantité négative ou le mettre à 0, veuillez contacter votre Responsable."),
                                        });
                                    }
                                } else {
                                    this.trigger('numpad-click-input', { key });
                                }
                            });
                        });
                    });
                }
            } else {
                this.trigger('numpad-click-input', { key });
            }
        }
    };

    Registries.Component.extend(NumpadWidget, PosDeleteOrderLineNumpadWidget);

    return PosDeleteOrderLineNumpadWidget;
});
