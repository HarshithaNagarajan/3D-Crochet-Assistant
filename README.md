# 3D Crochet Assistant: Automated Amigurumi Pattern Designer


## Overview

This repository contains all the code developed for my master's thesis, submitted in part completion of the MSc in Computer Graphics, Vision and Imaging Program at University College London.


## Project Abstract
Crocheting is a widely practiced craft where designers invest significant time in creating intricate crochet instructions or patterns for releasing commercial products. Many enthusiasts, however, lack the expertise to generate their own patterns and must rely on pre-made designs, limiting creative expression. Addressing this issue, we propose a novel computational method for generating crochet patterns directly from 3D model inputs, automating and streamlining the design process. This approach caters to both experienced designers seeking efficiency and hobbyists passionate about crafting original designs but lacking pattern-drafting skills.

By inputting a 3D model of the desired object, our algorithm converts the digital shape into a detailed crochet pattern by computing point-to-point distances to identify key structural features related to the curvature of the shape. Dynamic programming is then employed to map stitch connections based on crochet techniques, ensuring that the generated pattern accurately represents the input geometry. The resulting instructions guide users in creating a three-dimensional object that closely mirrors the original model.


## Repository Structure
------------

    ├── LICENSE                            
    ├── README.md                           
    ├── data_collection                     <- Overview and code involved in data collection
    |    ├── chromedriver_win32             <- Chromedriver installation for dynamic scraping
    |         ├── chromedriver.exe
    |    ├── data_collection                <- All about data collection methodology employed
    |         ├── README.md                 <- Explanantion of differesent data assets collected
    |         ├── PPL
    |         ├── intermediate
    |         ├── processed
    |         ├── labelled
    |         ├── notebooks_for_cleaning
    |    ├── scraping
    ├── data_analysis                       <- Code to analyse collected data
    |    ├── src                            <- Helper functions used
    |    ├── notebooks                      <- Jupyter notebooks and R markdown notebooks with data analysis
    |    ├── data_labeling                  <- Code for the data labelling software created in Streamlit
    ├── data_program_selector_development   <- Code for the Data PRogram Selector tool deployed on Streamlit
    ├── reports
    |   ├── Dissertation.pdf              <- Final copy of Dissertation submitted for degree 
    ├── .gitignore                        <- Files that need not be pushed to git
    ├── dse_logo.png                      <- PNG logo for project
    ├── requirements.txt                  <- The requirements file for reproducing the analysis environment.
    ├── setup.sh                          <- Bash script to install all dependencies for reproducing the project
--------
