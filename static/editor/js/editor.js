$(document).ready(function(){

	// TODO - changeSceneThumbnail

	// Current Scene loaded in the Client Browser
	scene = {};

	// Viewport Adjusted Scale - Default to 1.0
	var adjustedScale = 1.0;

	// Save New Background to Server
	function newBackground(formData, addToScene){
		$.ajax({
			type : "POST",
			url : "/api/backgrounds/",
			data : formData,
			processData : false,
			contentType : false,
			enctype : 'multiplart/form-data',
			success : function(result){
				// Show that New Background Was Uploaded to Server
				newBackgroundThumbnail(result.background);
				if (scene.hasOwnProperty("id") && addToScene){
					// Set Current Scene Background using Background Data Model Representation
					setBackground(result.background);
				}
			},
			error : function(error){
				// BAD
				console.log(error.statusText);
			}
		});
	}

	// Show that New Background Was Uploaded to Server
	function newBackgroundThumbnail(background){

		// Create a Thumbnail
		var thumb = new Image();
		thumb.crossOrigin = "Anonymous";
		thumb.src = background.url || "/media/default/question-mark.jpg";
		$(thumb).addClass("img-thumbnail").addClass("background-thumbnail").data("background", background);

		// Create a New Row in the Background Collection
		var thumbElement = $("<span></span>").append(thumb).data("background", background);
		
		// Add Thumbnail to Backgrounds
		$("#background-collection").append(thumbElement);

		// Event Listener for Background Thumbnail - Selection / Set
		$(thumb).dblclick(function(event){
			if (!scene.hasOwnProperty("id")){
				// Scene Must be Set First
				return false;
			}
			// Set Current Scene Background using Background Data Model Representation
			setBackground(background);
		});
	}

	// Set Current Scene Background using Background Dat Model Representation
	function setBackground(background){
		$.ajax({
			// TODO Scene Thumbnail
			type : "POST",
			url : "/api/scenes/" + scene.id + "/background/set",
			data : JSON.stringify({ background : background.id }),
			success : function(result){
				
				// Set Client Model Scene's Background
				var background = result.background;
				scene.background = background;

				// Set Current Scene's Background in the DOM
				renderBackgroundView(background);

				// Update Client Scene Thumbnail
				changeSceneThumbnail(scene);

				// Update Editor Menu
				changeEditorMenu();
			},
			error : function(error){
				// BAD
				console.log(error.statusText);
			}
		});
	}

	// Set Current Scene's Background in the DOM
	function renderBackgroundView(background){

		$("#scene-background-image")
			.attr("src", background.url || "")
			.css("display", "block")
			.attr("draggable", false);
		var tempBackground = new Image();
		tempBackground.crossOrigin = "Anonymous";
		tempBackground.onload = function(){
			scene.background.originalWidth = tempBackground.width;
			scene.background.originalHeight = tempBackground.height;
			var width = scene.background_scale * scene.background.originalWidth * adjustedScale;
			var height = scene.background_scale * scene.background.originalHeight * adjustedScale;
			$("#scene-background-image").width(width).height(height);
		}
		tempBackground.src = background.url || "";
	}

	// Save New Prop to Server
	function newProp(formData, addToScene){
		$.ajax({
			type : "POST",
			url : "/api/props/",
			data : formData,
			processData : false,
			contentType : false,
			enctype : 'multiplart/form-data',
			success : function(result){
				newPropThumbnail(result.prop);
				if (scene.hasOwnProperty("id") && addToScene){
					// Add prop to scene
					addProp(result.prop);
				}
			},
			error : function(error){
				// BAD
				console.log(error.statusText);
			}
		});
	}

	// Show that New Prop was Uploaded to Server
	function newPropThumbnail(prop){

		var thumb = new Image();
		thumb.crossOrigin = "Anonymous";
		thumb.src = prop.url || "/media/default/question-mark.jpg";
		$(thumb).addClass("img-thumbnail").addClass("prop-thumbnail").data("prop", prop);
		var thumbContainer = $("<span></span>").append(thumb).data("prop", prop);
		$("#props-collection").append(thumbContainer);

		$(thumb).dblclick(function(event){
			if (!scene.hasOwnProperty("id") || scene.background.url === ""){
				// Scene Must be Set First
				return false;
			}
			addProp(prop);
		});
	}

	// Add Prop to Current Scene on Server
	function addProp(prop){
		$.ajax({
			// TODO Scene Thumbnail
			type : "POST",
			url : "/api/scenes/" + scene.id + "/props/add",
			data : JSON.stringify({ prop : prop.id }),
			success : function(result){
				scene.props[result.prop.scene_prop_id] = result.prop;
				renderPropView(result.prop)
				changeSceneThumbnail(scene);
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	// Remove Prop from Current Scene on Server
	function removeProp(scene_prop_id){
		$.ajax({
			// TODO Scene Thumbnail
			type : "DELETE",
			url : "/api/scenes/props/" + scene_prop_id,
			success : function(result){
				if (result.success){
					
					// Remove from scene model
					for (var i in scene.props){
						if (scene.props[i].scene_prop_id === scene_prop_id){
							delete scene.props[i];
							break;
						}
					}
					
					// remove thumbnail from editor
					changeEditorMenu();

					// update scene view and thumbnail
					renderSceneView();
					changeSceneThumbnail(scene);
				}
			},
			error : function(error){
				console.log(error.statusText);
			}
		})
	}

	// Add Prop to Current Scene in the DOM
	function renderPropView(prop){
		if (!prop){
			return false;
		}
		var image = new Image();
		image.crossOrigin = "Anonymous";
		image.onload = function(){
			$(image).data("scene-prop", prop);
			image.draggable = true;
			$(image).addClass("prop");

			prop.originalWidth = image.width;
			prop.originalHeight = image.height;

			var offset = $("#scene-background-image").offset();
			var left = Math.floor((prop.position_x || 0) * adjustedScale + offset.left);
			var top = Math.floor((prop.position_y || 0) * adjustedScale + offset.top);

			// Scaling
			image.width = prop.originalWidth * prop.scale * adjustedScale;
			image.height = prop.originalHeight * prop.scale * adjustedScale;

			$("#scene").append(image);

			// Position
			$(image).offset({
				left : left,
				top : top
			});
			$(image).css({
				"z-index" : 4000 - prop.index // z
			});

			changeEditorMenu();
		}
		image.src = prop.url || "";
	}

	// Update Prop Position on Server
	function moveProp(id, update){
		$.ajax({
			// TODO Scene Thumbnail
			type : "PUT",
			url : "/api/scenes/" + scene.id,
			data : JSON.stringify(update),
			success : function(result){
				// Saved
				scene.props[id].position_x = update.update.position_x;
				scene.props[id].position_y = update.update.position_y;
				changeSceneThumbnail(scene);
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	// Save New Scene on Server
	function newScene(name, description){
		$.ajax({
			// TODO Scene Thumbnail
			// SPECIAL
			type : "POST",
			url : "/api/scenes",
			data : JSON.stringify({
				name : name,
				description : description
			}),
			success : function(result){
				newSceneView(result.scene);
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	// Show that New Scene was Created on Server
	function newSceneView(new_scene){

		// Close Modal
		$("#new-scene-modal").modal("hide");
		$("#new-scene-form .form-control").val("");

		// Model
		scene = {
			id : new_scene.id,
			name : new_scene.name,
			description : new_scene.description,
			background : {},
			background_scale : 1.0,
			props : {}
		}

		// View
		clearSceneView();

		// Thumbnail
		addSceneThumbnail(new_scene);

		// Update Editor Menu
		changeEditorMenu();

		// Switch to Editor Menu
		$("#editor-tab").tab("show");

	}

	function addSceneThumbnail(scene){

		// Create Thumbnail
		createSceneThumbnailImage(scene, function(thumb){
			// Create a New Row in the Background Collection
			$(thumb).addClass("img-thumbnail").addClass("scene-thumbnail");
			var thumbElement = $("<span></span>").addClass("scene-thumbnail-element").append(thumb).data("scene", scene);
			$(thumb).data("scene", scene);
			
			// Add Thumbnail to Backgrounds
			$("#scene-collection").append(thumbElement);

			// Event Listener for Background Thumbnail - Selection / Set
			$(thumb).dblclick(function(event){
				// Set Current Scene using Scene Data Model Representation
				changeScene(scene);
			});
		});
	}

	function changeSceneThumbnail(scene){

		createSceneThumbnailImage(scene, function(thumb){
			// Change Thumbnail
			$(".scene-thumbnail").filter(function(){
				return $(this).data("scene").id === scene.id;
			}).attr("src", thumb.src);
			updateSceneModelThumbnail(scene, thumb);
		});
	}

	function updateSceneModelThumbnail(scene, thumb){
		$.ajax({
			type : "PUT",
			url : "/api/scenes/" + scene.id,
			data : JSON.stringify({
				"update" : {
					"type" : "SCENE",
					"thumbnail" : thumb.src.split(',')[1]
				}
			}),
			success : function(result){
				if (!result.success){
					console.log("Unable to save scene thumbnail");
				}
			},
			error : function(error){
				console.log(error.statusText);
			}
		})
	}

	function createSceneThumbnailImage(scene, callback){
		
		// Create Temporary Canvas
		var canvas = $("<canvas></canvas>")[0];
		var width = 128;
		var height = 72;
		canvas.width = width;
		canvas.height = height;
		var thumbScale = height / 1080;
		var ctx = canvas.getContext('2d');

		// Create a Thumbnail
		var thumb = new Image();
		thumb.crossOrigin = "Anonymous";

		// Draw Background
		var backgroundImage = new Image();
		backgroundImage.crossOrigin = "Anonymous";
		backgroundImage.onload = function(){
			backgroundImage.width *= scene.background_scale * thumbScale;
			backgroundImage.height *= scene.background_scale * thumbScale;
			ctx.drawImage(this, 0, 0, backgroundImage.width, backgroundImage.height);
			multiplePropThumbnailLoader(scene.props, propsLoaded);
		}
		backgroundImage.src = scene.background.url || "/static/editor/img/blank-background.jpg";

		function propsLoaded(propImages){
			for (var i in propImages){
				var prop = propImages[i].prop;
				var image = propImages[i].image;
				var left = prop["position_x"] * thumbScale;
				var top = prop["position_y"] * thumbScale;
				image.width *= prop["scale"] * thumbScale;
				image.height *= prop["scale"] * thumbScale;
				ctx.drawImage(image, left, top, image.width, image.height);
			}
			var imageDataURL = canvas.toDataURL();
			var onLoad = function(e){
				thumb.removeEventListener("load", onLoad);
				callback(thumb);
			}
			thumb.addEventListener("load", onLoad, false);
			thumb.src = imageDataURL;
		}
	}

	// Change Scene Client Model
	function changeScene(new_scene){
		scene = new_scene;
		renderSceneView();
	}

	// Change Scene in the DOM
	function renderSceneView(){
		var background = scene.background;
		var props = scene.props;
		clearSceneView();
		renderBackgroundView(background);
		for (var i in props){
			var prop = props[i];
			scene.props[prop.scene_prop_id] = prop;
			renderPropView(prop);
		}

		// Update Editor
		changeEditorMenu();
		return true;
	}

	// Resets Scene to Empty View
	function clearSceneView(){
		$("#scene-background-image").width(0);
		$("#scene-background-image").height(0);
		$("#scene-background-image").attr("src", null);
		$(".prop").remove()
		return true;
	}

	// Update Editor Menu With Current Scene
	function changeEditorMenu(){

		scene = scene || {};

		// Change Metadata
		$("#editor-scene-name-value").text(scene.name || "");
		$("#editor-scene-description-value").text(scene.description || "");
		scene.id ? $("#edit-scene-btn").removeClass("disabled") : $("#edit-scene-btn").addClass("disabled");
		scene.id ? $("#delete-scene-btn").removeClass("disabled") : $("#delete-scene-btn").addClass("disabled");
		scene.id ? $(".new-asset-btn-group").removeClass("disabled") : $(".new-asset-btn-group").addClass("disabled");
		$("#add-background-label").text(scene.id ? "Change Background" : "Add Background");
		
		// Change Background
		$("#editor-background .background-thumbnail")
			.attr("src", (scene.background && scene.background.url) || "/static/editor/img/blank-background.jpg")
			.attr("data-toggle", "modal")
			.attr("data-target", "#background-modal")
			.click(function(event){
				if (!scene.background || !scene.background.url || scene.background.url === ""){
					return false;
				}
			});
		
		// Change Props
		$("#editor-props").html("");
		$.each(scene.props || [], function(i,prop){
			if (!prop.url){
				return false;
			}
			var propImage = new Image();
			propImage.crossOrigin = "Anonymous";
			propImage.src = prop.url;
			$(propImage).addClass("img-thumbnail")
				.addClass("prop-thumbnail")
				.attr("data-toggle", "modal")
				.attr("data-target", "#prop-modal")
				.data("prop", prop)
			$("#editor-props").append(propImage);
		});
	}

	function updateMetadata(data){
		$.ajax({
			type : "PUT",
			url : "/api/scenes/" + scene.id,
			data : JSON.stringify(data),
			success : function(result){
				updateMetadataModel(data.update)
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	function updateMetadataModel(update){
		if (update.hasOwnProperty("name")){
			scene.name = update["name"]; // Model
			$("#editor-scene-name-value").text(update["name"]); // View
		}
		if (update.hasOwnProperty("description")){
			scene.description = update["description"]; // Model
			$("#editor-scene-description-value").text(update["description"]); // View
		}
	}

	function updateBackground(data){
		$.ajax({
			// TODO Scene Thumbnail
			// Special
			type : "PUT",
			url : "/api/scenes/" + scene.id,
			data : JSON.stringify(data),
			success : function(result){
				updateBackgroundModel(data.update);
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	function updateBackgroundModel(update){
		if (update.hasOwnProperty("background_scale")){
			
			// Update Client Model
			scene.background_scale = update["background_scale"];

			// Get Original Dimensions
			var tempBackground = new Image();
			tempBackground.crossOrigin = "Anonymous";
			tempBackground.src = scene.background.url || "/static/editor/img/blank-background.jpg";
			var width = tempBackground.width;
			var height = tempBackground.height;

		}
		renderSceneView();
		changeSceneThumbnail(scene);
	}

	function updateSceneProp(data){
		$.ajax({
			// TODO Scene Thumbnail
			// Special
			type : "PUT",
			url : "/api/scenes/" + scene.id,
			data : JSON.stringify(data),
			success : function(result){
				updateScenePropModel(data.update);
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	function updateScenePropModel(update){
		if (!update.hasOwnProperty("scene_prop")){
			return false;
		}
		var sceneProp = scene.props[update["scene_prop"]];
		if (update.hasOwnProperty("scale")){
			sceneProp.scale = update["scale"];
		}
		if (update.hasOwnProperty("index")){
			sceneProp.index = update["index"];
		}
		if (update.hasOwnProperty("rotation")){
			sceneProp.rotation = update["rotation"];
		}
		renderSceneView();
		changeSceneThumbnail(scene);
	}

	function deleteScene(){
		$.ajax({
			type : "DELETE",
			url : "/api/scenes/" + scene.id,
			success : function(result){
				if (result.success){
					deleteSceneView(scene.id);
				}
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	function deleteSceneView(scene_id){
		
		// Clear Scene View
		clearSceneView();

		// Remove From Scenes Tab
		$(".scene-thumbnail-element").filter(function(){
			return $(this).data("scene").id === scene_id;
		}).remove();

		// Update Model
		scene = {};

		// Update Editor Menu
		changeEditorMenu();

	}

	// CLIENT EVENTS //

	// Drag Event Listener
	window.onload = function() {
		document.onmousedown = startDrag;
		document.onmouseup = stopDrag;
	}

	function adjustSceneDimension(){
		var newWidth = $("#scene-container").width() - 12;
		var newHeight = $("#scene-container").height() - 12;
		var ratio = newWidth / newHeight;
		var desiredRatio = 16/9;
		var adjustedWidth = newWidth;
		var adjustedHeight = newHeight;
		if (ratio < desiredRatio){
			// Too Tall
			adjustedHeight = newWidth / desiredRatio;
			adjustedWidth = newWidth;
		}
		else if (ratio > desiredRatio){
			// Too Wide
			adjustedWidth = newHeight * desiredRatio;
			adjustedHeight = newHeight;
		}

		// Set Adjusting Scale
		adjustedScale = adjustedWidth / 1920;

		// Adjust Scene Div
		$("#scene").width(adjustedWidth).height(adjustedHeight);
		var newBottom = $("#collections").height();
		$("#scene-row").css({ "bottom" : newBottom });
		
		// Adjust Scene Background Image
		var originalWidth, originalHeight;
		if (scene.background){
			originalWidth = scene.background.originalWidth || 0;
			originalHeight = scene.background.originalHeight || 0;
		}
		var backgroundWidth = scene.background_scale * originalWidth * adjustedScale;
		var backgroundHeight = scene.background_scale * originalHeight * adjustedScale;
		$("#scene-background-image").width(backgroundWidth).height(backgroundHeight);

		// Adjust Scene Prop Images
		var offset = $("#scene-background-image").offset();
		for (var i in scene.props || []){
			var originalWidth, originalHeight;
			var prop = scene.props[i];
			originalWidth = prop.originalWidth || 0;
			originalHeight = prop.originalHeight || 0;
			var propWidth = (prop.scale || 1) * originalWidth * adjustedScale;
			var propHeight = (prop.scale || 1) * originalHeight * adjustedScale;
			var left = Math.floor((prop.position_x || 0) * adjustedScale + offset.left);
			var top = Math.floor((prop.position_y || 0) * adjustedScale + offset.top);
			$(".prop").filter(function(){
				return $(this).data("scene-prop").scene_prop_id === prop.scene_prop_id;
			}).width(propWidth).height(propHeight).offset({ left : left, top : top });

		}
	}

	// Dynamic Scene View Adjuster
	$(window).resize(function(e){
		adjustSceneDimension();
	});

	// Drag Event Listener Helpers

	// Drag Event Variables
	var drag = false;
	var targ, startX, startY, startLeft, startTop;
	var left, top;

	// Start Drag Event Hanlder
	function startDrag(e) {
		// determine event object
		if (!e) {
			var e = window.event;
		}
		// if(e.preventDefault) e.preventDefault();

		// IE uses srcElement, others use target
		targ = e.target ? e.target : e.srcElement;

		if (targ.className != 'prop') {return true;};

		// assign default values for top and left properties
		if (!targ.style.left) { targ.style.left='0px'};
		if (!targ.style.top) { targ.style.top='0px'};

		// calculate integer values for top and left 
		// properties
		startX = e.clientX;
		startY = e.clientY;
		drag = true;

		// Where image was clicked
		var offset = $(targ).offset();
		startLeft = offset.left;
		startTop = offset.top;

		// move div element
		document.onmousemove = dragDiv;
		return false;
	}

	// Draggig Event Handler
	function dragDiv(e) {
		if (!drag) { return; }
		if (!e) { var e = window.event; }
		// var targ = e.target ? e.target : e.srcElement;
		// move div element
		var dx = e.clientX - startX;
		var dy = e.clientY - startY;
		left = startLeft + dx;
		top = startTop + dy;

		var sceneOffset = $("#scene-background-image").offset();
		var minLeft = sceneOffset.left;
		var maxLeft = 1920*adjustedScale - targ.width + sceneOffset.left;
		var minTop = sceneOffset.top;
		var maxTop = 1080*adjustedScale - targ.height + sceneOffset.top;

		if (left < minLeft){
			$(targ).offset({ left : minLeft });
		} else if (left > maxLeft){
			$(targ).offset({ left : maxLeft });
		} else {
			$(targ).offset({ left : left });
		}

		if (top < minTop){
			$(targ).offset({ top : minTop });
		} else if (top > maxTop){
			$(targ).offset({ top : maxTop });
		} else {
			$(targ).offset({ top : top });
		}

		return false;
	}

	// Stop Drag Event Handler
	function stopDrag(e) {
		drag = false;

		if (!e) {  var e = window.event; }
		if (targ.className != 'prop') {return true;};

		var propOffset = $(targ).offset();
		var sceneOffset = $("#scene-background-image").offset();
		var propLeft = parseInt((propOffset.left - sceneOffset.left)/adjustedScale, 10);
		var propTop = parseInt((propOffset.top - sceneOffset.top)/adjustedScale, 10);
		var scenePropId = $(targ).data("scene-prop").scene_prop_id;
		var update_data = {
			update : {
				type : "PROP",
				scene_prop : scenePropId,
				position_x : propLeft,
				position_y : propTop
			}
		};
		moveProp(scenePropId, update_data);
	}

	// New Scene Event Listener
	$("#create-new-scene-btn").click(function(event){
		
		// Get Metadata
		var name = $("#new-scene-name").val();
		var description = $("#new-scene-description").val();
		
		// Create New Scene on Server
		newScene(name, description);
	});

	// Background Image Uploaded Event Listener
	$("#new-background").on('change.bs.fileinput', function(){

		// Get File
		var files = [this.files[0]];
		var file = files[0];

		// Read File
		var backgroundFr = new FileReader();
		backgroundFr.readAsDataURL(file);

		// Reset Upload Tool (Blank)
		$("#new-background").replaceWith($("#new-background").val('').clone(true));
		
		// Create New Form with Background Image
		var data = new FormData();
		$.each(files, function(key,value){
			data.append("background",value);
		});

		// Background Image Metadata - TODO
		data.append("name", "BACKGROUND_NAME");
		data.append("description", "BACKGROUND_DESCRIPTION");
		
		// Save New Background to Server
		newBackground(data, false);
	});

	// Prop Image Uploaded Event Listener
	$("#new-prop").on('change.bs.fileinput', function(){
		
		// Get File
		var files = [this.files[0]];
		var file = files[0];

		// Read File
		var propFr = new FileReader();
		propFr.readAsDataURL(file);

		// Reset Upload Tool (Blank)
		$("#new-prop").replaceWith($("#new-prop").val('').clone(true));

		// Create New Form with Prop Image
		var data = new FormData();
		$.each(files, function(key,value){
			data.append("prop",value);
		});

		// Prop Image Metadata - TODO
		data.append("name", "SCENEPROP_NAME");
		data.append("description", "SCENEPROP_DESCRIPTION");

		newProp(data, false);
	});

	// Background Image Uploaded and Add Event Listener
	$("#upload-add-background").on('change.bs.fileinput', function(){

		// Get File
		var files = [this.files[0]];
		var file = files[0];

		// Read File
		var backgroundFr = new FileReader();
		backgroundFr.readAsDataURL(file);

		// Reset Upload Tool (Blank)
		$("#upload-add-background").replaceWith($("#upload-add-background").val('').clone(true));
		
		// Create New Form with Background Image
		var data = new FormData();
		$.each(files, function(key,value){
			data.append("background",value);
		});

		// Background Image Metadata - TODO
		data.append("name", "BACKGROUND_NAME");
		data.append("description", "BACKGROUND_DESCRIPTION");
		
		// Save New Background to Server
		newBackground(data, true);
	});

	// Prop Image Uploaded Event Listener
	$("#upload-add-prop").on('change.bs.fileinput', function(){
		
		// Get File
		var files = [this.files[0]];
		var file = files[0];

		// Read File
		var propFr = new FileReader();
		propFr.readAsDataURL(file);

		// Reset Upload Tool (Blank)
		$("#upload-add-prop").replaceWith($("#upload-add-prop").val('').clone(true));

		// Create New Form with Prop Image
		var data = new FormData();
		$.each(files, function(key,value){
			data.append("prop",value);
		});

		// Prop Image Metadata - TODO
		data.append("name", "SCENEPROP_NAME");
		data.append("description", "SCENEPROP_DESCRIPTION");

		newProp(data, true);
	});

	// Modal Event Listeners
	$("#metadata-modal").on("show.bs.modal", function(event){
		$("#edit-metadata-name").val(scene.name);
		$("#edit-metadata-description").val(scene.description);
	});

	$("#background-modal").on("show.bs.modal", function(event){
		$("#edit-background-scale").val(scene["background_scale"]);
	});

	$("#prop-modal").on("show.bs.modal", function(event){
		var element = event.relatedTarget;
		var prop = $(element).data("prop");
		$("#update-prop-btn").data("prop", prop);
		$("#remove-prop-btn").data("prop", prop);
		// Load Modal Based on Prop
		$("#edit-prop-scale").val(prop.scale);
		$("#edit-prop-index").val(prop.index);
		$("#edit-prop-index-value").text($("#edit-prop-index").val());
	});

	$("#update-metadata-btn").click(function(event){
		var data = {
			"update" : {
				"type" : "META",
				"name" : $("#edit-metadata-name").val(),
				"description" : $("#edit-metadata-description").val()
			}
		}
		updateMetadata(data);
	});

	$("#update-background-btn").click(function(event){
		var data = {
			"update" : {
				"type" : "BACKGROUND",
				"background_scale" : parseFloat($("#edit-background-scale").val())
			}
		}
		updateBackground(data);
	});

	$("#update-prop-btn").click(function(event){
		var prop = $(this).data("prop");
		var data = {
			"update" : {
				"type" : "PROP",
				"scene_prop" : prop.scene_prop_id,
				"scale" : parseFloat($("#edit-prop-scale").val()),
				"index" : parseInt($("#edit-prop-index").val(), 10),
				"rotation" : parseFloat($("#edit-prop-rotation").val() || "0.0"),
			}
		}
		updateSceneProp(data);
	});

	$("#remove-prop-btn").click(function(event){
		var prop = $(this).data("prop");
		removeProp(prop.scene_prop_id || "");
	});

	$("#delete-scene-btn-action").click(function(event){
		deleteScene();
	});

	// Helper Functions and Event Listeners
	$('.float-input').keypress(function(event) {
		if ((event.which != 46 || $(this).val().indexOf('.') != -1) && 
			(event.which < 48 || event.which > 57) || 
			(event.which == 46 && $(this).caret().start == 0)) {
			event.preventDefault();
			return false;
		}

		// this part is when left part of number is deleted and leaves a . in the leftmost position. For example, 33.25, then 33 is deleted
		$('.float-input').keyup(function(event) {
			if ($(this).val().indexOf('.') == 0) {
				$(this).val($(this).val().substring(1));
			}
		});
	});

	function multiplePropThumbnailLoader(props, callback){
		if (!props){
			return;
		}
		if ("undefined" === Object.keys(props).length){
			props = [props];
		}
		var count = Object.keys(props).length;
		var propImages = [];
		if (count === 0){
			return callback(propImages);
		}
		$.each(props, function(i,prop){
			var img = new Image();
			img.crossOrigin = "Anonymous";
			var propImage = {
				prop : prop,
				image : img
			};

			img.onload = function(){
				propImages.push(propImage);
				count--;
				if (count === 0){
					callback(propImages);
				}
			}
			img.src = prop.url || "";
		});
	}

	function imageDataToFileBlob(data){
		var png = data.split(',')[1];
		var file = new Blob([window.atob(png)],  {type: 'image/png', encoding: 'utf-8'});

		var fr = new FileReader();
		fr.onload = function(e){
			var v = e.target.result.split(',')[1]; // encoding is messed up here, so we fix it
			v = atob(v);
			var good_b64 = btoa(decodeURIComponent(escape(v)));
			document.getElementById("uploadPreview").src = "data:image/png;base64," + good_b64;
		}
		fr.readAsDataURL(file);
	}

	// Slider Displays Value
	$(".slider").on("input", function(event){
		var self = this;
		$(".slider-value").text($(self).val());
	});

	// Initializtion

	// Load All Scenes
	$.ajax({
		type: "GET",
		url: "/api/scenes",
		success: function(result){
			var scenes = result.scenes;
			for (var i in scenes){
				var load_scene = scenes[i];
				var props_array = load_scene.props;
				load_scene.props = {};
				for (var j in props_array){
					var prop = props_array[j];
					load_scene.props[prop.scene_prop_id] = prop;
				}
				scenes[load_scene.id] = load_scene;
				addSceneThumbnail(load_scene);
			}
		}
	});

	// Load All Backgrounds
	$.ajax({
		type: "GET",
		url: "/api/backgrounds",
		success: function(result){
			var backgrounds = result.backgrounds;
			for (var i in backgrounds){
				var background = backgrounds[i];
				newBackgroundThumbnail(background);
			}
		}
	});

	// Load All Props
	$.ajax({
		type: "GET",
		url: "/api/props",
		success: function(result){
			var props = result.props;
			for (var i in props){
				var prop = props[i];
				newPropThumbnail(prop);
			}
		}
	});

	adjustSceneDimension();
});