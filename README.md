# sps-simulator
## Table of contents
* [General info](#general-info)
* [Versions](#versions)
* [Setup](#setup)
* [Referencing](#referencing)
* [License](#license)

## General info
This project aims to help low-power circuit and system designers analyze the relationships between system power consumption and application-relevant design/operating knobs. The modeling framework uses a hierarchical description of a complex system, the relevant power consuming behaviors and variables of all components, and various functions to perform analyses and generate figures to inform the user. The target audience of this system modeling framework are those designing custom integrated circuits and power-sensitive self-powered systems. However, this tool should also be useful to embedded system designers who are power-conscious of their designs.

This project is developed at the University of Virginia, primarily by the RLP-VLSI research group. It has been funded by the UVA Strategic Investment Fund (SIF128 Smart Infrastructure). Our research webpage can be found [here](https://rlpvlsi.ece.virginia.edu/).

## Versions
This project is currently compatible with:
* python 3.8.3
* numpy 1.19.0
* plotly 4.8.2
	
## Getting Started
Please view the wiki for more details on this project. The example code "Example_System.py" is ready-to-go, so once you've installed the proper libraries as listed
then that file should run and many browser windows will begin popping up. Some information will also stream through the terminal. When using Anaconda, a few extra commands may be necessary to set the default plotting mechanism to your browser. These are provided in this example script.

## Referencing
If and when using this project in papers, reports, or in any published setting, please cite this repository.

## License
TBD