importScripts('/pos_load_offline/static/src/js/lib/idb-keyval.js');
importScripts('/pos_load_offline/static/src/js/lib/IndexedDB.js');

const serializeRequest = async (req) => ({
    url: req.url,
    body: await req.json(),
});

const serializeResponse = async (res) => ({
    body: await res.text(),
    status: res.status,
    statusText: res.statusText,
    headers: Object.fromEntries(res.headers.entries()),
});

const deserializeResponse = (responseData) => {
    const {body} = responseData;
    delete responseData.body;
    return new Response(body, responseData);
};

const buildCacheKey = ({url, body: {method, params}}) =>
    JSON.stringify({
        url,
        method,
        params,
    });

const isGET = (request) => request.method === 'GET';

const cacheTheRequest = async (request, response) => {
    if (isGET(request)) {
        const cache = await caches.open('POS-ASSETS');
        await cache.put(request.clone(), response.clone());
    } else {
        if (await IndexedDB.get('stopCaching')) {
            return;
        }
        const serializedRequest = await serializeRequest(request.clone());
        const serializedResponse = await serializeResponse(response.clone());
        await IndexedDB.set(buildCacheKey(serializedRequest), serializedResponse);
    }
};

const getResponseFromCache = async (request) => {
    if (isGET(request)) {
        const cache = await caches.open('POS-ASSETS');
        return await cache.match(request);
    } else {
        const serializedRequest = await serializeRequest(request);
        const cachedResponse = await IndexedDB.get(buildCacheKey(serializedRequest));
        if (cachedResponse) {
            return deserializeResponse(cachedResponse);
        } else {
            throw new Error(`Unable to find ${request.url} from (idb) cache.`);
        }
    }
};

const processFetchEvent = async ({request}) => {
    try {
        const response = await fetch(request.clone());
        await cacheTheRequest(request, response.clone());
        return response;
    } catch (fetchError) {
        try {
            return await getResponseFromCache(request);
        } catch (err) {
            console.warn(err);
        }
    }
};
self.addEventListener('fetch', (event) => event.respondWith(processFetchEvent(event)));