/* 
 * Robot Webinterface - Main Script
 * Simon B., https://wired.chillibasket.com
 * V1.4, 16th February 2020
 */


// Control speed at which gamepad
// can move the arms and head
var armsMultiplier = 6;
var headMultiplier = 5;

// Runtime variables to manage the gamepad
var moveXY = [0,0,0,0];
var moveYP = [0,0,0,0];
var moveArms = [0,50,0,50];
var moveHead = [50,50];
var gamepadTimer;
var gamePadActive = 0;
var jsJoystick;

// Timer to periodically check if Arduino has sent a message
var arduinoTimer;


/*
 * Update Web-Interface Settings
 */
function sendSettings(type, value) {
	
	// If shutdown is requested, show a confirmation prompt
	if (type=="shutdown") {
		if (!confirm("Are you sure you want to shutdown?")) {
			return 0;
		}
	}
	
	//alert(type + ", " + value);
	// Send data to python app, so that it can be passed on
	$.ajax({
		url: "/settings",
		type: "POST",
		data: {"type" : type, "value": value},
		dataType: "json",
		success: function(data){
			// If a response is received from the python backend, but it contains an error
			if(data.status == "Error"){
				showAlert(1, 'Error!', data.msg, 1);
				return 0;
			
			// Else if response is all good
			} else {
				showAlert(0, 'Success!', 'Settings have been updated.', 1);
				
				// If setting related to the camera stream, show/hide the video stream
				if(typeof data.streamer !== "undefined"){
						if(data.streamer == "Active"){
							$('#conn-streamer').html('End Stream');
							$('#conn-streamer').removeClass('btn-outline-info');
							$('#conn-streamer').addClass('btn-outline-danger');
							$("#stream").attr("src","http:/" + "/" + window.location.hostname + ":8081/?action=stream");
						} else if(data.streamer == "Offline"){
							$('#conn-streamer').html('Reactivate');
							$('#conn-streamer').addClass('btn-outline-info');
							$('#conn-streamer').removeClass('btn-outline-danger');
							$("#stream").attr("src","/static/streamimage.jpg");
						}
				}
				return 1;
			}
		},
		error: function(error) {
			// If no response was recevied from the python backend, show an "unknown" error
			if (type == "shutdown") {
				showAlert(0, 'Raspberry Pi is now shutting down!', 'The WALL-E web-interface is no longer active.', 1);
			} else {
				showAlert(1, 'Unknown Error!', 'Unable to update settings.', 1);
			}
			return 0;
		}
	});
}










/*
 * This function displays an alert message at the bottom of the screen
 */
function showAlert(error, bold, content, fade) {
	if (fade == 1) $('#alert-space').fadeOut(100);
	var alertType = 'alert-success';
	if (error == 1) alertType = 'alert-danger';
	$('#alert-space').html('<div class="alert alert-dismissible ' + alertType + ' set-alert">\
								<button type="button" class="close" data-dismiss="alert">&times;</button>\
								<strong>' + bold + '</strong> ' + content + ' \
							</div>');			
	if (fade == 1) $('#alert-space').fadeIn(150);
	if (content == "Arduino not connected" && $('#conn-arduino').hasClass('btn-outline-danger')) {
		updateSerialList(false);
		$('#conn-arduino').html('Reconnect');
		$('#conn-arduino').addClass('btn-outline-info');
		$('#conn-arduino').removeClass('btn-outline-danger');
		$('#ardu-area').attr('data-original-title','Disconnected');
		$('#ardu-area').addClass('bg-danger');
		$('#ardu-area').removeClass('bg-success');
		$('#batt-area').addClass('d-none');
		clearInterval(arduinoTimer);
		console.log("Cleared arduino timer");
	}
}



// When controller is disconnected
function resetInfo(e) {
	if (gamePadActive == 1) {
		$('#cont-area').attr('data-original-title','Disconnected');
		$('#cont-area').addClass('bg-danger');
		$('#cont-area').removeClass('bg-success');
		//$('#joystick').removeClass('d-none');
		clearInterval(gamepadTimer);
		moveXY[0] = 0;
		moveXY[2] = 0;
		sendMovementValues();
		gamePadActive = 0;
	}
}

// When a new controller is connected
function updateInfo(e) {
	const { gamepad } = e;
	$('#cont-area').attr('data-original-title','Connected');
	$('#cont-area').removeClass('bg-danger');
	$('#cont-area').addClass('bg-success');
	//$('#joystick').addClass('d-none');
	gamepadTimer = setInterval(sendMovementValues, 100); 
}

