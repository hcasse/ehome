
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
		
