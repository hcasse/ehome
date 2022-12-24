
var current_tab;
var update_time = new Map();
var current_timeout = null;

function doLogin() {
	const user = getInput("user");
	const pwd = getInput("pwd");
	setInput("pwd", "");
	askText(
		`/login?user=${user}&pwd=${pwd}`,
		function(res) {
			setContent("login-message", res);
			setFocus("pwd");
			if(res.indexOf("success") >= 0)
				setPage("main");
		}
	);
}

function onUserPress(e) {
	const code = (e.keyCode ? e.keyCode : e.which);
	if(code == 13)
		setFocus("pwd");
}
		
function logout() {
	setPage("logout");	
}

function help() {
}

function reloadTab() {
	const tab = current_tab;
	askText(`/content?tab=${tab}`, function(res) {
		setContent("tab-pages", res);
		t = update_time.get(tab);
		if(t > 0)
			current_timeout = setTimeout(reloadTab, t);
	});	
}

function moveTo(ntab) {
	setClass(`page-${current_tab}`, "tab-unselected");
	current_tab = ntab;
	if(current_timeout != null) {
		clearTimeout(current_timeout);
		current_timeout = null;
	}
	setClass(`page-${current_tab}`, "tab-selected");
	setContent("tab-pages", "Loading...");
	reloadTab();
}
