// ==UserScript==
// @name         YouTube auto cinema mode
// @namespace    http://youtube.com/
// @version      0.1
// @description  YouTube auto cinema mode
// @author       pncolvr
// @match        https://*.youtube.com/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

if (document.cookie.indexOf("wide=1") === -1) {
    document.cookie="wide=1;domain=.youtube.com"
    location.reload();
}


// taken from https://github.com/SebastianSimon/youtube-save-time-stamp/blob/master/YouTube%3A%20Remember%20current%20time%20stamp.user.js
addEventListener("pause", () => {
  if(location.pathname.includes("/watch")){
    const url = new URL(location),
      [
        currentTime,
        totalTime
      ] = [
          ".ytp-time-current",
          ".ytp-time-duration"
        ].map((selector) => {
          const timeStamp = document.querySelector(selector)?.textContent;
          
          if(timeStamp){
            const time = timeStamp.split(":").map(Number);
            
            if(time.length === 4){
              time[1] += 24 * time[0];
              time.shift();
            }
            
            const {
                timeParam,
                totalSeconds
              } = time.reduceRight((aggregator, measure) => {
                  const unit = aggregator.timeUnits.shift(),
                    scalar = aggregator.timeScalars.shift();
                  
                  if(measure){
                    aggregator.timeParam = `${measure}${unit}${aggregator.timeParam}`;
                    aggregator.totalSeconds += scalar * measure;
                  }
                  
                  return aggregator;
                }, {
                  timeParam: "",
                  totalSeconds: 0,
                  timeUnits: [
                    "s",
                    "m",
                    "h"
                  ],
                  timeScalars: [
                    1,
                    60,
                    60 * 60
                  ]
                });
            
            return {
              timeParam,
              totalSeconds
            };
          }
          
          return null;
        });
    
    if(currentTime){
      if(currentTime.timeParam && currentTime.totalSeconds <= totalTime.totalSeconds - 5){
        if(currentTime.timeParam !== url.searchParams.get("t")){
          url.searchParams.set("t", currentTime.timeParam);
          history.replaceState(history.state, "", url);
        }
      }
      else{
        url.searchParams.delete("t");
        history.replaceState(history.state, "", url);
      }
    }
  }
}, {
  capture: true
});