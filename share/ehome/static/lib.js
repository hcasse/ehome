
/* Element management */

function getElement(id) {
	return document.getElementById(elt);
}

function getAttr(elt) {
	e = document.getElementById(elt);
	return e.getAttribute(att);
}

function getInput(elt) {
	e = document.getElementById(elt);
	return e.value;
}

function setInput(elt, val) {
	e = document.getElementById(elt);
	e.value = val;
}

function setContent(elt, val) {
	e = document.getElementById(elt);
	e.innerHTML = val;
}

function setFocus(id) {
	e = document.getElementById(id);
	e.focus();
}

function setClass(id, cls) {
	document.getElementById(id).className = cls;	
}


/* Page manegement */

function setPage(name) {
	const target = window.location.origin + "/" + name;
	console.log("setPage(" + target + ")");
	window.location = target;
}


/* Connection management */
function askServer(cmd, fun) {
	const req = new XMLHttpRequest();
	req.onreadystatechange = function() {
		if(req.readyState == 4 && req.status == 200)
			fun(req);
	}
	req.open("GET", cmd, true);
	req.send();
}

function askXML(cmd, fun) {
	askServer(cmd, function(req) {
		fun(req.responseXML);
	});
}

function askText(cmd, fun) {
	askServer(cmd, function(req) {
		fun(req.responseText);
	});
}

