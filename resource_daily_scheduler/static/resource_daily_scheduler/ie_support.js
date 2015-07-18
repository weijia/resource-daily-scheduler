if (!Date.now) {
    Date.now = function() { return new Date().getTime(); }
}

function msIeVersion() {
    var ua = window.navigator.userAgent;
    var msie = ua.indexOf("MSIE ");

    if (msie > 0)      // If Internet Explorer, return version number
        return (parseInt(ua.substring(msie + 5, ua.indexOf(".", msie))));
//    else                 // If another browser, return 0
//        alert('otherbrowser');

    return false;
}
