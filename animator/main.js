var startTime = -1;

// Settings
const settings = {
	car: {
		color: {
			strat_optimal: 'yellow',
			strat_random: 'blue',
			strat_gipps: 'yellow',
			strat_gipps2: 'yellow',
			strat_idm: 'yellow',
			strat_leader: 'blue',
		},
		length: 4.5,
		width: 1.75,
		scale: true,
		// length: 30,
		// width: 20,
		// scale: false,
	},
	lane: {
		pad: 0.75,
		length: max_x,
		s: max_lane + 1,
	},
	text_color: "black",
	dt: dt,
	frames: road[0].length,
};

settings.lane.d = settings.lane.pad * 2 + settings.car.width;

function drawCar_(context, instant, settings, car, x_) {
	if (car.visible) {
		const x = x_ * settings.scale
		const y = (settings.lane.d * car.lane + settings.lane.pad) * settings.scale;
		const dx = settings.car.length * (settings.car.scale ? settings.scale : 1);
		const dy = settings.car.width * (settings.car.scale ? settings.scale : 1);
		context.beginPath();
		context.rect(x, y, dx, dy);
		context.fillStyle = settings.car.color[car.state];
		context.fill();
		context.lineWidth = 1;
		context.strokeStyle = 'black';
		context.stroke();
		context.fillStyle = 'black';
		// context.fillText(car.i, x + dx / 3, y + dy);
	}
}

function carPosition(car, instant) {
	return  (car[instant.fmod].x * (1 - instant.weight) +
	         car[instant.fmod + 1].x * instant.weight)
}

function drawCar(context, instant, settings) {
	return function(car) {
		drawCar_(context, instant, settings, car[instant.fmod], carPosition(car, instant));
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
	settings.width = canvas.width;
	settings.height = canvas.height;
	// as per http://stackoverflow.com/questions/15661339/how-do-i-fix-blurry-text-in-my-html5-canvas#15666143
	canvas.style.width = canvas.width;
	canvas.style.height = canvas.height;
	settings.scale = Math.max(canvas.width / (settings.lane.length + settings.car.length), 0);
	context.clearRect(0, 0, settings.width, settings.height);

	// draw stuff
	//drawRoad(context, instant, settings);
	// drawTime(context, instant, settings);
	road.map(drawCar(context, instant, settings));
	
	// call self
	window.requestAnimationFrame(draw);
}

window.requestAnimationFrame(draw);
