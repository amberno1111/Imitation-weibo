var canvas = document.getElementById("canvas");
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    var ctx = canvas.getContext('2d');
    function rand(min, max) {
        return parseInt(Math.random()*(max - min) + min);
    }
    function Round() {
        /*半径*/
        this.r = rand(5, 15);
        var speed = rand(1, 3);
        this.speedX = rand(0, 4) > 2 ? speed: -speed;
        this.speedY = rand(0, 4) > 2 ? speed: -speed;
        var x = rand(this.r, canvas.width - this.r);
        this.x = x < this.r ? this.r : x;
        var y = rand(this.r, canvas.height - this.r);
        this.y = y < this.y ? this.r : y;
    }
    Round.prototype.draw = function () {
        ctx.fillStyle = 'rgba(200, 200, 200, 0.2)';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.r, 0, 2* Math.PI, true);
        ctx.closePath();
        ctx.fill();
    }
    Round.prototype.move = function () {
        this.x += this.speedX/10;
        if(this.x > canvas.width || this.x < 0){
            this.speedX *= -1;
        }
        this.y += this.speedY/10;
        if(this.y > canvas.height || this.y < 0){
            this.speedY *= -1;
        }
    }
    Round.prototype.links = function () {
        for(var loop = 0; loop < setBall.length; loop++){
            var len = Math.sqrt(((this.x - setBall[loop].x)*(this.x - setBall[loop].x)) + ((this.y-setBall[loop].y)*(this.y-setBall[loop].y)));
            var line = 1/len * 2;
            if(len < 250){
                ctx.beginPath();
                ctx.strokeStyle = 'rgba(0, 0, 0, '+ line + ')';
                ctx.moveTo(this.x, this.y);
                ctx.lineTo(setBall[loop].x, setBall[loop].y);
                ctx.stroke();
                ctx.closePath();
            }
        }
    }
    var setBall = [];
    function init() {
        for(var num = 0; num < 50; num++){
            var obj = new Round();
            obj.draw();
            obj.move();
            setBall.push(obj);
        }
    }
    function ballMove() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for(var i = 0; i < setBall.length; i++){
            var ball = setBall[i];
            ball.draw();
            ball.move();
            ball.links();
        }
        requestAnimationFrame(ballMove);
    }
    window.onload = function () {
        init();
        requestAnimationFrame(ballMove);
    }