// When a controller button is pressed
function pressButton(e) {
	const { buttonName } = e.detail;
	
	// A or Cross button - Sad eye expression
	if (buttonName === 'button_0') {
		servoPresets(document.getElementById('eyes-sad'),'eyes-sad','i');
	
	// B or Circle button - Right head tilt
	} else if (buttonName === 'button_1') {
		servoPresets(document.getElementById('eyes-right'),'eyes-right','l');
	
	// X or Square button - Left head tilt
	} else if (buttonName === 'button_2') {
		servoPresets(document.getElementById('eyes-left'),'eyes-left','j');
	
	// Y or Triangle button - Neutral eye expression
	} else if (buttonName === 'button_3') {
		servoPresets(document.getElementById('eyes-neutral'),'eyes-neutral','k');
	
	// Left Trigger button - Lower left arm
	} else if (buttonName === 'button_6') {
		moveArms[0] = -1;
	
	// Left Bumper button - Raise left arm
	} else if (buttonName === 'button_4') {
		moveArms[0] = 1;
		
	// Right Trigger button - Lower right arm
	} else if (buttonName === 'button_7') {
		moveArms[2] = -1;
		
	// Right Bumper button - Raise right arm
	} else if (buttonName === 'button_5') {
		moveArms[2] = 1;
	
	// Press down on left stick - Move arms back to neutral position
	} else if (buttonName === 'button_10') {
		moveArms[0] = 0;
		moveArms[1] = 50;
		moveArms[2] = 0;
		moveArms[3] = 50;
		servoPresets(document.getElementById('arms-neutral'),'arms-neutral','n');
	
	// Press down on right stick - Move head back to neutral position
	} else if (buttonName === 'button_11') {
		moveHead[0] = 50;
		servoControl(document.getElementById('head-rotation'),'G',50);
		moveHead[1] = 125;
		servoPresets(document.getElementById('head-neutral'),'head-neutral','g');
		
	// Back or Share button - Turn on/off automatic servo mode
	} else if (buttonName === 'button_8') {
		if ($('#auto-anime').parent().hasClass('active')) {
			$('#auto-anime').parent().removeClass('active');
			$('#manu-anime').parent().addClass('active');
			sendSettings('animeMode',0);
			servoInputs(1);
		} else if ($('#manu-anime').parent().hasClass('active')) {
			$('#auto-anime').parent().addClass('active');
			$('#manu-anime').parent().removeClass('active');
			sendSettings('animeMode',1);
			servoInputs(0);
		}
	
	// Left d-pad button - Play random sound
	} else if (buttonName === 'button_14') {
		var fileNames = [];
		var fileLengths = [];
		$("#audio-accordion div div a").each(function() { 
			fileNames.push($(this).attr('file-name'));
			fileLengths.push($(this).attr('file-length'));
		});
		var randomNumber = Math.floor((Math.random() * fileNames.length));
		playAudio(fileNames[randomNumber],fileLengths[randomNumber]);
		
	// Right d-pad button - Play random servo animation
	} else if (buttonName === 'button_15') {
		var fileNames = [];
		var fileLengths = [];
		$("#anime-accordion div div a").each(function() { 
			fileNames.push($(this).attr('file-name'));
			fileLengths.push($(this).attr('file-length'));
		});
		var randomNumber = Math.floor((Math.random() * fileNames.length));
		anime(fileNames[randomNumber],fileLengths[randomNumber]);
		console.log(randomNumber);
	}
}





/*
 * This function is run once when the page is loading
 */
window.onload = function () { 
	var h = window.innerHeight - 100;
	var cw = $('#limit').width();
	var pointer = 80;
	
	if (h > cw) {
		$('#limit').css({'height':cw+'px'});
	} else {
		$('#limit').css({'height':h+'px'});
		$('#limit').css({'width':h+'px'});
		pointer = 60;
		$('#base').css({'width':pointer+'px'});
		$('#base').css({'height':pointer+'px'});
		$('#stick').css({'width':pointer+'px'});
		$('#stick').css({'height':pointer+'px'});
		cw = h;
	}
	$('#stick').css({'top':Math.round(cw/2-pointer/2)+'px'});
	$('#stick').css({'left':Math.round(cw/2-pointer/2)+'px'});
	$('#base').css({'top':Math.round(cw/2-pointer/2)+'px'});
	$('#base').css({'left':Math.round(cw/2-pointer/2)+'px'});

	var offsets = document.getElementById('limit').getBoundingClientRect();
	var top = offsets.top;
	var left = offsets.left;
	
	jsJoystick = new VirtualJoystick({
		mouseSupport: true,
		stationaryBase: true,
		baseX: left+(cw/2),
		baseY: top+(cw/2),
		center: (cw/2),
		limitStickTravel: true,
		stickRadius: Math.round(cw/2) - pointer/2,
		container: document.getElementById('limit'),
		stickElement: document.getElementById('stick'),
		//baseElement: document.getElementById('base'),
		useCssTransform: true,
		updateText: document.getElementById('joytext')
	});
}


/*
 * This function is run when the window is resized
 */
$(window).resize(function () {
	var h = window.innerHeight - 100;
	var w = window.innerWidth;
	var cw = (w - 30) * 0.8;
	if (w > 767) cw = ((w / 2) - 30) * 0.8;
	if (cw > 500) cw = 500;
	var pointer = 80;
	
	if (h < cw) {
		cw = h;
		pointer = 60;
	}
	
	$('#limit').css({'height':cw+'px'});
	$('#limit').css({'width':cw+'px'});
	$('#base').css({'width':pointer+'px'});
	$('#base').css({'height':pointer+'px'});
	$('#stick').css({'width':pointer+'px'});
	$('#stick').css({'height':pointer+'px'});
	$('#stick').css({'top':Math.round(cw/2-pointer/2)+'px'});
	$('#stick').css({'left':Math.round(cw/2-pointer/2)+'px'});
	$('#base').css({'top':Math.round(cw/2-pointer/2)+'px'});
	$('#base').css({'left':Math.round(cw/2-pointer/2)+'px'});

	var middleX = w / 2;
	if (w > 767) middleX += w / 4;
	var middleY = 40 + 30 + cw / 2;
	
	jsJoystick.updateDimensions(middleX, middleY, (cw/2), Math.round(cw/2) - pointer/2);
});

