odoo.define('pos_delete_orderline.TicketScreen', function(require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');
    const { posbus } = require('point_of_sale.utils');
    var core = require('web.core');
    var _t = core._t;

    console.log("essai");

    const PosDeleteOrderLineTicketScreen = TicketScreen => class extends TicketScreen {
        async _onDeleteOrder({ detail: order }) {
            const screen = order.get_screen_data();
            const cashier = this.env.pos.get_cashier()
            if (cashier.role == 'manager') {
                if (['ProductScreen', 'PaymentScreen'].includes(screen.name) && order.get_orderlines().length > 0) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: 'Existing orderlines',
                        body: `${order.name} has total amount of ${this.getTotal(
                            order
                        )}.\n Are you sure you want delete this order?`,
                    });
                    if (!confirmed) return;
                }
                if (order && (await this._onBeforeDeleteOrder(order))) {
                    if (order === this.env.pos.get_order()) {
                        this._selectNextOrder(order);
                    }
                    this.env.pos.removeOrder(order);
                }
            }else{
                const { confirmed, payload } = Gui.showPopup('ErrorPopup', {
                    title: _t('Autorisation'),
                    body: _t("Vous n'êtes pas autorisés à supprimer ces commandes. Veilliez contacter votre responsable"),
                })
           }
        }
    };

    Registries.Component.extend(TicketScreen, PosDeleteOrderLineTicketScreen);

    return PosDeleteOrderLineTicketScreen;
 });