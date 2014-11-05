$(document).ready(function(){

	scene = {};

	$("#new-background").on('change.bs.fileinput', function(){
		// Background Attached
		var files = [this.files[0]];
		var file = files[0];

		var backgroundFr = new FileReader();
		backgroundFr.readAsDataURL(file);
		$("#new-background").replaceWith($("#new-background").val('').clone(true));
		$(".fileinput-filename").html("");
		
		var data = new FormData();
		$.each(files, function(key,value){
			data.append("background",value);
		});
		data.append("name", "testing the backgrond upload");
		data.append("description", "");
		
		$.ajax({
			type : "POST",
			url : "/api/backgrounds/",
			data : data,
			processData : false,
			contentType : false,
			enctype : 'multiplart/form-data',
			success : function(result){

				var background = result.background;

				var thumb = new Image();
				thumb.src = background.url;
				$(thumb).addClass("img-thumbnail").addClass("background-thumbnail");
				var thumbRow = $("<div></div>").append(thumb);
				$("#backgrounds").append(thumbRow);

				$(".background-thumbnail").dblclick(function(event){
					$.ajax({
						type : "POST",
						url : "/api/scenes/" + scene.id + "/background/set",
						data : JSON.stringify({ background : background.id }),
						success : function(result){
							var background = result.background;
							scene.background = background;
							console.log(background);
							$("#scene-background-image")[0].src = background.url;
							$("#scene-background-image").css("display", "block");
						},
						error : function(error){
							console.log("ERROR");
						}
					});
				});
			},
			error : function(error){
				// BAD
				console.log(error);
			}
		});
	});
	
	$("#new-prop").on('change.bs.fileinput', function(){
		// Prop Attached
		var files = [this.files[0]];
		var file = files[0];

		var propFr = new FileReader();
		propFr.readAsDataURL(file);
		$("#new-prop").replaceWith($("#new-prop").val('').clone(true));
		$(".fileinput-filename").html("");

		var data = new FormData();
		$.each(files, function(key,value){
			data.append("prop",value);
		});
		data.append("name", "testing the prop upload");
		data.append("description", "");
		
		$.ajax({
			type : "POST",
			url : "/api/props/",
			data : data,
			processData : false,
			contentType : false,
			enctype : 'multiplart/form-data',
			success : function(result){
				// GOOD
				var prop = result.prop;

				var thumb = new Image();
				thumb.src = prop.url;
				$(thumb).addClass("img-thumbnail").addClass("prop-thumbnail");
				var thumbRow = $("<div></div>").append(thumb);
				$("#props").append(thumbRow);

				$(".prop-thumbnail").dblclick(function(event){
					$.ajax({
						type : "POST",
						url : "/api/scenes/" + scene.id + "/props/add",
						data : JSON.stringify({ prop : prop.id }),
						success : function(result){
							var prop = result.prop;
							scene.props[prop.scene_prop_id] = prop;
							var image = new Image();
							image.src = prop.url;
							$(image).data("scene-prop-id", prop.scene_prop_id);
							image.draggable = true;
							$(image).addClass("prop");
							$(".scene-props").append(image);
						},
						error : function(error){
							console.log("ERROR");
						}
					});
				});
			},
			error : function(error){
				// BAD
				console.log("Failed to add prop")
			}
		})
	});

	var drag = false;
	var targ, coordX, coordY, offsetX, offsetY;
	var left, top, maxLeft, maxTop;

	function startDrag(e) {
		// determine event object
		if (!e) {
			var e = window.event;
		}
		// if(e.preventDefault) e.preventDefault();

		// IE uses srcElement, others use target
		targ = e.target ? e.target : e.srcElement;

		if (targ.className != 'prop') {return true;};
		// calculate event X, Y coordinates
		offsetX = e.clientX;
		offsetY = e.clientY;

		// assign default values for top and left properties
		if (!targ.style.left) { targ.style.left='0px'};
		if (!targ.style.top) { targ.style.top='0px'};

		// calculate integer values for top and left 
		// properties
		coordX = parseInt(targ.style.left);
		coordY = parseInt(targ.style.top);
		drag = true;

		// move div element
		document.onmousemove = dragDiv;
		return false;
	}

	function dragDiv(e) {
		if (!drag) { return; }
		if (!e) { var e = window.event; }
		// var targ=e.target?e.target:e.srcElement;
		// move div element
		left = coordX + e.clientX - offsetX;
		maxLeft = ($("#scene-background-image")[0].width || 1920) - targ.width;
		top = coordY + e.clientY - offsetY;
		maxTop = ($("#scene-background-image")[0].height || 1080) - targ.height;
		if (left < 0){
			targ.style.left = '0px';
		} else if (left > maxLeft){
			targ.style.left = maxLeft + 'px'
		} else {
			targ.style.left = left + 'px';
		}
		if (top < 0){
			targ.style.top = '0px';
		} else if (top > maxTop){
			targ.style.top = maxTop + 'px';
		} else {
			targ.style.top = top + 'px';
		}
		return false;
	}

	function stopDrag(e) {
		drag = false;

		if (!e) {  var e = window.event; }
		if (targ.className != 'prop') {return true;};
		var propLeft = parseInt(targ.style.left,10);
		var propTop = parseInt(targ.style.top,10);
		var scenePropId = $(targ).data("scene-prop-id");
		var update_data = JSON.stringify({
			update : {
				type : "PROP",
				scene_prop : scenePropId,
				position_x : propLeft,
				position_y : propTop
			}
		});
		$.ajax({
			type : "PUT",
			url : "/api/scenes/" + scene.id,
			data : update_data,
			success : function(result){
				// Saved
				scene.props[scenePropId].position_x = propLeft;
				scene.props[scenePropId].position_y = propTop;
			},
			error : function(error){
				console.log(error);
			}
		})
	}

	window.onload = function() {
		document.onmousedown = startDrag;
		document.onmouseup = stopDrag;
	}

	$("#create-new-scene-btn").click(function(event){
		var name = $("#new-scene-name").val();
		var description = $("#new-scene-description").val()
		$.ajax({
			type : "POST",
			url : "/api/scenes",
			data : JSON.stringify({
				name : name,
				description : description
			}),
			success : function(result){
				console.log(result);

				// Close Modal
				$(".scenemaker-fileinput .btn").removeClass("disabled");
				$("#new-prop, #new-background").attr("disabled", false);
				$("#new-scene-prompter").addClass("disabled");
				$("#new-scene-modal").modal("hide");
				$("#new-scene-form .form-control").val("");

				// Display Meta Info
				$("#save-scene").removeClass("disabled");
				var nameDiv = $("<div></div>").text("Name: " + name);
				var descDiv = $("<div></div>").text("Description: " + description);
				$("#scenes").append(nameDiv).append(descDiv);

				// Model
				scene = {
					id : result.scene.id,
					name : result.scene.name,
					description : result.scene.description,
					version : result.scene.version,
					background : {},
					background_scale : 1.0,
					props : {}
				}

				// Switch to Backgronds Tab now
				$(".full-tab.active").removeClass("active");
				$("#backgrounds-tab").parent().addClass("active");
				$(".tab-pane#scenes").removeClass("active").removeClass("in");
				$(".tab-pane#backgrounds").addClass("active").addClass("in");
			},
			error : function(error){
				console.log(error);
			}
		})
	});
});