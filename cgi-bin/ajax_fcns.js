
//
// ajax functions for basic getting info and sending info
//
// ajax_set(url, objectID)
// ajax_do( url );
// ajax_get(url, fcn to call with response string)
// ajax_put(url, post_string, fcn to call with response string)
// basic_logout( url ) -- cancel credentials for current page
//
// hist: 2014-08-18 added logout function, folded in _do and _set
//

	//
	// ajax_set( resource, objID )
	//  purpose: objID.innerHTML = resource()
	//     i.e.: call a remote function and display result on page
	//     args: addr, objID
	//     rets: nothing, this is an async call
	//
	function ajax_set( addr, objID )
	{
		ajax_get( addr, function(x)
				{
					var o = document.getElementById(objID);
					o.innerHTML = x;
				}
		);
	}

	//
	//  ajax_do( resource )
	//  purpose: eval(resource())
	//     i.e.: call a remote function and eval the result 
	//     args: addr
	//     rets: nothing, this is an async call
	//
	function ajax_do( addr )
	{
		ajax_get( addr, function(x) 
				{
					eval(x);
				}
		);
	}

	//
	//  ajax_get( resource, handler )
	//    purp: set up an GET ajax request
	//    args: addr, and name of function
	//    rets: nothing
	//
	function ajax_get( addr, handler )
	{
		var xmlhttp = get_xmlreq(handler);
		//alert("setting " + addr );
		xmlhttp.open("GET", addr, true);
		xmlhttp.send();
	}
			
	//
	//  ajax_put( resource, string, handler )
	//    purp: set up an ajax POST request
	//    args: addr, string to send, name of function
	//    rets: nothing
	//
	function ajax_put( addr, str, handler )
	{
		var xmlhttp = get_xmlreq(handler);
		xmlhttp.open("POST", addr, true);
		xmlhttp.send( str );
	}

	//
	// logout from a session by sending an invalid login/passwd pair
	//
	function basic_logout_(s)
	{
	}

	function basic_logout( addr )
	{
		var xmlhttp = get_xmlreq(basic_logout_);

		//alert("setting " + addr );
		xmlhttp.open("GET", addr, false, "logout", "logout");
		xmlhttp.send();
		xmlhttp.abort();
	}

	//
	// browser independent version of making a request
	//  args: name of handler
	//  rets: an ajax object, ready to use
	//
	//
	function get_xmlreq(handler)
	{
		var xmlhttp;
		if ( window.XMLHttpRequest )	// IE7+, Firefox, ...
		{
			xmlhttp = new XMLHttpRequest();
		}
		else	// IE5, IE6
		{
			xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
		}
		xmlhttp.onreadystatechange = 
			function()
			{
				if ( xmlhttp.readyState == 4 &&
				     xmlhttp.status     == 200 )
				{
					// alert(xmlhttp.responseText);
					handler(xmlhttp.responseText);
				}
			};
		return xmlhttp;
	}

