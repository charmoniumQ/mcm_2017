var startTime = -1;

// utils
function last(arr) { return arr[arr.length - 1]; }

// Settings
const settings = {
	car: {
		color: "green",
		length: 4.5,
		width: 1.75,
		scale: true,
		// length: 30,
		// width: 20,
		// scale: false,
	},
	lane: {
		pad: 1.0,
		length: maxX,
		s: road.length,
	},
	text_color: "black",
	dt: dt,
	frames: road[0][0].length,
};

settings.lane.d = settings.lane.pad * 2 + settings.car.width;

// draw utilities
// function drawRoad(context, instant, settings) {
// 	context.fillStyle = settings.text_color;
// 	context.strokeRect(0, 0, settings.width, settings.car_width + 2);
// }

// function drawTime(context, instant, settings) {
// 	context.fillStyle = settings.text_color;
// 	context.fillRect(0, settings.car_width + 4,
// 	                 instant.phase * settings.width, 1);
// 	const text = "frame: " + (instant.fmod + instant.weight).toFixed(2);
// 	context.fillText(text, 0, settings.car_width + 20);
// }

function drawCar_(context, instant, settings, lane_i, car_i, x_) {
	const x = x_ * settings.scale
	const y = (settings.lane.d * lane_i + settings.lane.pad) * settings.scale;
	const dx = settings.car.length * (settings.car.scale ? settings.scale : 1);
	const dy = settings.car.width * (settings.car.scale ? settings.scale : 1);
	if (car_i == 0) {
		console.log(lane_i, y);
	}
	context.fillRect(x, y, dx, dy);
}

function carPosition(car, instant) {
	return  car[instant.fmod].x * (1 - instant.weight) +
	        car[instant.fmod + 1].x * instant.weight;
}

function drawCar(context, instant, settings, lane_i) {
	return function(car, car_i) {
		drawCar_(context, instant, settings, lane_i, car_i, carPosition(car, instant));
	};
}

function drawLane(context, instant, settings) {
	return function(lane, lane_i) {
		lane.map(drawCar(context, instant, settings, lane_i));
	};
}

function draw() {
	// compute frame
	if(startTime < 0){
		startTime = new Date().getTime() / 1e3;
		document.getElementById("test-div").innerHTML = new Date();
	}
	const s = new Date().getTime() / 1e3 - startTime;
	const f = Math.floor(s / settings.dt);
	const weight = s / settings.dt - f;
	const fmod = f % (settings.frames - 1);
	const phase = (fmod + weight) / (settings.frames - 1);
	const instant = {fmod: fmod, weight: weight, phase: phase};

	// prepare canvas
	const canvas = document.getElementById("canvas");
	const context = canvas.getContext("2d")
	canvas.width = canvas.clientWidth;
	canvas.height = settings.lane.d * settings.lane.s * settings.scale;
	console.log(canvas.width + ' x '+ canvas.height);
	settings.width = canvas.width;
	settings.height = canvas.height;
	// as per http://stackoverflow.com/questions/15661339/how-do-i-fix-blurry-text-in-my-html5-canvas#15666143
	canvas.style.width = canvas.width;
	canvas.style.height = canvas.height;
	settings.scale = canvas.width / (settings.lane.length + settings.car.length);
	context.clearRect(0, 0, settings.width, settings.height);

	// draw stuff
	//drawRoad(context, instant, settings);
	// drawTime(context, instant, settings);
	road.map(drawLane(context, instant, settings));
	
	// call self
	window.requestAnimationFrame(draw);
}

window.requestAnimationFrame(draw);
