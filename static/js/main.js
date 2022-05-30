window.isMobile = ('ontouchstart' in document.documentElement && /mobi/i.test(navigator.userAgent) )
console.log(`main.js: isMobile=${window.isMobile} height=${window.innerHeight}`)

// Use ScrollMagic to set paragraphs as 'active'
if (window.controller)  window.controller.destroy(true)
window.controller = new ScrollMagic.Controller({globalSceneOptions: {}})
Array.from(document.querySelectorAll('p')).forEach(p => {  // build scenes
    new ScrollMagic.Scene({
            triggerElement: p,
            triggerHook: window.isMobile ? 0.5 : 200/window.innerHeight, 
            offset: -20,
            duration: p.clientHeight
        })
        .setClassToggle(p, 'active') // add class toggle
        //.addIndicators()
        .addTo(controller)
})

// Google Analytics
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-DRHNQSMN5Y');
