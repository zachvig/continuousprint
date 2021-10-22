# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask, json

import time
import os

from octoprint.server.util.flask import restricted_access
from octoprint.events import eventManager, Events
from octoprint.access.permissions import Permissions,ADMIN_GROUP,USER_GROUP
class ContinuousprintPlugin(octoprint.plugin.SettingsPlugin,
							octoprint.plugin.TemplatePlugin,
							octoprint.plugin.AssetPlugin,
							octoprint.plugin.StartupPlugin,
							octoprint.plugin.BlueprintPlugin,
							octoprint.plugin.EventHandlerPlugin):
	print_history = []
	enabled = False
	paused = False
	looped = False
	item = None;

	##~~ SettingsPlugin mixin
	def get_settings_defaults(self):
		return dict(
			cp_queue="[]",
			cp_bed_clearing_script="M17 ;enable steppers\nG91 ; Set relative for lift\nG0 Z10 ; lift z by 10\nG90 ;back to absolute positioning\nM190 R25 ; set bed to 25 for cooldown\nG4 S90 ; wait for temp stabalisation\nM190 R30 ;verify temp below threshold\nG0 X200 Y235 ;move to back corner\nG0 X110 Y235 ;move to mid bed aft\nG0 Z1v ;come down to 1MM from bed\nG0 Y0 ;wipe forward\nG0 Y235 ;wipe aft\nG28 ; home",
			cp_queue_finished="M18 ; disable steppers\nM104 T0 S0 ; extruder heater off\nM140 S0 ; heated bed heater off\nM300 S880 P300 ; beep to show its finished",
			cp_looped="false",
			cp_print_history="[]"
			
		)
	
	bed_script=''
	
	##~~ StartupPlugin mixin
	def on_after_startup(self):
		self._logger.info("Continuous Print Plugin started")
		self._settings.save()
	
	
	
	
	##~~ Event hook
	def on_event(self, event, payload):
		try:
			##  Print complete check it was the print in the bottom of the queue and not just any print
			if event == Events.PRINT_DONE:
				if self.enabled == True:
					self.complete_print(payload)

			# On fail stop all prints
			if event == Events.PRINT_FAILED or event == Events.PRINT_CANCELLED:
				if self.enabled == True:
					self.enabled = False # Set enabled to false
					self._plugin_manager.send_plugin_message(self._identifier, dict(type="error", msg="Print queue cancelled"))

			if event == Events.PRINTER_STATE_CHANGED:
				# If the printer is operational and the last print succeeded then we start next print
				state = self._printer.get_state_id()
				if state  == "OPERATIONAL":
					if self.enabled == True and self.paused == False:
						self.start_next_print()

			if event == Events.FILE_SELECTED:
				# Add some code to clear the print at the bottom
				self._logger.info("File selected")
				bed_clearing_script=self._settings.get(["cp_bed_clearing_script"])

			if event == Events.UPDATED_FILES:
				self._plugin_manager.send_plugin_message(self._identifier, dict(type="updatefiles", msg=""))
		except Exception as error:
			raise error
			self._logger.exception("Exception when handling event.")

	def complete_print(self, payload):
		queue = json.loads(self._settings.get(["cp_queue"]))
		LOOPED=self._settings.get(["cp_looped"])
		self.item = queue[0]
		if payload["path"] == self.item["path"] and self.item["count"] > 0:
			
			# check to see if loop count is set. If it is increment times run.
			
			if "times_run" not in self.item:
				self.item["times_run"] = 0
				
			self.item["times_run"] += 1
			
			
			
			# On complete_print, remove the item from the queue 
			# if the item has run for loop count  or no loop count is specified and 
			# if looped is True requeue the item.
			if self.item["times_run"] >= self.item["count"]:
				self.item["times_run"] = 0
				queue.pop(0)
				if LOOPED=="false":
					self.looped=False
				if LOOPED=="true":
					self.looped=True
				if self.looped==True and self.item!=None:
					queue.append(self.item)
					
			self._settings.set(["cp_queue"], json.dumps(queue))
			self._settings.save()
			
			#Add to the print History
		
			print_history = json.loads(self._settings.get(["cp_print_history"]))
			#	#calculate time
			#	time=payload["time"]/60;
			#	suffix="mins"
			#	if time>60:
			#		time = time/60
			#		suffix = "hours"
			#		if time>24:
			#			time= time/24
			#			suffix= "days"
			#	#Add to the print History
			#	inPrintHistory=False
			#	if len(print_history)==1 and item["path"]==print_history[0]["path"]:
			#		print_history[0]=dict(
			#			path = payload["path"],
			#			name = payload["name"],
			#			time = (print_history[0]["time"]+payload["time"])/(print_history[0]["times_run"]+1),
			#			times_run =  print_history[0]["times_run"]+1,
			#			title = print_history[0]["title"]+" "+print_history[i]["times_run"]+". " + str(int(time))+suffix
			#		)
			#		inPrintHistory=True
			#	if len(print_history)>1:
			#		for i in range(0,len(print_history)-1):
			#			if item["path"]==print_history[i]["path"] and InPrintHistory != True:
			#				print_history[i]=dict(
			#					path = payload["path"],
			#					name = payload["name"],
			#					time = (print_history[i]["time"]+payload["time"])/(print_history[i]["times_run"]+1),
			#					times_run =  print_history[i]["times_run"]+1,
			#					title = print_history[i]["title"]+" "+print_history[i]["times_run"]+". " + str(int(time))+suffix
			#				)
			#				inPrintHistory=True
			#	if inPrintHistory == False:
			#		print_history.append(dict(
			#			path = payload["path"],
			#			name = payload["name"],
			#			time = payload["time"],
			#			times_run =  item["times_run"],
			#			title="Print Times: 1. "+str(int(time))+suffix
			#		))
			#		
			print_history.append(dict(
					name = payload["name"],
					time = payload["time"]
				))	

			#save print history
			self._settings.set(["cp_print_history"], json.dumps(print_history))
			self._settings.save()

			# Clear down the bed
			if len(queue)>0:
				self.clear_bed()

			# Tell the UI to reload
			self._plugin_manager.send_plugin_message(self._identifier, dict(type="reload", msg=""))
		else:
			enabled = False
			

	def parse_gcode(self, input_script):
		script = []
		for x in input_script:
			if x.find("[PAUSE]", 0) > -1:
				self.paused = True
				self._plugin_manager.send_plugin_message(self._identifier, dict(type="paused", msg="Queue paused"))
			else:
				script.append(x)
		return script
	
		
	

	def clear_bed(self):
		self._logger.info("Clearing bed")
		bed_clearing_script=self.bed_script.split("\n")	
		self._printer.commands(self.parse_gcode(bed_clearing_script),force=True)
		
	def complete_queue(self):
		self.enabled = False # Set enabled to false
		self._plugin_manager.send_plugin_message(self._identifier, dict(type="complete", msg="Print Queue Complete"))
		queue_finished_script = self._settings.get(["cp_queue_finished"]).split("\n")
		self._printer.commands(self.parse_gcode(queue_finished_script),force=True)#send queue finished script to the printer
		
		

	def start_next_print(self):
		if self.enabled == True and self.paused == False:
			queue = json.loads(self._settings.get(["cp_queue"]))
			
			if len(queue) > 0:
				self._plugin_manager.send_plugin_message(self._identifier, dict(type="popup", msg="Starting print: " + queue[0]["name"]))
				self._plugin_manager.send_plugin_message(self._identifier, dict(type="reload", msg=""))

				sd = False
				if queue[0]["sd"] == "true":
					sd = True
				try:
					self._printer.select_file(queue[0]["path"], sd)
					self._logger.info(queue[0]["path"])
					self._printer.start_print()
					self.update_bed_script(queue[0])
					self._logger.debug(self.bed_script)
				except InvalidFileLocation:
					self._plugin_manager.send_plugin_message(self._identifier, dict(type="popup", msg="ERROR file not found"))
				except InvalidFileType:
					self._plugin_manager.send_plugin_message(self._identifier, dict(type="popup", msg="ERROR file not gcode"))
			else:
				self.complete_queue()
	def update_bed_script(self, file):
		self.bed_script=self._settings.get(["cp_bed_clearing_script"])
		#possible values:
		#[MIN_X]
		#[MIN_X@Z<a]
		#[MIN_X@Z>a]
		#[MIN_X@a<Z<b]
		# a and b are z height in mm. MIN_X is the minumum x position in that range
		# 
		#[MIN_X]
		#[MIN_Y]
		#[MIN_Z]
		#[MAX_X]
		#[MAX_Y]
		#[MAX_Z]
		#[PAUSE] is used later on
		i=0
		args=[]
		while i<len(self.bed_script):
			out=''
			if self.bed_script[i]=='[':
				i+=1
				# start end str lower upper value
				args.append([i-1,0,'',None,None,None])
				while self.bed_script[i]!=']':
					args[-1][2]+=self.bed_script[i]
					i+=1
				if args[-1]=='PAUSE':
					args.pop(-1)
				else:
					args[-1][1]=i
					if '@' in args[-1][2]:
						range=args[-1][2].split('@')[1].upper()
						args[-1][2]=args[-1][2].split('@')[0].upper()
						if range.startswith('Z'):
							if '>' in range:
								args[-1][3]=float(range.split('>')[1])
							if '<' in range:
								args[-1][4]=float(range.split('<')[1])
						else:
							args[-1][3]=float(range.split('<')[0])
							args[-1][4]=float(range.split('<')[2])
					
			i+=1
		if len(args)>0:#so this is only run when args are in the script.
			self._logger.debug('processing '+file['path']+', args are '+str(args))
			start=time.time()#to test speeds
			gcode=open(os.path.expanduser('~/.octoprint/uploads/')+file['path'],'r').read().split('\n')
			Z=0
			i=0
			#remove comment only lines
			while i<len(gcode):
				x=0
				while gcode[i]=='':
					gcode.pop(i)
					if i>=len(gcode):
						break
				if i<len(gcode):
					while gcode[i][x]==' 'or gcode[i][x]=='\t':
						x+=1
						if x>=len(gcode[i]):
							x-=1
							break
					if gcode[i][x:].startswith(';'):
						gcode.pop(i)
					i+=1
			#remove last layer (if the last layer is incredibly larger than the one before it, it will fall and not take up quite so much space) Also on the last Layer the extruder often moves to some point and does not print. These two things mean that it must be removed.
			i=len(gcode)-1
			g=gcode[i].upper()
			t=0
			while g[t]==' 'or g[t]=='\t':
				t+=1
			while 'Z' not in g or (not g[t:].startswith('G1') and not g[t:].startswith('G1') ):
				gcode.pop(i)
				i-=1
				g=gcode[i].upper()
				t=0
				while g[t]==' 'or g[t]=='\t':
					t+=1
			del g
			del t
			del i
			for line in gcode:
				c=0
				line=line.upper()
				while c<len(line):
					x=None
					y=None
					if line[c]=='G':
						c+=1
						if c>=len(line):
							break
						if line[c]=='0'or line[c]=='1':
							if 'Z' in line.split(';')[0]:
								Z=line.split(';')[0].split('Z')[1].split(' ')[0]
								if Z!='':
									Z=float(Z)
							if 'X' in line.split(';')[0]:
								x=line.split(';')[0].split('X')[1].split(' ')[0]
								if x!='':
									x=float(x)
							if 'Y' in line.split(';')[0]:
								y=line.split(';')[0].split('Y')[1].split(' ')[0]
								if y!='':
									y=float(y)
					i=0
					while i<len(args):
						if args[i][2]=='MIN_X':
							if x:
								if args[i][3] and args[i][4]:
									if args[i][3]<Z<args[i][4]:
										if not args[i][5]or args[i][5]>x:
											args[i][5]=x
								elif args[i][3]:
									if args[i][3]<Z:
										if not args[i][5]or args[i][5]>x:
											args[i][5]=x
								elif args[i][4]:
									if Z<args[i][4]:
										if not args[i][5]or args[i][5]>x:
											args[i][5]=x
								else:
										if not args[i][5]or args[i][5]>x:
											args[i][5]=x
						elif args[i][2]=='MIN_Y':
							if y:
								if args[i][3] and args[i][4]:
									if args[i][3]<Z<args[i][4]:
										if not args[i][5]or args[i][5]>y:
											args[i][5]=y
								elif args[i][3]:
									if args[i][3]<Z:
										if not args[i][5]or args[i][5]>y:
											args[i][5]=y
								elif args[i][4]:
									if Z<args[i][4]:
										if not args[i][5]or args[i][5]>x:
											args[i][5]=y
								else:
										if not args[i][5]or args[i][5]>x:
											args[i][5]=y
						elif args[i][2]=='MIN_Z':
							if args[i][3] and args[i][4]:
								if args[i][3]<Z<args[i][4]:
									if not args[i][5]or args[i][5]>Z:
										args[i][5]=Z
							elif args[i][3]:
								if args[i][3]<Z:
									if not args[i][5]or args[i][5]>Z:
										args[i][5]=Z
							elif args[i][4]:
								if Z<args[i][4]:
									if not args[i][5]or args[i][5]>Z:
										args[i][5]=Z
							else:
									if not args[i][5]or args[i][5]>Z:
										args[i][5]=Z
						elif args[i][2]=='MAX_X':
							if x:
								if args[i][3] and args[i][4]:
									if args[i][3]<Z<args[i][4]:
										if not args[i][5]or args[i][5]<x:
											args[i][5]=x
								elif args[i][3]:
									if args[i][3]<Z:
										if not args[i][5]or args[i][5]<x:
											args[i][5]=x
								elif args[i][4]:
									if Z<args[i][4]:
										if not args[i][5]or args[i][5]<x:
											args[i][5]=x
								else:
										if not args[i][5]or args[i][5]<x:
											args[i][5]=x
						elif args[i][2]=='MAX_Y':
							if y:
								if args[i][3] and args[i][4]:
									if args[i][3]<Z<args[i][4]:
										if not args[i][5]or args[i][5]<y:
											args[i][5]=y
								elif args[i][3]:
									if args[i][3]<Z:
										if not args[i][5]or args[i][5]<y:
											args[i][5]=y
								elif args[i][4]:
									if Z<args[i][4]:
										if not args[i][5]or args[i][5]<y:
											args[i][5]=y
								else:
										if not args[i][5]or args[i][5]<y:
											args[i][5]=y
						elif args[i][2]=='MAX_Z':
							if args[i][3] and args[i][4]:
								if args[i][3]<Z<args[i][4]:
									if not args[i][5]or args[i][5]<Z:
										args[i][5]=Z
							elif args[i][3]:
								if args[i][3]<Z:
									if not args[i][5]or args[i][5]<Z:
										args[i][5]=Z
							elif args[i][4]:
								if Z<args[i][4]:
									if not args[i][5]or args[i][5]<Z:
										args[i][5]=Z
							else:
									if not args[i][5]or args[i][5]<Z:
										args[i][5]=Z
						i+=1
					c+=1
			del Z
			del gcode
			i=0
			ls=list(self.bed_script)
			Del=0#difference in number of characters
			while i<len(args):
				# start end str lower upper value
				s=args[i][0]-Del
				while s<=args[i][1]-Del:
					ls.pop(s)
					Del+=1#increase number of deleted characters
				ls.insert(s,str(args[i][5]))#add value of variable to gcode
				Del-=len(str(args[i][5]))#characters have been added
				i+=1
				ls=list(''.join(ls))
			self.bed_script=''.join(ls)
			self._logger.debug('processed bed_script: '+self.bed_script)
				
					
			end=time.time()
			self._logger.info('Processed bed script, time to process: '+str(end-start))
					
		
		#'~/.octoprint/uploads/'
	##~~ APIs
	@octoprint.plugin.BlueprintPlugin.route("/looped", methods=["GET"])
	@restricted_access
	def looped(self):
		loop2=self._settings.get(["cp_looped"])
		return loop2
		
	@octoprint.plugin.BlueprintPlugin.route("/loop", methods=["GET"])
	@restricted_access
	def loop(self):
		if not Permissions.PLUGIN_CONTINUOUSPRINT_LOOP.can():
			return flask.make_response("insufficient rights to loop", 403)
		self.looped=True
		self._settings.set(["cp_looped"], "true")
		return flask.make_response("success", 200)
		
		
	@octoprint.plugin.BlueprintPlugin.route("/unloop", methods=["GET"])
	@restricted_access
	def unloop(self):
		if not Permissions.PLUGIN_CONTINUOUSPRINT_LOOP.can():
			return flask.make_response("insufficient rights to unloop", 403)
		self.looped=False
		self._settings.set(["cp_looped"], "false")
		return flask.make_response("success", 200)
		
	@octoprint.plugin.BlueprintPlugin.route("/queue", methods=["GET"])
	@restricted_access
	def get_queue(self):
		#this is getting to be quite redundant. Turning an array of jsons into a dictionary just so flask can turn it into a json of an array of jsons.
		#return flask.jsonify(queue=json.loads(self._settings.get(["cp_queue"])))
		return '{"queue":' + self._settings.get(["cp_queue"]) + "}"
	
	@octoprint.plugin.BlueprintPlugin.route("/print_history", methods=["GET"])
	@restricted_access
	def get_print_history(self):
		#return flask.jsonify(queue=json.loads(self._settings.get(["cp_print_history"])))
		return'{"queue":' + self._settings.get(["cp_print_history"]) + "}"
	
	@octoprint.plugin.BlueprintPlugin.route("/queueup", methods=["GET"])
	@restricted_access
	def queue_up(self):
		if not Permissions.PLUGIN_CONTINUOUSPRINT_CHQUEUE.can():
			return flask.make_response("insufficient rights", 403)
		index = int(flask.request.args.get("index", 0))
		queue = json.loads(self._settings.get(["cp_queue"]))
		orig = queue[index]
		queue[index] = queue[index-1]
		queue[index-1] = orig	
		self._settings.set(["cp_queue"], json.dumps(queue))
		self._settings.save()
		return flask.jsonify(queue=queue)
	
	@octoprint.plugin.BlueprintPlugin.route("/change", methods=["GET"])
	@restricted_access
	def change(self):
		if not Permissions.PLUGIN_CONTINUOUSPRINT_CHQUEUE.can():
			return flask.make_response("insufficient rights", 403)
		index = int(flask.request.args.get("index")) 
		count = int(flask.request.args.get("count"))
		queue = json.loads(self._settings.get(["cp_queue"]))
		queue[index]["count"]=count
		self._settings.set(["cp_queue"], json.dumps(queue))
		self._settings.save()
		return flask.jsonify(queue=queue)
	
	@octoprint.plugin.BlueprintPlugin.route("/queuemove", methods=["GET"])
	@restricted_access
	def queue_move(self):
		if not Permissions.PLUGIN_CONTINUOUSPRINT_CHQUEUE.can():
			return flask.make_response("insufficient rights", 403)
		To = int(flask.request.args.get("to", 0))
		From = int(flask.request.args.get("from", 0))
		self._logger.debug("Index"+str(To)+str(From))
		queue = json.loads(self._settings.get(["cp_queue"]))
		orig = queue[From]
		queue.pop(From)
		queue.insert(To,orig)
		self._settings.set(["cp_queue"], json.dumps(queue))
		self._settings.save()		
		return flask.jsonify(queue=queue)
		
	@octoprint.plugin.BlueprintPlugin.route("/queuedown", methods=["GET"])
	@restricted_access
	def queue_down(self):
		if not Permissions.PLUGIN_CONTINUOUSPRINT_CHQUEUE.can():
			return flask.make_response("insufficient rights", 403)
		index = int(flask.request.args.get("index", 0))
		queue = json.loads(self._settings.get(["cp_queue"]))
		orig = queue[index]
		queue[index] = queue[index+1]
		queue[index+1] = orig	
		self._settings.set(["cp_queue"], json.dumps(queue))
		self._settings.save()		
		return flask.jsonify(queue=queue)
		
			
	@octoprint.plugin.BlueprintPlugin.route("/addqueue", methods=["POST"])
	@restricted_access
	def add_queue(self):
		if not Permissions.PLUGIN_CONTINUOUSPRINT_ADDQUEUE.can():
			return flask.make_response("insufficient rights", 403)
		queue = json.loads(self._settings.get(["cp_queue"]))
		try:
			self._logger.debug(flask.request.form)
			queue.append(dict(
				name=flask.request.form["name"],
				path=flask.request.form["path"],
				sd=flask.request.form["sd"],
				count=int(flask.request.form["count"]),
				#printArea=dict(
				#	maxX=flask.request.form["printArea[maxX]"],
				#	maxY=flask.request.form["printArea[maxY]"],
				#	maxZ=flask.request.form["printArea[maxZ]"],
				#	minX=flask.request.form["printArea[minX]"],
				#	minY=flask.request.form["printArea[minY]"],
				#	minZ=flask.request.form["printArea[minZ]"],
				#)
			))
		except:
			self._logger.debug('error')
			return flask.make_response("error", 400)
		self._settings.set(["cp_queue"], json.dumps(queue))
		self._settings.save()
		return flask.make_response("success", 200)
	
	@octoprint.plugin.BlueprintPlugin.route("/removequeue", methods=["DELETE"])
	@restricted_access
	def remove_queue(self):
		if not Permissions.PLUGIN_CONTINUOUSPRINT_RMQUEUE.can():
			return flask.make_response("insufficient rights", 403)
		queue = json.loads(self._settings.get(["cp_queue"]))
		self._logger.info(flask.request.args.get("index", 0))
		queue.pop(int(flask.request.args.get("index", 0)))
		self._settings.set(["cp_queue"], json.dumps(queue))
		self._settings.save()
		return flask.make_response("success", 200)
	
	@octoprint.plugin.BlueprintPlugin.route("/startqueue", methods=["GET"])
	@restricted_access
	def start_queue(self):
		if not Permissions.PLUGIN_CONTINUOUSPRINT_STARTQUEUE.can():
			return flask.make_response("insufficient rights to start queue", 403)
		self._settings.set(["cp_print_history"], "[]")#Clear Print History
		self._settings.save()
		self.paused = False
		self.enabled = True # Set enabled to true
		self.start_next_print()
		return flask.make_response("success", 200)
	
	@octoprint.plugin.BlueprintPlugin.route("/resumequeue", methods=["GET"])
	@restricted_access
	def resume_queue(self):
		if self.paused == True: # add same logic, only run if paused, otherwise it'll call "self.start_next_print()" even if currently printing...
			self.paused = False
			self.start_next_print()
			return flask.make_response("success", 200)
	
    # Listen for resume from printer ("M118 //action:queuego"), only act if actually paused.
	def resume_action_handler(self, comm, line, action, *args, **kwargs):
		if not action == "queuego":
			return
		if self.paused == True:
			self.paused = False
			self.start_next_print()

	##~~  TemplatePlugin
	def get_template_vars(self):
		return dict(
			cp_enabled=self.enabled,
			cp_bed_clearing_script=self._settings.get(["cp_bed_clearing_script"]),
			cp_queue_finished=self._settings.get(["cp_queue_finished"]),
			cp_paused=self.paused
		)
	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False, template="continuousprint_settings.jinja2"),
			dict(type="tab", custom_bindings=False, template="continuousprint_tab.jinja2")
		]

	##~~ AssetPlugin
	def get_assets(self):
		return dict(
			js=["js/continuousprint.js"],
			css=["css/continuousprint.css"]
		)


	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			continuousprint=dict(
				displayName="Continuous Print Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="Zinc-OS",
				repo="continuousprint",
				current=self._plugin_version,
				stable_branch=dict(
				    name="Stable", branch="master", comittish=["master"]
				),
				prerelease_branches=[
				    dict(
					name="Release Candidate",
					branch="rc",
					comittish=["rc", "master"],
				    )
				],
                              # update method: pip
				pip="https://github.com/Zinc-OS/continuousprint/archive/{target_version}.zip"
			)
		)
	def add_permissions(*args, **kwargs):
		return [
			dict(key="STARTQUEUE",
			     name="Start Queue",
			     description="Allows for starting queue",
			     roles=["admin","continuousprint"],
			     dangerous=False,
			     default_groups=[ADMIN_GROUP]),
			dict(key="ADDQUEUE",
			     name="Add to Queue",
			     description="Allows for adding prints to the queue",
			     roles=["admin","continuousprint"],
			     dangerous=False,
			     default_groups=[USER_GROUP]),
			dict(key="RMQUEUE",
			     name="Remove Print from Queue ",
			     description="Allows for removing prints from the queue",
			     roles=["admin","continuousprint"],
			     dangerous=False,
			     default_groups=[USER_GROUP]),
			dict(key="LOOP",
			     name="Loop Queue ",
			     description="Allows for looping the queue",
			     roles=["admin","continuousprint"],
			     dangerous=False,
			     default_groups=[ADMIN_GROUP]),
			dict(key="CHQUEUE",
			     name="Move items in Queue ",
			     description="Allows for moving items in the queue",
			     roles=["admin","continuousprint"],
			     dangerous=False,
			     default_groups=[USER_GROUP]),
		]
		


__plugin_name__ = "Continuous Print"
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = ContinuousprintPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
		"octoprint.comm.protocol.action": __plugin_implementation__.resume_action_handler, # register to listen for "M118 //action:" commands
		"octoprint.access.permissions": __plugin_implementation__.add_permissions
	}

