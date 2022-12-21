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

function setFocus(id) {
	e = document.getElementById(id);
	e.focus();
}

function setPage(name) {
	window.location = window.location.origin + "/" + name;
}
