odoo.define('matarshop_pos.InheritClosePosPopup', function (require) {
    'use strict';

    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');


    const InheritClosePosPopup = (ClosePosPopup) =>
        class extends ClosePosPopup {
            setup() {
                super.setup();
                this.noAccess = false;
            }

            async checkUserAccess(){
                try {
                    const quant = await this.env.services.rpc({
                        model: 'pos.session',
                        method: 'check_user_access',
                        args: [],
                    });
                    this.noAccess = quant ;
                    console.log('quantity ..........',quant);
                    let value = '';
                    if (quant){
                        value = 'responsable';
                    }

                    return value;
                } catch (error) {
                    console.log('tyty .........', error);

                }
                finally{
                    console.log('lttetetet , ......', this.noAccess);
                }

            }

            async confirm() {

                if (this.defaultCashDetails.no_access){
                    if (this.hasDifference()){
                        const { confirmed, payload } = await this.showPopup('ErrorPopup', {
                                title: this.env._t('Erreur de fermeture'),
                                body: this.env._t("Impossible de fermer la caisse, il y a un écart entre le montant attendu et le montant renseigné"),
                                });
                    }
                    else {
                        return super.confirm();
                    }
                }
                else{
                    return super.confirm();
                }
            }



        };
    Registries.Component.extend(ClosePosPopup, InheritClosePosPopup);

    return InheritClosePosPopup;
});