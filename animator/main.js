var startTime = -1;

// utils
function last(arr) { return arr[arr.length - 1]; }

// Settings
const settings = {
	car_color: "green",
	text_color: "black",
	fps: 12,
	car_width: 10,
	car_length: 7,
	frames: cars[0].length - 1,
};

// draw utilities
function drawCar(context, instant, settings) {
	// each frame computes its own drawCar
	return function(positions, i) {
		const pos =
  			  positions[instant.fmod] * (1 - instant.weight) +
  			  positions[instant.fmod + 1] * instant.weight;
		x = pos * (settings.width - 1) + 1;
		context.fillStyle = settings.car_color;
		context.fillRect(x, 1, settings.car_length, settings.car_width);
		context.strokeRect(x, 1, settings.car_length, settings.car_width);
		context.fillStyle = settings.text_color;
		context.fillText(i + "", x + settings.car_length / 2, settings.car_width / 2);
	}
}

function drawRoad(context, instant, settings) {
	context.fillStyle = settings.text_color;
	context.strokeRect(0, 0, settings.width, settings.car_width + 2);
}

function drawTime(context, instant, settings) {
	context.fillStyle = settings.text_color;
	context.fillRect(0, settings.car_width + 4,
					 instant.phase * settings.width, 1);
	const text = "frame: " + (instant.fmod + instant.weight).toFixed(2);
	context.fillText(text, 0, settings.car_width + 20)
}

function draw() {
	// compute frame
	if(startTime < 0){
		startTime = new Date().getTime() / 1e3;
		document.getElementById("test-div").innerHTML = new Date();
	}
	const s = new Date().getTime() / 1e3 - startTime;
	const f = Math.floor(s * settings.fps);
	const weight = s * settings.fps - f;
	const fmod = f % (settings.frames - 1);
	const phase = (fmod + weight) / (settings.frames - 1);
	const instant = {fmod: fmod, weight: weight, phase: phase};

	// prepare canvas
	const canvas = document.getElementById("canvas");
	const context = canvas.getContext("2d");
	canvas.width = canvas.clientWidth;
	
	settings.width = canvas.width;
	settings.height = canvas.height;
	// as per http://stackoverflow.com/questions/15661339/how-do-i-fix-blurry-text-in-my-html5-canvas#15666143
	canvas.style.width = canvas.width;
	canvas.style.height = canvas.height;
	context.clearRect(0, 0, settings.width, settings.height);

	// draw stuff
	drawRoad(context, instant, settings);
	drawTime(context, instant, settings);
	cars.map(drawCar(context, instant, settings));
	
	// call self
	window.requestAnimationFrame(draw);
}

window.requestAnimationFrame(draw);
