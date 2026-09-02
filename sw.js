const CACHE='sodegau-ride-v051';
const SHELL=['./','./index.html','./app.js','./cityhall.html','./cityhall.js','./offline.html','./manifest.webmanifest','./icon.svg'];
const CACHEABLE_PATHS=new Set(SHELL.map(x=>new URL(x,self.registration.scope).pathname));
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(SHELL)))});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim()});
self.addEventListener('message',event=>{if(event.data&&event.data.type==='SKIP_WAITING')self.skipWaiting()});
function normalizedNavigationRequest(req){const u=new URL(req.url);u.search='';u.hash='';return new Request(u.toString(),{credentials:'same-origin'})}
self.addEventListener('fetch',event=>{const req=event.request;if(req.method!=='GET')return;const url=new URL(req.url);if(url.origin!==self.location.origin)return;
 if(req.mode==='navigate'){event.respondWith(fetch(req).then(res=>{if(res.ok){const key=normalizedNavigationRequest(req),copy=res.clone();event.waitUntil(caches.open(CACHE).then(c=>c.put(key,copy)))}return res}).catch(async()=>{const key=normalizedNavigationRequest(req);return(await caches.match(key))||(await caches.match('./offline.html'))}));return}
 if(!CACHEABLE_PATHS.has(url.pathname)){event.respondWith(fetch(req));return}
 event.respondWith(caches.match(req,{ignoreSearch:true}).then(hit=>{const network=fetch(req).then(res=>{if(res.ok&&res.type==='basic'){const clean=new Request(new URL(url.pathname,self.location.origin).toString());const copy=res.clone();event.waitUntil(caches.open(CACHE).then(c=>c.put(clean,copy)))}return res});return hit||network.catch(()=>hit)}))});
