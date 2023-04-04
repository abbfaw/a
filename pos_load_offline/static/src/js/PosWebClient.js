odoo.define('pos_load_offline.web_client', function (require) {
    'use strict';

    const WebClient = require('web.web_client');

    async function registerPosServiceWorker() {
        if (!('serviceWorker' in navigator)) {
            return;
        }

        try {
            const registration = await navigator.serviceWorker.register('/pos-cache', {scope: '/pos/'});
        } catch (error) {
            console.error(error);
        }
    }


    async function startPosApp(webClient) {
        await registerPosServiceWorker();
    }

    startPosApp(WebClient);
    return WebClient;
});
