/*
 * View model for OctoPrint-Print-Queue
 *
 * Author: Michael New
 * License: AGPLv3
 */
const svg=' <?xml version="1.0" encoding="UTF-8" standalone="no"?><svg   xmlns:dc="http://purl.org/dc/elements/1.1/"   xmlns:cc="http://creativecommons.org/ns#"   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"   xmlns:svg="http://www.w3.org/2000/svg"   xmlns="http://www.w3.org/2000/svg"   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"   width="8.0506573mm"   height="5.1754222mm"   viewBox="0 0 8.0506573 5.1754222"   version="1.1"   id="svg8"   inkscape:version="1.0.2 (e86c870879, 2021-01-15)"   sodipodi:docname="drawing.svg">  <defs     id="defs2" />  <sodipodi:namedview     id="base"     pagecolor="#ffffff"     bordercolor="#666666"     borderopacity="1.0"     inkscape:pageopacity="0.0"     inkscape:pageshadow="2"     inkscape:zoom="7.1574975"     inkscape:cx="35.5073"     inkscape:cy="22.824451"     inkscape:document-units="mm"     inkscape:current-layer="layer1"     inkscape:document-rotation="0"     showgrid="false"     inkscape:window-width="1530"     inkscape:window-height="991"     inkscape:window-x="26"     inkscape:window-y="23"     inkscape:window-maximized="0" />  <metadata     id="metadata5">    <rdf:RDF>      <cc:Work         rdf:about="">        <dc:format>image/svg+xml</dc:format>        <dc:type           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />        <dc:title></dc:title>      </cc:Work>    </rdf:RDF>  </metadata>  <g     inkscape:label="Layer 1"     inkscape:groupmode="layer"     id="layer1"     transform="translate(-10,-10)">    <rect       style="fill:#999999;stroke-width:0.0124756"       id="rect833"       width="1.5335305"       height="1.5335305"       x="11.226084"       y="11.717759" />    <rect       style="fill:#999999;stroke-width:0.0124756"       id="rect833-6"       width="1.5335305"       height="1.5335305"       x="13.142997"       y="11.717759" />    <rect       style="fill:#999999;stroke-width:0.0124756"       id="rect833-6-7"       width="1.5335305"       height="1.5335305"       x="15.05991"       y="11.717759" />    <rect       style="fill:#999999;stroke-width:0.0124756"       id="rect833-5"       width="1.5335305"       height="1.5335305"       x="11.226084"       y="13.634672" />    <rect       style="fill:#999999;stroke-width:0.0124756"       id="rect833-6-3"       width="1.5335305"       height="1.5335305"       x="13.142997"       y="13.634672" />    <rect       style="fill:#999999;stroke-width:0.0124756"       id="rect833-6-7-5"       width="1.5335305"       height="1.5335305"       x="15.05991"       y="13.634672" />  </g></svg>'
$(function() {
	function ContinuousPrintViewModel(parameters) {
		var self = this;
		self.params = parameters;
		self.printerState = parameters[0];
		self.loginState = parameters[1];
		self.files = parameters[2];
		self.settings = parameters[3];
		self.is_paused = ko.observable();
		self.is_looped = ko.observable();
		self.ncount=1;
		self.itemsInQueue=0;
        
		self.onBeforeBinding = function() {
			self.loadQueue();
			self.is_paused(false);
			self.checkLooped();
            
		}
		self.files.addtoqueue = function(data) {
			var sd="true";
			if(data.origin=="local"){
			 sd="false";
			}
			data.sd=sd;
			self.addToQueue({
			 name:data.name,
			 path:data.path,
			 sd:sd,
			 //printArea:data.printsrea,
			 count:1
			});
		}
		
		self.loadQueue = function() {
            		$('#queue_list').html("");
			$.ajax({
				url: "plugin/continuousprint/queue",
				type: "GET",
				dataType: "json",
				headers: {
					"X-Api-Key":UI_API_KEY,
				},
				success:function(r){
                   		 self.itemsInQueue=r.queue.length;
					if (r.queue.length > 0) {
						$('#queue_list').html("");
						for(var i = 0; i < r.queue.length; i++) {
							var file = r.queue[i];
							var row;

                            if (i == 0) {other = "";}
                            if (i == 1) {other = "<i style='cursor: pointer' class='fa fa-chevron-down' data-index='"+i+"'></i>&nbsp;";}
                            row = $("<div class='n"+i+"' style='padding: 10px;border-bottom: 1px solid #000;"+(i==0 ? "background: #f9f4c0;" : "background: white;")+"'><div class='queue-row-container'><div class='queue-inner-row-container'><input class='fa fa-text count-box' type = 'number' data-index='"+i+"' value='" + file.count + "'/><p class='file-name' > " + file.name + "</p></div><div>" + other + "<i style='cursor: pointer' class='drag' data-index='"+i+"'>"+svg+"</i><i style='cursor: pointer' class='fa fa-minus text-error' data-index='"+i+"'></i></div></div></div>");
                            row.find('.drag').mousedown(function(i){
                            	pNode=this.parentNode.parentNode.parentNode
				if (pNode.style.translate.replace(' ','').length>3){
					pNode.pos={
						x:i.originalEvent.clientX-pNode.style.translate.toString().split(' ')[0].replace('px','')-1+1,
						y:i.originalEvent.clientY-pNode.style.translate.toString().split(' ')[1].replace('px','')-1+1,
					}
				}
				else{
					pNode.pos={
						x:i.originalEvent.clientX,
						y:i.originalEvent.clientY,
					}
				}
				if((i.originalEvent.clientY-pNode.pos.y+pNode.offsetTop)>=pNode.parentNode.offsetTop+64){
					pNode.clicked=true;
				}
		               
		                	
                            	//console.log("click")
                            });
                            
                            row.find('.drag').mousemove(function(i){
                            	pNode=this.parentNode.parentNode.parentNode
                            	if(pNode.clicked&&(i.originalEvent.clientY-pNode.pos.y+pNode.offsetTop)>pNode.parentNode.offsetTop+64){
                            		pNode.style.translate="0px "+(i.originalEvent.clientY-pNode.pos.y)+"px";
                            		pNode.style.opacity=0.5;
                            	}
                            	//console.log(i)
                            	//console.log("move")
                            });
                            row.find('.drag').mouseup(function(i){
                            		pNode=this.parentNode.parentNode.parentNode
                            		console.log('up')
                            		if(pNode.clicked){
		                    		pNode.clicked=false;
		                    		pNode.style.opacity=1;
		                    		let pos=Math.round((i.originalEvent.clientY-pNode.pos.y)/64)
		                    		pNode.style.translate="0px "+pos*64+"px";
		                    		pNode.ytran=pos*64;
		                    		fromindex=$(pNode).children(".queue-row-container").children(".queue-inner-row-container").children('.fa-text').data("index")-1+1;
		                    		//if(!pNode.offset){
		                    		//	pNode.offset=0;
		                    		//}

		                    		//if(pos+pNode.offset!=0){
		                    	//		let tmpofs=pNode.offset
				            		//for(var f=0;f<pNode.parentNode.childNodes.length;f++){
				            			
				            		//}

				          //  		console.log("pnode-offset="+pNode.offset)
				            //		console.log("tmpofs="+tmpofs)
				            //		console.log("fromindex="+fromindex)
				            //		console.log("pos=="+pos)
				            //		self.movePos(fromindex,fromindex+pos-pNode.offset);
				            		
				            		
		                    		//}
						//pNode.offset=pos;
                            		}
                            		
                            		//console.log(i)
                            		//console.log("up")
                            });
                            row.find(".fa-minus").click(function() {
                                self.removeFromQueue($(this).data("index"));
                            });
                            row.find(".fa-chevron-up").click(function() {
                                self.moveUp($(this).data("index"));
                            });
                            row.find(".fa-chevron-down").click(function() {
                                self.moveDown($(this).data("index"));
                            });
                            row.find(".fa-text").focusout(function() {
                                    var ncount= parseInt(this.value);
                                    self.changecount($(this).data("index"),ncount);                                
                            });
                            row.find(".fa-text").keydown(function() {
                                    if (event.keyCode === 13){
                                        blip = true;
                                    }else{blip = false}
                                });
                            row.find(".fa-text").keyup(function() {
                                if (blip){
                                    var ncount= parseInt(this.value);
                                    self.changecount($(this).data("index"),ncount);
                                }
                            });
                            row.find(".fa-text").mouseup(function() {
                                if (blip){
                                    var ncount= parseInt(this.value);
                                    self.changecount($(this).data("index"),ncount);
                                }
                            });
                             $('#queue_list').append(row);
                        }
                       
                        self.loadPrintHistory("full");
                    }else{
                        self.loadPrintHistory("empty");
                    }
                }
							 
								
				
			});
                
		};    
                        
            self.loadPrintHistory = function(items){
                $('#print_history').html("");
                $.ajax({
			url: "plugin/continuousprint/print_history",
			type: "GET",
			dataType: "json",
			headers: {
				"X-Api-Key":UI_API_KEY,
			},
			success:function(r){
				if (r.queue.length > 0) {
					$('#print_history').html("");
					for(var i = 0; i < r.queue.length; i++) {
				            var file=r.queue[i];
				            var row;
				            var time = file.time / 60;
				            var suffix = " mins";
				            if (time > 60) {
				                time = time / 60;
				                suffix = " hours";
				                if (time > 24) {
				                    time = time / 24;
				                    suffix = " days";
				                }
				            }
					    row = $("<div style='padding: 10px; border-bottom: 1px solid #000;background:#c2fccf'>Complete: "+ file.name+ " <div class='pull-right'>took: " + time.toFixed(0) + suffix + "</div></div>")
                    			    $('#print_history').append(row);
                        		}
                    
                                } else if(items=="empty"){
                                    $('#queue_list').html("<div style='text-align: center'>Queue is empty</div>");
                                }
                       }
                   });
            }
            self.reloadQueue = function(data,CMD) {
            	console.log(data,CMD);
                if(CMD=="ADD"){
                    var file = data;
                    var row;
                    var other = "<i style='cursor: pointer' class='fa fa-chevron-down' data-index='"+self.itemsInQueue+"'></i>&nbsp; <i style='cursor: pointer' class='fa fa-chevron-up' data-index='"+self.itemsInQueue+"'></i>&nbsp;";
                    if (self.itemsInQueue == 0) {other = "";$('#queue_list').html("");}
                    if (self.itemsInQueue == 1) {other = "<i style='cursor: pointer' class='fa fa-chevron-down' data-index='"+self.itemsInQueue+"'></i>&nbsp;";}
                    row = $("<div class='n" + self.itemsInQueue + "' style='padding: 10px;border-bottom: 1px solid #000;"+(self.itemsInQueue==0 ? "background: #f9f4c0;" : "")+"'><div class='queue-row-container'><div class='queue-inner-row-container'><input class='fa fa-text count-box' type = 'number' data-index='"+self.itemsInQueue+"' value='" + 1 + "'/><p class='file-name' > " + file.name + "</p></div><div>" + other + "<i style='cursor: pointer' class='fa fa-minus text-error' data-index='"+self.itemsInQueue+"'></i></div></div></div>");
	       
                    row.find(".fa-minus").click(function() {
                        self.removeFromQueue($(this).data("index"));
                    });
                    row.find(".fa-chevron-up").click(function() {
                        self.moveUp($(this).data("index"));
                    });
                    row.find(".fa-chevron-down").click(function() {
                        self.moveDown($(this).data("index"));
                    });
                    row.find(".fa-text").focusout(function() {
                            var ncount = parseInt(this.value);
                            self.changecount($(this).data("index"),ncount);
                    });
                    row.find(".fa-text").keydown(function() {
                                    if (event.keyCode === 13){
                                        blip = true;
                                    }else{blip = false}
                                });
                    row.find(".fa-text").keyup(function() {
                        if (blip){
                            var ncount= parseInt(this.value);
                            self.changecount($(this).data("index"),ncount);
                        }
                    });

                $('#queue_list').append(row);
                    self.itemsInQueue+=1;
                
            }
            if(CMD=="SUB"){
                $("#queue_list").children(".n"+data).remove();
                for(var i=data+1;i<self.itemsInQueue;i++){
                    $("#queue_list").children(".n"+i).children(".queue-row-container").children(".queue-innner-row-container").children(".count-box").attr("data-index",(i-1).toString());
                    $("#queue_list").children(".n"+i).children(".queue-row-container").find(".fa-minus").attr("data-index",(i-1).toString());
                    if(i>1){
                        $("#queue_list").children(".n"+i).children(".queue-row-container").find(".fa-chevron-down").attr("data-index",(i-1).toString());
                        if(i==2){
                            $("#queue_list").children(".n"+i).children(".queue-row-container").find(".fa-chevron-up").remove();
                        }
                        if(i>2){
                            $("#queue_list").children(".n"+i).children(".queue-row-container").find(".fa-chevron-up").attr("data-index",(i-1).toString());
                        }
                    }
                    if(i==1){
                        $("#queue_list").children(".n"+i).css("background","#f9f4c0");
                        $("#queue_list").children(".n"+i).children(".queue-row-container").find(".fa-chevron-down").remove();
                    }else{
                    	$("#queue_list").children(".n"+i).css("background","white");
                    }
                    $("#queue_list").children(".n"+i).addClass("n"+(i-1).toString());
                    $("#queue_list").children(".n"+i).removeClass("n"+i.toString());
                }
                self.itemsInQueue-=1;
                if(self.itemsInQueue==0){
                    $('#queue_list').html("<div style='text-align: center'>Queue is empty</div>");
                }
            }
            if(CMD=="UP"){
                //simple
                //first, we switch the data-indexes of the count-boxes of the rows to be switched
                //then, we copy the html of the count boxes and the html(nothing else) to a temporary variable of the row to be moved
                //We then change the html of the count-box and file name of that row to the file name and count-box of that above it,
                //and change the html of the count-box and file name of to the temporary variable
                var temp3 = $("#queue_list").children(".n"+data).children(".queue-row-container").children(".queue-inner-row-container").children(".count-box").val();
                var temp4 = $("#queue_list").children(".n"+(data-1)).children(".queue-row-container").children(".queue-inner-row-container").children(".count-box").val();
                var temp=$("#queue_list").children(".n"+data).children(".queue-row-container").children(".queue-inner-row-container").children(".file-name").text();
                var temp2=$("#queue_list").children(".n"+(data-1)).children(".queue-row-container").children(".queue-inner-row-container").children(".file-name").text();
                $("#queue_list").children(".n"+data).children(".queue-row-container").children(".queue-inner-row-container").children(".file-name").text(temp2);
                $("#queue_list").children(".n"+(data-1)).children(".queue-row-container").children(".queue-inner-row-container").children(".file-name").text(temp);
                $("#queue_list").children(".n"+data).children(".queue-row-container").children(".queue-inner-row-container").children(".count-box").val(parseInt(temp4));
                $("#queue_list").children(".n"+(data-1)).children(".queue-row-container").children(".queue-inner-row-container").children(".count-box").val(parseInt(temp3));
  
            }
            if(CMD=="DOWN"){
                var temp3 = $("#queue_list").children(".n"+data).children(".queue-row-container").children(".queue-inner-row-container").children(".count-box").val();
                var temp4 = $("#queue_list").children(".n"+(data+1)).children(".queue-row-container").children(".queue-inner-row-container").children(".count-box").val();
                var temp=$("#queue_list").children(".n"+data).children(".queue-row-container").children(".queue-inner-row-container").children(".file-name").text();
                var temp2=$("#queue_list").children(".n"+(data+1)).children(".queue-row-container").children(".queue-inner-row-container").children(".file-name").text();
                $("#queue_list").children(".n"+data).children(".queue-row-container").children(".queue-inner-row-container").children(".file-name").text(temp2);
                $("#queue_list").children(".n"+(data+1)).children(".queue-row-container").children(".queue-inner-row-container").children(".file-name").text(temp); 
                $("#queue_list").children(".n"+data).children(".queue-row-container").children(".queue-inner-row-container").children(".count-box").val(parseInt(temp4));
                $("#queue_list").children(".n"+(data+1)).children(".queue-row-container").children(".queue-inner-row-container").children(".count-box").val(parseInt(temp3));
            }
	}      
		self.checkLooped = function(){
			$.ajax({
					url: "plugin/continuousprint/looped",
					type: "GET",
					dataType: "text",
					headers: {"X-Api-Key":UI_API_KEY},
					success: function(c) {
						if(c=="true"){
							self.is_looped(true);
						} else{
							self.is_looped(false);
						}
					},
			});
        	}
		self.getFileList = function() {
			$('#file_list').html("");
			$.ajax({
				url: "/api/files?recursive=true",
				type: "GET",
				dataType: "json",
				headers: {
					"X-Api-Key":UI_API_KEY,
				},
				success:function(r){
					var filelist = [];
					if (r.files.length > 0) {
						filelist = self.recursiveGetFiles(r.files);
					
						for(var i = 0; i < filelist.length; i++) {
							var file = filelist[i];
							var row = $("<div data-name='"+file.name.toLowerCase()+"' style='padding: 10px;border-bottom: 1px solid #000;'>"+file.path+"<div class='pull-right'><i style='cursor: pointer' class='fa fa-plus text-success' data-name='"+file.name+/*"' data-printarea='"+JSON.stringify(file.gcodeAnalysis.printingArea)+*/"' data-path='"+file.path+"' data-sd='"+(file.origin=="local" ? false : true)+"'></i></div></div>");
							row.find(".fa").click(function() {
								self.addToQueue({
									name: $(this).data("name"),
									path: $(this).data("path"),
									sd: $(this).data("sd"),
                     					count: 1,
                     					//printArea:$(this).data("printarea")
                                    					
								});
								//console.log($(this).data("printarea"))
							});
							
							$('#file_list').append(row);
						}
						
					} else {
						$('#file_list').html("<div style='text-align: center'>No files found</div>");
					}
				}
			});
		}

		$(document).ready(function(){
			self.getFileList();
			self.checkLooped();
			$("#gcode_search").keyup(function() {
				var criteria = this.value.toLowerCase();
				$("#file_list > div").each(function(){
					if ($(this).data("name").indexOf(criteria) == -1) {
						$(this).hide();
					} else {
						$(this).show();
					}
				})
			});
			
			
		});
		
		
		self.recursiveGetFiles = function(files) {
			var filelist = [];
			for(var i = 0; i < files.length; i++) {
				var file = files[i];
				if (file.name.toLowerCase().indexOf(".gco") > -1 || file.name.toLowerCase().indexOf(".gcode") > -1) {
					filelist.push(file);
				} else if (file.children != undefined) {
					console.log("Getting children", self.recursiveGetFiles(file.children))
					filelist = filelist.concat(self.recursiveGetFiles(file.children));
				}
			}
			return filelist;
		}

		self.addToQueue = function(data) {
            		self.reloadQueue(data,"ADD");
            		console.log(data);
			$.ajax({
				url: "plugin/continuousprint/addqueue",
				type: "POST",
				dataType: "text",
				headers: {
					"X-Api-Key":UI_API_KEY,
				},
				data: data,
				success: function(c) {
					
				},
				error: function() {
					self.loadQueue();
				}
			});
		}
		
		self.movePos = function(indexfrom,indexto) {
			console.log("indexfrom="+indexfrom)
			console.log("indexto="+indexto)
			if(indexfrom<indexto){
				for(var i=indexfrom;i<indexto;i++){
					self.reloadQueue(i,"DOWN");
				}
			}else{
				for(var i=indexfrom;i>indexto;i--){
					self.reloadQueue(i,"UP");
				}
			}//good enough

			$.ajax({
				url: "plugin/continuousprint/queuemove?from=" + indexfrom+"&to="+indexto,
				type: "GET",
				dataType: "json",
				headers: {"X-Api-Key":UI_API_KEY},
				success: function(c) {
				},
				error: function() {
					self.loadQueue();
				}
			});
		};
		self.moveUp = function(data) {
            		self.reloadQueue(data,"UP");
			$.ajax({
				url: "plugin/continuousprint/queueup?index=" + data,
				type: "GET",
				dataType: "json",
				headers: {"X-Api-Key":UI_API_KEY},
				success: function(c) {
				},
				error: function() {
					self.loadQueue();
				}
			});
		};
        	self.changecount = function(data,ncount){
            		$.ajax({
				url: "plugin/continuousprint/change?count=" + ncount+"&index="+data,
				type: "GET",
				dataType: "json",
				headers: {"X-Api-Key":UI_API_KEY},
				success: function(c) {
					//self.loadQueue();
				},
				error: function() {
					self.loadQueue();
				}
			});
        	};
		
		self.moveDown = function(data) {
            		self.reloadQueue(data,"DOWN");
			$.ajax({
				url: "plugin/continuousprint/queuedown?index=" + data,
				type: "GET",
				dataType: "json",
				headers: {"X-Api-Key":UI_API_KEY},
				success: function(c) {
				},
				error: function() {
					self.loadQueue();
				}
			});
		};
		
		self.removeFromQueue = function(data) {
            		self.reloadQueue(data,"SUB");
			$.ajax({
				url: "plugin/continuousprint/removequeue?index=" + data,
				type: "DELETE",
				dataType: "text",
				headers: {
					"X-Api-Key":UI_API_KEY,
				},
				success: function(c) {
					//self.loadQueue();
				},
				error: function() {
					self.loadQueue();
				}
			});
		};

		self.startQueue = function() {
			self.is_paused(false);
			$.ajax({
				url: "plugin/continuousprint/startqueue",
				type: "GET",
				dataType: "json",
				headers: {
					"X-Api-Key":UI_API_KEY,
				},
				data: {}
			});
		};
        
        self.loop = function() {
            self.is_looped(true);
			$.ajax({
				url: "plugin/continuousprint/loop",
				type: "GET",
				dataType: "json",
				headers: {
					"X-Api-Key":UI_API_KEY,
				},
				data: {}
			});
		};
        self.unloop = function() {
            self.is_looped(false);
			$.ajax({
				url: "plugin/continuousprint/unloop",
				type: "GET",
				dataType: "json",
				headers: {
					"X-Api-Key":UI_API_KEY,
				},
				data: {}
			});
		};
		
		self.resumeQueue = function() {
			self.is_paused(false)
			$.ajax({
				url: "plugin/continuousprint/resumequeue",
				type: "GET",
				dataType: "json",
				headers: {
					"X-Api-Key":UI_API_KEY,
				},
				data: {}
			});
		};

		self.onDataUpdaterPluginMessage = function(plugin, data) {
			if (plugin != "continuousprint") return;

			var theme = 'info';
			switch(data["type"]) {
				case "popup":
					theme = "info";
					break;
				case "error":
					theme = 'danger';
					self.loadQueue();
					break;
				case "complete":
					theme = 'success';
					self.loadQueue();
					break;
				case "reload":
					theme = 'success'
					self.loadQueue();
					break;
				case "paused":
					self.is_paused(true);
					break;
				case "updatefiles":
					self.getFileList();
					break;
			}
			
			if (data.msg != "") {
				new PNotify({
					title: 'Continuous Print',
					text: data.msg,
					type: theme,
					hide: true,
					buttons: {
						closer: true,
						sticker: false
					}
				});
			}
		};
	
    /*
    #Adapted from OctoPrint-PrusaSlicerThumbnails
    #https://github.com/jneilliii/OctoPrint-PrusaSlicerThumbnails/blob/master/octoprint_prusaslicerthumbnails/static/js/prusaslicerthumbnails.js
    */
    $(document).ready(function(){
			let regex = /<div class="btn-group action-buttons">([\s\S]*)<.div>/mi;
			let template = '<div class="btn btn-mini bold" data-bind="click: function() { if ($root.loginState.isUser()) { $root.addtoqueue($data) } else { return; } }" title="Add To Queue" ><i></i>Q</div>';

			$("#files_template_machinecode").text(function () {
				var return_value = $(this).text();
				return_value = return_value.replace(regex, '<div class="btn-group action-buttons">$1	' + template + '></div>');
				return return_value
			});
		});
	}
    /**/

	// This is how our plugin registers itself with the application, by adding some configuration
	// information to the global variable OCTOPRINT_VIEWMODELS
	OCTOPRINT_VIEWMODELS.push([
		// This is the constructor to call for instantiating the plugin
		ContinuousPrintViewModel,

		// This is a list of dependencies to inject into the plugin, the order which you request
		// here is the order in which the dependencies will be injected into your view model upon
		// instantiation via the parameters argument
		["printerStateViewModel", "loginStateViewModel", "filesViewModel", "settingsViewModel"],

		// Finally, this is the list of selectors for all elements we want this view model to be bound to.
		["#tab_plugin_continuousprint"]
	]);
});
