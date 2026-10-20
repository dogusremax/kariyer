const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const h of ['','?temiz']){await p.goto('http://127.0.0.1:8767/story-tasarim/story.html'+h);await p.waitForTimeout(1500);
for(const id of ['s1','s2','s3']){if(h&&id!=='s3')continue;await p.locator('#'+id).screenshot({path:'/mnt/project-files/danisman-basvuru/story-'+id.slice(1)+(h?'':'-yerlesim')+'.png'})}}
await b.close()})();
