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