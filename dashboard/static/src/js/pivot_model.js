/** @odoo-module **/

import { PivotModel } from "@web/views/pivot/pivot_model";
import { PivotView } from "@web/views/pivot/pivot_view";
import { computeReportMeasures, processMeasure } from "@web/views/helpers/utils";
import { Domain } from "@web/core/domain";

// console.log("PivotModel exec 4")
export class PivotModelInherit extends PivotModel {
    // Fonction chargé lorsque l'on vient sur le module dashboard
	async load(searchParams) {
        this.searchParams = searchParams;

        const activeMeasures =
            processMeasure(searchParams.context.pivot_measures) || this.metaData.activeMeasures;
        const metaData = this._buildMetaData({ activeMeasures });
        if (!this.reload) {
            metaData.rowGroupBys =
                searchParams.context.pivot_row_groupby ||
                (searchParams.groupBy.length ? searchParams.groupBy : metaData.rowGroupBys);
            this.reload = true;
        } else {
            metaData.rowGroupBys = searchParams.groupBy.length
                ? searchParams.groupBy
                : searchParams.context.pivot_row_groupby || metaData.rowGroupBys;
        }
        metaData.colGroupBys =
            searchParams.context.pivot_column_groupby || this.metaData.colGroupBys;

        if (JSON.stringify(metaData.rowGroupBys) !== JSON.stringify(this.metaData.rowGroupBys)) {
            metaData.expandedRowGroupBys = [];
        }
        if (JSON.stringify(metaData.colGroupBys) !== JSON.stringify(this.metaData.colGroupBys)) {
            metaData.expandedColGroupBys = [];
        }

        // Suppression des champs de la liste deroulante de mesure du modele sale.report
        if (metaData.resModel == 'sale.report'){
            const fields = this._delete_fields(metaData.fields)
            metaData.measures = computeReportMeasures(
                fields,
                metaData.fieldAttrs,
                metaData.activeMeasures,
                metaData.additionalMeasures
            );
        }else{
            metaData.measures = computeReportMeasures(
                metaData.fields,
                metaData.fieldAttrs,
                metaData.activeMeasures,
                metaData.additionalMeasures
            );
        }


        const config = { metaData, data: this.data };
        // console.log("Le config", config)
        return this._loadData(config);
    }

    // Fonction executé lorsque l'on change la ligne de pivot
    async addGroupBy(params) {
        // console.log("Le load 3", )
        const activeMeasures = this.metaData.activeMeasures
        // Activation de la mesure ratio lorsque Meilleur client payeur est selectionné
        /*if (params.fieldName == 'partner_id' && !('ratio' in activeMeasures)){
            // this.toggleMeasure('montant_du');
            // this.toggleMeasure('montant_total');
            this.toggleMeasure('ratio');
            // this._sortRows("ratio desc", { data: this.data, this.metaData });
        }*/
        if (this.race.getCurrentProm()) {
            return; // we are currently reloaded the table
        }

        const { groupId, fieldName, type, custom } = params;
        let { interval } = params;
        const metaData = this._buildMetaData();
        if (custom && !metaData.customGroupBys.has(fieldName)) {
            const field = metaData.fields[fieldName];
            if (!interval && ["date", "datetime"].includes(field.type)) {
                interval = DEFAULT_INTERVAL;
            }
            metaData.customGroupBys.set(fieldName, {
                ...field,
                id: fieldName,
            });
        }

        let groupBy = fieldName;
        if (interval) {
            groupBy = `${groupBy}:${interval}`;
        }
        if (type === "row") {
            metaData.expandedRowGroupBys.push(groupBy);
        } else {
            metaData.expandedColGroupBys.push(groupBy);
        }
        const config = { metaData, data: this.data };
        console.log("Le config", config)
        await this._expandGroup(groupId, type, config);
        this.metaData = metaData;
        // this._loadData({metaData, data: this.data});
        this.notify();
    }

    // Fonction permettant d'activer ou de desactiver une mesure
    async toggleMeasure(fieldName) {
    	// console.log("toggleMeasure ", fieldName)
        const metaData = this._buildMetaData();
        this.nextActiveMeasures = this.nextActiveMeasures || metaData.activeMeasures;
        metaData.activeMeasures = this.nextActiveMeasures;
        const index = metaData.activeMeasures.indexOf(fieldName);
        // console.log("L'index", inde)
        if (index !== -1) {
            // in this case, we already have all data in memory, no need to
            // actually reload a lesser amount of information (but still, we need
            // to wait in case there is a pending load)
            // console.log("iondex 1")
            metaData.activeMeasures.splice(index, 1);
            await Promise.resolve(this.race.getCurrentProm());
            this.metaData = metaData;
        } else {
            // console.log("index 2")
            metaData.activeMeasures.push(fieldName);
            let config = { metaData, data: this.data };
            await this._loadData(config);
        }
        this.nextActiveMeasures = null;
        this.notify();
    }

    // Fonction permettant de supprimer des colonnes dans la liste des mesures
    _delete_fields(fields) {
    	for (const field in fields){
    		switch(field){
    			case 'discount_amount':
    				delete(fields.discount_amount);
    				break;
    			// case 'order_id':
    			// 	delete(fields.order_id);
    			// 	break;
    			case 'untaxed_amount_invoiced':
    				delete(fields.untaxed_amount_invoiced);
    				break;
    			case 'untaxed_amount_to_invoice':
    				delete(fields.untaxed_amount_to_invoice);
    				break;
    			case 'nbr':
    				delete(fields.nbr);
    				break;
    			case 'weight':
    				delete(fields.weight);
    				break;
    			case 'qty_to_invoice':
    				delete(fields.qty_to_invoice);
    				break;
    			case 'qty_to_deliver':
    				delete(fields.qty_to_deliver);
    				break;
    			case 'qty_invoiced':
    				delete(fields.qty_invoiced);
    				break;
    			case 'qty_delivered':
    				delete(fields.qty_delivered);
    				break;
    			case 'product_uom_qty':
    				delete(fields.product_uom_qty);
    				break;
    			case 'discount':
    				delete(fields.discount);
    				break;
    			case 'volume':
    				delete(fields.volume);
    				break;
    		}
    	}
    	return fields;
    }
}

export class PivotViewInherit extends PivotView {}

PivotView.Model = PivotModelInherit;