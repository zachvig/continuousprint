# Continuous Print Queue Plugin

Octoprint plugin that allows users to generate a print queue, specify a print bed clearning script and run the queue which will print-clear-print until the end of the queue.

## Setup

Install manually using this URL:

    https://github.com/zachvig/continuousprint/archive/master.zip



## Configuration

Make sure you have a method of clearning the bed automatically and have set the print bed clearing script or you'll end up messing the first print.

## Print Count

The number of times a gcode will be printed can be specified in an input box.
When the queue is looped, this number will be equal to the relative quantities of each print.
When the queue is not looped, this number will be equal to the number of times each gcode is printed. 
