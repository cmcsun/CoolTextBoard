var set_cookie = function(cookieValue) {
    var today = new Date();
    var expire = new Date();
    var cookieName = 'name';
    expire.setTime(today.getTime() + 3600000*24*90);
    document.cookie = cookieName+"="+escape(cookieValue) + ";expires="+expire.toGMTString() + ";path=/";
};

var set_inputs = function() {
    var i=0;
    for (i=0;i<=document.forms.length-1;i++) {
        with(document.forms[i]) {
            if(!name.value) {name.value=get_cookie("name");}
        }
    }
};

var get_cookie = function(name) {
    with(document.cookie) {
        var regexp=new RegExp("(^|;\\s+)"+name+"=(.*?)(;|$)");
        var hit=regexp.exec(document.cookie);
        if (hit&&hit.length>2) return unescape(hit[2]);
        else return '';
    }
};

var quote = function(postnumber,thread) {
    var text = '>>'+postnumber+'\n';
    var textarea=document.getElementById("form"+thread).message;
    if(textarea) {
        if(textarea.createTextRange && textarea.caretPos) {
            var caretPos=textarea.caretPos;
            caretPos.text=caretPos.text.charAt(caretPos.text.length-1)==" "?text+" ":text;
        }
        else if(textarea.setSelectionRange) {
            var start=textarea.selectionStart;
            var end=textarea.selectionEnd;
            textarea.value=textarea.value.substr(0,start)+text+textarea.value.substr(end);
            textarea.setSelectionRange(start+text.length,start+text.length);
        }
        else {
            textarea.value+=text+" ";
        }
        textarea.focus();
    }
    textarea.setSelectionRange(4097,4097);
};

var subback_style = function() {
    for (var i = 0, n = document.getElementsByClassName('thread').length; i < n; ) {
        var div = document.createElement("div");
        div.className = "float";
        document.body.insertBefore(div, document.body.childNodes[i / 20]);
        for (var j = 0; j < 20 && i < n; j++, i++) {
            div.appendChild(document.getElementsByClassName('thread')[i]);
        }
    }
};

window.onload = function() { set_inputs(); };