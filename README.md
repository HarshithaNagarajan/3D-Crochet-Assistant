# 3D Crochet Assistant: Automated Amigurumi Pattern Designer


## Overview

This repository contains all the code developed for my master's thesis, submitted in part completion of the _**MSc in Computer Graphics, Vision and Imaging Program**_ at University College London.


## Project Abstract
Crocheting is a widely practiced craft where designers invest significant time in creating intricate crochet instructions or patterns for releasing commercial products. Many enthusiasts, however, lack the expertise to generate their own patterns and must rely on pre-made designs, limiting creative expression. Addressing this issue, we propose a novel computational method for generating crochet patterns directly from 3D model inputs, automating and streamlining the design process. This approach caters to both experienced designers seeking efficiency and hobbyists passionate about crafting original designs but lacking pattern-drafting skills.

By inputting a 3D model of the desired object, our algorithm converts the digital shape into a detailed crochet pattern by computing point-to-point distances to identify key structural features related to the curvature of the shape. Dynamic programming is then employed to map stitch connections based on crochet techniques, ensuring that the generated pattern accurately represents the input geometry. The resulting instructions guide users in creating a three-dimensional object that closely mirrors the original model.


## Repository Structure
------------
                        
    ├── Blender and JSON Files             <- contains the .blend used for slicing and .json files obtained as the output
    |    ├── cactus              
    |         ├── cactus_main                
    |         ├── cactus_left
    |         ├── cactus_right
    |    ├── worm             
    ├── Output                             <- Crochet Pattern outputs generated for the worm and cactus from the algorithm, for a quick preview
    |    ├── crochet_pattern_cactus.txt                         
    |    ├── crochet_pattern_worm.txt                           
    ├── Pattern Synthesis                  <- MAIN: Code that produces the crochet instructions
    |    ├── blender                           
    |         ├── slice_resample_store.py  <- Blender script using Python API that slices a 3D mesh, resamples and stores vertices
    |    ├── src                           <- Python scripts to analyse the vertices, extract shape information in line with crochet techniques and output pattern
    |         ├── dp.py
    |         ├── main.py
    |         ├── utils.py
    |         ├── write_pattern.py
    ├── LICENSE                            
    ├── README.md   
    ├── requirements.txt                   <- The requirements file for reproducing the analysis environment.
--------
