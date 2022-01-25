# Continuous Print Queue Plugin

Octoprint plugin that allows users to generate a print queue, specify a print bed clearning script and run the queue which will print-clear-print until the end of the queue.
This version has been rolled back to Zinc-OS's 1.2.3a, which uses an older API and allows the [pause] command between prints.

## Setup

Install manually using this URL:

    https://github.com/zachvig/continuousprint/archive/master.zip



## Configuration

Make sure you have a method of clearning the bed automatically and have set the print bed clearing script or you'll end up messing the first print.

## Print Count

The number of times a gcode will be printed can be specified in an input box.
When the queue is looped, this number will be equal to the relative quantities of each print.
When the queue is not looped, this number will be equal to the number of times each gcode is printed. 

## Origins

This plugin is pretty much essentially the one from Zinc-OS, with the update information stripped from it.  All credit here:
https://github.com/Zinc-OS/continuousprint
