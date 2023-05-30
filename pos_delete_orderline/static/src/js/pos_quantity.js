odoo.define("pos_quantity.paiement", function (require) {
    
    console.log("testrecharge");
    const Registries = require('point_of_sale.Registries');
    const paiementPos = require("point_of_sale.ProductScreen")

    const nextscreen = (paiementPos) =>
        class extends paiementPos {
            async _onClickPay() {
                const orderlines = this.env.pos.get_order().get_orderlines();
                var isProductNoPrice = false
                for (let orderline of orderlines) {
                    if (orderline.price == 0 || orderline.quantity == 0) {
                        isProductNoPrice = true;
                        continue;
                    }
                }
                if (isProductNoPrice) {
                    await this.showPopup('ErrorPopup', {
                        title: this.env._t('Erreur paiement'),
                        body: this.env._t("Impossible de valider une commande avec le prix d'un article à 0 CFA"),
                    });
                    return;
                } else {
                    return this.showScreen('PaymentScreen');

                }
            }
            get nextScreen() {
                this.env.pos.set_synch('connected', this.env.pos.db.get_orders().length)
                return !this.error ? 'ReceiptScreen' : 'ProductScreen';
            }

        }
    Registries.Component.extend(paiementPos, nextscreen);
    return paiementPos

});
