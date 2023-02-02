odoo.define('account_secii.dashboard', function (require) {
"use strict";
var core = require('web.core');
var ListController = require('web.ListController');
var ListModel = require('web.ListModel');
var ListRenderer = require('web.ListRenderer');
var ListView = require('web.ListView');
var KanbanController = require('web.KanbanController');
var KanbanModel = require('web.KanbanModel');
var KanbanRenderer = require('web.KanbanRenderer');
var KanbanView = require('web.KanbanView');
var SampleServer = require('web.SampleServer');
var view_registry = require('web.view_registry');
const session = require('web.session');

var QWeb = core.qweb;

let dashboardValues;
SampleServer.mockRegistry.add('account.secii/retrieve_dashboard', () => {
    return Object.assign({}, dashboardValues);
});

var ManagerListDashboardRenderer = ListRenderer.extend({
    events:_.extend({}, ListRenderer.prototype.events, {
        'click .o_manager_dashboard_action': '_onDashboardActionClicked',
    }),
    /**
     * @override
     * @private
     * @returns {Promise}
     */
    _renderView: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            var values = self.state.dashboardValues;
            var manager_dashboard = QWeb.render('account_secii.managerDashboard', {
                values: values,
            });
            self.$el.prepend(manager_dashboard);
        });
    },

    /**
     * @private
     * @param {MouseEvent}
     */
    _onDashboardActionClicked: function (e) {
        e.preventDefault();
        var $action = $(e.currentTarget);
        this.trigger_up('dashboard_open_action', {
            action_name: "account_secii.view_secii_manager_tree_action",
            action_context: $action.attr('context'),
        });
    },
});

var ManagerListDashboardModel = ListModel.extend({
    /**
     * @override
     */
    init: function () {
        this.dashboardValues = {};
        this._super.apply(this, arguments);
    },

    /**
     * @override
     */
    __get: function (localID) {
        var result = this._super.apply(this, arguments);
        if (_.isObject(result)) {
            result.dashboardValues = this.dashboardValues[localID];
        }
        return result;
    },
    /**
     * @override
     * @returns {Promise}
     */
    __load: function () {
        return this._loadDashboard(this._super.apply(this, arguments));
    },
    /**
     * @override
     * @returns {Promise}
     */
    __reload: function () {
        return this._loadDashboard(this._super.apply(this, arguments));
    },

    /**
     * @private
     * @param {Promise} super_def a promise that resolves with a dataPoint id
     * @returns {Promise -> string} resolves to the dataPoint id
     */
    _loadDashboard: function (super_def) {
        var self = this;
        var dashboard_def = this._rpc({
            model: 'account.secii',
            method: 'retrieve_dashboard',
            context: session.user_context,
        });
        return Promise.all([super_def, dashboard_def]).then(function(results) {
            var id = results[0];
            dashboardValues = results[1];
            self.dashboardValues[id] = dashboardValues;
            return id;
        });
    },
});

var ManagerListDashboardController = ListController.extend({
    custom_events: _.extend({}, ListController.prototype.custom_events, {
        dashboard_open_action: '_onDashboardOpenAction',
    }),

    /**
     * @private
     * @param {OdooEvent} e
     */
    _onDashboardOpenAction: function (e) {
        return true
    },
});

var ManagerListDashboardView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Model: ManagerListDashboardModel,
        Renderer: ManagerListDashboardRenderer,
        Controller: ManagerListDashboardController,
    }),
});

view_registry.add('manager_list_dashboard', ManagerListDashboardView);

return {
    ManagerListDashboardModel: ManagerListDashboardModel,
    ManagerListDashboardRenderer: ManagerListDashboardRenderer,
    ManagerListDashboardController: ManagerListDashboardController
};


});